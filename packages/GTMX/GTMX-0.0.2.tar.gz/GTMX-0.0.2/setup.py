from setuptools import setup, find_packages

setup(
    name='GTMX',
    version='0.0.2',
    description="A Python package for Generative Topographic Mapping (GTM)",
    url='https://github.com/innovationb1ue/GTMX',
    install_requires=[
        'numpy',
        'scipy',
        'scikit-learn',
        'matplotlib',
        'bokeh'
    ],
    include_dirs=['data']
)