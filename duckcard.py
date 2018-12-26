""" command-line interface(CLI) for the duckcard office solution"""

import os
import json
#import sqlite3
from datetime import datetime
import click
from stevens_systems import JSA, Blackboard, Slate, FacStaff, StudentInfo
from nerdy_ben import NerdyBen

os.chdir(os.path.abspath(os.path.dirname(__file__)))

def meta_exist():
    """ Check if the meta data is existed and valid."""


class Config:
    """ Pass the configuration of program to each command"""

    def __init__(self):
        try:
            fread = open('meta_duckcard.json', 'r')
        except FileNotFoundError:
            click.echo('duckcard: there is no meta data given. See "duckcard --help".\n')
            click.echo('command to set the data source and database pathes:\n\tduckcard meta')
            exit()
        else:
            with fread:
                self.__dict__ = json.load(fread)

pass_config = click.make_pass_decorator(Config, ensure=True)
    
@click.group()
def duckcard():
    """ Made by Benji, for Stevens DuckCard office"""

@duckcard.command()
@click.argument('data_source')
@click.argument('database', default=os.path.abspath(os.path.join(os.curdir, 'dbfortest.db')), required=False)
def meta(data_source, database):
    """ Set the metadata for the CLI."""

    meta_data = {'data_source': data_source, 'database': database}
    existed_meta = dict()
    
    if os.path.isfile(os.path.join(os.curdir, 'meta_duckcard.json')):
        with open('meta_duckcard.json', 'r') as fread:
            existed_meta = json.load(fread)
    if existed_meta and existed_meta != meta_data:
        click.echo('Current data source path: ' + existed_meta['data_source'])
        click.echo('Current database path: ' + existed_meta['database'])
        while True:
            decision = input('Are you sure you want to override the meta data? [y/n] ')
            if decision in ('y', 'Y'):
                break
            elif decision in ('n', 'N'):
                click.echo('Cancel the meta data setting.')
                exit()
            else:
                click.echo('Answer my question! JAVA people :p')

    with open('meta_duckcard.json', 'w') as fwrite:
        json.dump(meta_data, fwrite)

    click.echo(f'Set data source path to {data_source}.')
    click.echo(f'Set datadase path to {database}.')

@duckcard.command()
@click.argument('tbls', nargs=-1, required=False)
@pass_config
def summary(cfg, tbls):
    """ usage: duckcard summary [<table name>]
        Display the tables' info
    """
    tbl_dct = {'bb': Blackboard, 'sla': Slate, 'jsa': JSA, 'facsta': FacStaff, 'sis': StudentInfo}

    if 'all' in tbls or not tbls:  # either given a 'all' argument or no argument
        for tbl in tbl_dct.values():  # display summaries of all tables
            tbl(cfg.data_source, cfg.database).print_count()

    else:
        for ali in tbls: # ali for alias, key of dictionary
            if ali in tbl_dct:
                tbl_dct[ali](cfg.data_source, cfg.database).print_count()

@duckcard.command()
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display the counting detail of databases.')
def init(verbose):
    """ Building the database for the first time, will take about five minutes"""
    if verbose:
        click.echo('verbose mode')
    click.echo('Under developed.')

@duckcard.command()
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display the counting detail of databases.')
def update(verbose):
    """ Update the data of specific date, TODAY by default."""
    if verbose:
        click.echo('verbose mode')
    click.echo('Under developed.')
