from setuptools import setup, find_packages

setup(
    name='GTMX',
    version='0.0.1',
    install_requires=[
        'numpy',
        'scipy',
        'scikit-learn',
        'matplotlib',
        'bokeh'
    ],
    packages=find_packages(where='.',
                           include=['bokeh_app']),
    include_dirs=['data']
)