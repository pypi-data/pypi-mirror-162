import time

from bokeh.server.server import Server
from bokeh.layouts import row
from bokeh.document import Document

from threading import Thread

from random import random
from bokeh.models import ColumnDataSource, AjaxDataSource
from bokeh.plotting import figure


def update(source, data):
    source.data = data


def new_doc(doc: Document):
    # sources
    latent_space_source = AjaxDataSource(data_url='http://127.0.0.1:5000/latent_space', polling_interval=500, method='GET')
    llhs_source = AjaxDataSource(data_url='http://127.0.0.1:5000/llh', polling_interval=500, method='GET')
    # figs
    p1 = figure(x_range=(-1, 1), y_range=(-1, 1), toolbar_location=None, x_axis_label="x1", y_axis_label='x2')
    p1.width = 800
    p1.height = 600
    p1.outline_line_color = None
    p1.grid.grid_line_color = None
    p1.circle(x='x', y='y', source=latent_space_source)
    p1.title = "Latent space"
    p2 = figure(x_range=(0, 50), toolbar_location=None)
    p2.title = "Log-likelihood"
    p2.width = 500
    p2.height = 300
    p2.line(x='x', y='y', source=llhs_source)
    r = row([p1, p2])
    doc.set_title("Latent space visualization")
    doc.add_root(r)
    doc.on_session_destroyed(lambda ctx: print("Session destroyed"))


def run_server():
    """Start bokeh vis hosting server"""
    server = Server({'/': new_doc}, port=1234)
    server.io_loop.add_callback(server.show, '/')
    server_t = Thread(target=server.io_loop.start, args=())
    server_t.setDaemon(True)
    server_t.start()
    return server_t


if __name__ == '__main__':
    t1 = run_server()
    data = {'x': [random() for _ in range(5)], 'y': [random() for _ in range(5)]}
    for i in range(100):
        time.sleep(1)
        data.update({'x': [random() for _ in range(5)], 'y': [random() for _ in range(5)]})




