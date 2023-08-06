GTMX
======

Description
------------
A Python package for Generative Topographic Mapping (GTM)
Provide original version of GTM by Bishop et al. (1998) and GTM through time by Bishop et al. (1997).

Installation
--------------

.. code-block:: console

    $ pip install gtmx


basic GTM
---------

.. code-block:: python

    from gtmx import GTMBase
    from sklearn.datasets import load_iris

    iris = load_iris()
    x = iris.data
    y = iris.target

    gtm = GTMBase(l=1)
    gtm.fit(x, epoch=30)
    gtm.plot_llh()
    gtm.plot('mean', label=y)
    gtm.plot('mode', label=y)

GTM through time
-------------------

.. code-block:: python

    from gtmx import GTMTimeSeries
    import numpy as np

    x = np.ndarray(["Your time series data in shape (n_obs, sequence, dimension)"])

    gtm = GTMTimeSeries()
    gtm.fit(x)
    gtm.plot_llh()
    gtm.plot('mean')
    gtm.plot('mode')



