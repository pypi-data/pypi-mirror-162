from __future__ import annotations

import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.base import BaseEstimator

from .bokeh_app import run_server
from .gtm_base import GTMBase


class GTMTimeSeries(GTMBase, BaseEstimator):
    """GTM model for time series or sequential data """

    def __init__(self, s=2, group_size=5, l=0.01,
                 map_shape: tuple = (10, 10), rbf_shape: tuple = (4, 4)):
        """
        Initialize the hyper parameters of GTMTT model

        Note here: the n_obs is not meant to be fixed in this step. n_obs is only used to split the input data
                    into separate sequences. If you want to train the model with different size of training data,
                    modify this directly by calling .n_bos = *correct_num_of_observations*
        Parameters
        ----------
        s: variance factor for gaussian basis functions
        group_size: grouping the latent space points. Allow transfer into groups then proceed to a single hidden state.
        l: regulatory parameter.
        map_shape: the size of mixture components. Default (10, 10) which means a 10x10 grid is used.
        rbf_shape: the size of basis functions.
        """
        # check group parameter value (map grid should be able to be divided into groups)
        if map_shape is None:
            map_shape = [10, 10]
        if map_shape[0] % group_size != 0:
            raise ValueError(f" {map_shape} map grid can not be divided into groups with length {group_size} ")
        # init GTM base model (flatten the first dimension of data)
        super().__init__(s, l, map_shape=map_shape, rbf_shape=rbf_shape)

        self.s = s

        # emission prob
        self.B = None

        # data metrics init to None
        self.d = None
        self.seq_length = None

        # data in (num_series, length, dimension) and (obs*length, d )form
        self.data_series = None
        self.T = None

        # prior probs (Pi) (randomly initialized)
        self.priors = np.random.random_sample([self.K])
        self.priors = self.priors / self.priors.sum()

        self.group_size = group_size

        # Init transition probs p_ij  (state i -> state j)
        self.P: np.ndarray = np.random.random_sample([self.K, self.K])
        self.P /= self.P.sum(axis=1)[:, None]  # row divided by sum of row

        # Grouping latent space
        # C indicator where C_ij = 1 if state i in group j
        num_group = self.K // (group_size ** 2)
        state_belonging = np.zeros(map_shape)
        cur_group = 0
        for i in range(self.k // group_size):
            for j in range(self.k // group_size):
                state_belonging[i * group_size:(i + 1) * group_size:, j * group_size:(j + 1) * group_size] = cur_group
                cur_group += 1
        self.C = np.zeros([self.K, num_group])
        # C_ij = 1 if state i in group j
        for g in range(num_group):
            self.C[:, g] = (state_belonging.flatten() == g)
        #  as equation (6) in GTMTT
        self.CC = np.zeros([num_group, self.K])
        for g in range(num_group):
            self.CC[g, :] = (state_belonging.flatten().T == g) / (state_belonging.flatten() == g).sum(axis=0)
        # init eta (eta_ik: prob that trans from state i to a state in group k)
        self.eta = self.P.dot(self.C)

        # M-step vars init
        self.gammas = []  # collect gammas over different sequence
        # xi.shape = (self.K, self.K)
        self.xi = None
        # intermediates
        self.G: np.ndarray = np.zeros([self.K, self.K])
        # col wise sum of gamma across t
        # since the phi doesn't change with t, we can perform a single M-step at the end of time
        # using accumulative vars
        self.gamma_sum = np.zeros(self.K)
        self.Pi_sum = np.zeros(self.K)

        # responsibility dot single_time_series (accumulative)
        self.RT = None

        # col wise sum of alpha before normalization (accumulative)
        self.Scale = None

        # in-real-time vis attrs
        self.latent_coors = {"x": [], 'y': []}
        self.llh_coors = {'x': [], 'y': []}

        # training history
        self.llhs = []

    def start_vis_server(self):
        """
        If called before training, a browser will be started and a sample of time series
        projected into latent space will be displayed on that page.

        """
        # run data host server
        from flask import Flask
        from flask_cors import CORS
        from threading import Thread
        import logging
        log = logging.getLogger('werkzeug')
        log.disabled = True

        app = Flask(__name__)
        CORS(app)

        @app.route("/latent_space")
        def latent():
            return self.latent_coors

        @app.route("/llh")
        def llh():
            return self.llh_coors

        t = Thread(target=app.run, kwargs={"port": 5000})
        t.setDaemon(True)
        t.start()

        # start the bokeh server
        run_server()

    def forward(self, obs: np.ndarray) -> [np.ndarray, np.ndarray]:
        """
        Generate alpha_T(N)
        obs is a single time-series in shape of (length, dimension)
        """
        # check input shape
        seq_length = obs.shape[0]
        d = obs.shape[1]
        if self.seq_length != seq_length or d != self.d:
            raise ValueError(f"Invalid sequence input of shape {seq_length.shape}, expecting {self.seq_length}")

        # seq_length = num time steps
        alpha = np.zeros([seq_length, self.K])

        scale = np.zeros(seq_length)
        # alpha_1(i) = Pi_i * b_i(O_1)
        alpha[0] = self.priors * self.B[0]
        scale[0] = alpha[0].sum()
        alpha[0] /= scale[0]  # normalize
        # induction
        for t in range(1, self.seq_length):
            # alpha * Pij * C_ik * B
            alpha[t] = alpha[t - 1].dot(self.eta).dot(self.CC) * self.B[t]
            # alpha[t] = alpha[t-1].dot(self.P) * self.B[t]
            scale[t] = alpha[t].sum()  # set scale before normalize alpha
            alpha[t] /= alpha[t].sum()  # normalize

        return alpha, scale

    def backward(self, scale):
        # beta.shape = (seq_length, K)
        beta = np.zeros([self.seq_length, self.K])

        beta[self.seq_length - 1:, ] = 1 / scale[self.seq_length - 1]
        for t in range(self.seq_length - 2, -1, -1):
            beta[t] = (beta[t + 1] * self.B[t + 1]).dot(self.CC.T).dot(self.eta.T) / scale[t]
        return beta

    def calc_gamma(self, forward_alpha, backward_beta) -> np.ndarray:
        """
        gamma_t(i) = P(q_t = S_i | O, lambda)      : shape = (T*K)
        the probability of being in state S_i in time t, given observe seq O and the model lambda
        """
        # gamma: (length*K)  T(length*d)
        gamma = forward_alpha * backward_beta
        # normalize to probability
        gamma /= gamma.sum(axis=1)[:, None]
        return gamma

    def calc_xi(self, forward_alpha, backward_beta):
        """
        Xi_t(i, j): the prob that being in state i at time t and state j at time t+1
        """
        # this is accumulative xi.
        self.xi += self.P * \
                   forward_alpha[0:self.seq_length - 2].T. \
                       dot(
                       backward_beta[1:self.seq_length - 1] * self.B[1:self.seq_length - 1]
                   )

    def m_step(self) -> bool:
        """
        To update the GTM model parameters which is constant across time steps.

        M-step should be called after all time series have been evaluated.
        """

        # gamma = responsibilities
        # G = col wise sum of gamma
        self.G = np.diag(self.gamma_sum)

        # update W using equation (11) from GTMTT 1998
        for l in [self.l, self.l * 10, self.l * 100]:
            A = self.phi_with_ones.T @ self.G @ self.phi_with_ones + \
                l * np.identity(self.phi_with_ones.shape[1])
            try:
                A_inv = np.linalg.pinv(A)
                break
            except np.linalg.LinAlgError:
                continue
        else:
            print("Failed to inverse the Phi^T*G*Phi matrix.")
            return False
        self.W = A_inv @ self.phi_with_ones.T @ self.RT
        # new projection into data space
        mu = self.phi_with_ones.dot(self.W)

        bsum = 0
        for idx, t in enumerate(self.data_series):
            gamma = self.gammas[idx]
            dist = cdist(t, mu, metric='sqeuclidean')
            bsum += (dist * gamma).sum()

        self.beta = self.N * self.seq_length * self.d / bsum

        # update P
        xi_sum = self.xi.sum(axis=1)
        xi_sum += (xi_sum == 0)  # avoid zero division
        self.P = (self.xi / xi_sum[:, None])
        # update eta
        self.eta = self.P.dot(self.C)
        self.P = self.eta.dot(self.CC)
        # update Prior
        self.priors = self.Pi_sum / self.N

        return True

    def fit(self, x: np.ndarray, y: np.ndarray | None = None, tol=10, epoch=10, early_stopping=False, verbose=True):
        """
        fit the GTM through time model
        x is in shape (n_obs, seq_length, dim)
        the EM process will stop if the change of loglikelihood < tolerance (tol)
        """
        self._init_vars(x)
        self.llhs = []
        for epoch in range(epoch):
            self.refresh_intermediates()
            for t in self.data_series:
                self.single_sequence_opt(t)  # a single gamma is appended to self.gammas

            flag = self.m_step()

            llh = self.Scale.sum()
            self.llhs.append(llh)
            if self.latent_coors:
                gammas = random.sample(self.gammas, 4)
                g = gammas[0]
                # modes = self.map_grid[g.argmax(axis=1)]
                means = g.dot(self.map_grid)
                self.latent_coors.update({'x': means[:, 0].tolist(), 'y': means[:, 1].tolist()})
                self.llh_coors = {'x': [*range(len(self.llhs))], 'y': self.llhs}
            if verbose:
                print(f"epoch: {epoch}, llh = {llh}")
            if not flag:
                print("Optimize failed. Due to failure in M-step. ")
                break
            # early stopping
            if early_stopping and epoch >= 2 and abs(self.llhs[-2] - llh) < tol:
                break

    def plot_llh(self):
        plt.plot(self.llhs)
        plt.title("GTMTT Training Log-likelihood")
        plt.xlabel("epoch")
        plt.ylabel("llh")
        plt.show()

    def score(self, x):
        return self.Scale.sum()

    def _init_vars(self, x: np.ndarray):
        """
        data: flattened data points with shape (n_obs * seq_length, dimension)
        """
        # use GTMBase to init phi, W and beta etc.
        n_obs, seq_length, dim = x.shape
        # flattened dataset
        self.T = x.reshape([-1, dim])
        super(GTMTimeSeries, self)._init_vars(self.T)
        # data in (num_series, length, dimension) form
        self.data_series = x
        # metrics
        self.d = dim
        self.D = dim
        self.seq_length = seq_length
        self.N = n_obs

        # scale is col wise sum of forward alpha
        self.Scale = np.array(self.seq_length)  # row wise sum of alpha, equation (91) in Rabiner1989

    def refresh_intermediates(self):
        # empty intermediate vars
        self.gamma_sum = np.zeros(self.K)
        self.gammas = []
        self.Scale = np.zeros(self.seq_length)
        self.xi = np.zeros([self.K, self.K])
        self.RT = np.zeros([self.K, self.d])
        self.Pi_sum = np.zeros(self.K)

    def single_sequence_opt(self, obs: np.ndarray):
        """
        Steps:
        for each sequence (length, d) in the training series sets (num_obs, length, d)
            1. calc DIST and B
            2. forward-backward
            3. gamma
            4. xi
            5. llh & sums

        This function only go through a single sequence.
        You are expected to call this function T times, where T is the number of time-series you have.
        And pass in a single sequence each time you call this function.
        After all sequences have been gone through, a M-step call must be followed.
        """
        # intermediates
        self.G: np.ndarray = np.zeros([self.K, self.K])

        # STEP 1: calc DIST & B
        # obs.shape = (seq_length, d)
        # dist = (d*K)
        mu = self.phi_with_ones.dot(self.W)
        # emission probability B, shape = (K*length)
        # note here: in the reference code, it is (length*K) matrix (transpose of this B)
        # note here: we do not add the mix-in coefficient 1/K
        dist = cdist(obs, mu, metric='sqeuclidean')
        max_dist = np.max(dist, axis=1)
        min_dist = np.min(dist, axis=1)
        median = (max_dist + min_dist) / 2
        median_variant = (min_dist + 600) * (2 / self.beta)
        dist_corr = np.minimum(median, median_variant)
        dist -= (np.ones(dist.shape).T @ np.diag(dist_corr)).T
        # emission probability B = (K*length)
        # note here: in the reference code, it is (length*K) matrix
        # note here: we do not add the mix-in coefficient 1/K
        self.B = ((self.beta / (2 * np.pi)) ** (self.d / 2)
                  *
                  np.exp((-self.beta / 2) * dist))

        # STEP 2: forward-backward
        # shape = (length, K) where K is the num of states
        forward_alpha, scale = self.forward(obs)
        backward_beta = self.backward(scale)

        # STEP 3: gamma
        gamma = self.calc_gamma(forward_alpha, backward_beta)
        self.gamma_sum += gamma.sum(axis=0)
        self.gammas.append(gamma)
        self.RT += gamma.T.dot(obs)
        self.Pi_sum += gamma[0]

        # STEP 4: xi
        self.calc_xi(forward_alpha, backward_beta)

        # STEP 5: add single time series scale to batch scale
        self.Scale += np.log(scale) - dist_corr * (self.beta / 2)

    def sample(self) -> np.ndarray:
        """
        sample a single sequence in data space from the model distribution
        using spherical gaussian distribution in data space
        """
        # initial state
        # state = np.random.choice([*range(self.K)], p=self.priors)
        state = np.argmax(self.priors)  # best possible start state
        res = []
        for n in range(self.seq_length):
            # project the latent point (hidden state) to data space
            phi: np.ndarray = self.phi_with_ones[state]
            mu = phi.dot(self.W)
            # sample from the data space distribution (d is dimension)
            # 1. init the covariance matrix to 1/beta
            covars = np.ones([self.d, self.d]) / self.beta
            # 2. find the eigen vales&vectors of cov
            evalue, evec = np.linalg.eig(covars)
            evalue = np.abs(evalue)
            # coef = sample from standard normal * sqrt eigen value
            coef = np.random.randn(1, self.d) * np.sqrt(evalue)
            # sample_x = mu + coef * eigen_vec
            val = mu + coef @ evec.T
            # val = np.random.multivariate_normal(mu, np.ones([self.d, self.d])*(1/self.beta), 1)
            res.append(val)
            # move to next state with transition probability P
            state = np.random.choice([*range(self.K)], p=self.P[state])
        res = np.array(res)
        return res

    def sample_states(self) -> np.ndarray:
        """
        get a state sequence sample from a trained GTMTT model
        states are numbered as [0, 1, 2, ..., num_states-1]

        Returns ndarray: [i, j, k, ..... ] where i j k are hidden states
        """
        states = []
        state = np.argmax(self.priors)  # best possible start state
        states.append(state)
        for i in range(1, self.seq_length):
            state = np.random.choice([*range(self.K)], p=self.P[state])
            states.append(state)
        states = np.array(states)
        return states

    def plot(self, mode='mode', labels: np.ndarray = np.array([]), **kwargs):
        """
        mode = 'mean' or ''mode
        """
        # sample from data
        data_idx = [i for i in range(self.data_series.shape[0])]
        sample_idx = random.choices(data_idx, k=4)
        if labels.any():
            plot_label = labels[sample_idx]
        else:
            plot_label = np.array([None] * 4)
        gammas = np.array(self.gammas)[sample_idx]
        fg, axis = plt.subplots(2, 2)

        if mode == 'mode':
            for g, ax, l in zip(gammas, axis.flatten(), plot_label):
                points = self.map_grid[g.argmax(axis=1)]
                x = points[:, 0]
                y = points[:, 1]
                ax.quiver(x[:-1], y[:-1], x[1:] - x[:-1], y[1:] - y[:-1], scale_units='xy', angles='xy', scale=1)
                ax.scatter(x, y)
                ax.set_title(l)
            plt.show()
        elif mode == 'mean':
            for g, ax in zip(gammas, axis.flatten()):
                points = g.dot(self.map_grid)
                x = points[:, 0]
                y = points[:, 1]
                ax.scatter(x, y)
            plt.show()
            print('done')
        return


if __name__ == '__main__':
    # read the same dataset from the matlab sample code
    dta = pd.read_excel("./data/example_data.xlsx", sheet_name=0, header=None)
    dta = dta.to_numpy()
    dta = dta[:, :9]  # first 9 cols
    print(dta.shape)
    dta = dta.reshape([4, dta.shape[0] // 4, 9])

    e = GTMTimeSeries(s=2, map_shape=(12, 12), group_size=2)
    e.fit(dta, epoch=30)
    print("vis time")

    e.plot(mode='mode')
    e.plot(mode='mean')
