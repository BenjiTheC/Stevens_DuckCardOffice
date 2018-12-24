""" command-line interface(CLI) for the duckcard office solution"""

import os
#import sqlite3
from datetime import datetime
import click
from stevens_systems import JSA, Blackboard, Slate, FacStaff, StudentInfo
from nerdy_ben import NerdyBen

os.chdir(os.path.abspath(os.path.dirname(__file__)))

@click.group()
def duckcard():
    """ Made by Benji, for Stevens DuckCard office"""

@duckcard.command()
@click.argument('data_source')
@click.argument
def meta(data_source):
    """ Set the metadata for the CLI."""
    click.echo(f'data source: {data_source}')
    click.echo('Under developed.')

@duckcard.command()
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display the counting detail of databases.')
def init(verbose):
    """ Building the database for the first time, will take about five minutes"""
    click.echo('Under developed.')

@duckcard.command()
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display the counting detail of databases.')
def update(verbose):
    """ Update the data of specific date, TODAY by default."""
    click.echo('Under developed.')

@duckcard.command()
def summary():
    """ Display the count of databases"""
    click.echo('Under developed.')
