""" setup the whole application as a command-line interface"""
from setuptools import setup

setup(
    name='DuckCard',
    version='1.0',
    py_modules=['duckcard'],
    install_requires=[
        'tabulate', 'Click'
    ],
    entry_points={
        'console_scripts':[
            'duckcard=duckcard:main'
        ]
    }
)
