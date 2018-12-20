""" setup the whole application as a command-line interface"""
from setuptools import setup

setup(
    name='DuckCard',
    version='1.0',
    py_modules=['duckcard'],
    include_package_data=True,
    install_requires=[
        'tabulate', 'Click'
    ],
    description=\
        """ The customized solution for duckcard office printing the newly 19 spring students' ID cards""",
    author='Benjamin Cai',
    author_email="benjamincaiyh@gmail.com or ycai11@stevens.edu",
    license='GNU',
    entry_points={
        'console_scripts':[
            'duckcard=duckcard:duckcard'
        ]
    }
)
