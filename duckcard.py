""" command-line interface(CLI) for the duckcard office solution"""

import os
import json
#import sqlite3
from datetime import datetime
import click
from stevens_systems import JSA, Blackboard, Slate, FacStaff, StudentInfo
from nerdy_ben import NerdyBen

TODAY = datetime.today().strftime('%y%m%d')

os.chdir(os.path.abspath(os.path.dirname(__file__)))

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
            self.tbl_dct = {'bb': Blackboard, 'sla': Slate, 'jsa': JSA, 'facsta': FacStaff, 'sis': StudentInfo}

pass_config = click.make_pass_decorator(Config, ensure=True)
    
@click.group()
@click.version_option()
def duckcard():
    """ \b
        duckcard: 
                Made by Benji, for the Stevens DuckCard Office

        \b
        duckcard is a command line interface designed for the program used to process received newly admitted
        students' data. This documentation describes the commands group design of the CLI application.

        \b
        Initialize a database build
        [x] meta	Set the data source path and database path, store the setting in a .json file
        [x] init	First time building a database. By default builds all of the tables

        \b
        Maintain and visulize database
        [x] update	Update the data of specific day of time spans
        [x] summary	Show the summary information of specific table or all of the tables by default
            search	Support single keyword searching in the database. Limited only for basic SQL
        
        \b
        Extract and write the desired data to the files
            silly	Distinguish error prone students
            toimport	Get all students info that ready to be imported into Blackboard
            toprint	Get all students who have their photos uploaded but ID cards not printed
            remind	Get all students who are imported into the Blackboard but haven't uploaded their photos
            check 	Check if our dear friends Kristen has or has not imported the data we send to her

    """


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
        
        if not click.confirm('Are you sure you want to override the meta data?'):
            click.echo('\nYou choose to keep the current meta data.')
            exit()

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
    if 'all' in tbls or not tbls:  # either given a 'all' argument or no argument
        for tbl in cfg.tbl_dct.values():  # display summaries of all tables
            tbl(cfg.data_source, cfg.database).print_count()

    else:
        for ali in tbls: # ali for alias, key of dictionary
            if ali in cfg.tbl_dct:
                cfg.tbl_dct[ali](cfg.data_source, cfg.database).print_count()
            else:
                click.echo(f'{ali} is not a table in the database.\nMore info in duckcard --help.')
                exit()


@duckcard.command()
@click.option('--specific', '-sp', 'spc',
              help='Only create one specific table.')
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display the counting detail of databases.')
@pass_config
def init(cfg, verbose, spc):
    """ Building the database for the first time, will take about five minutes"""
    if spc:
        if spc in cfg.tbl_dct:
            t = cfg.tbl_dct[spc](cfg.data_source, cfg.database)
            t.insert_data(first_time=True)  # initialize the specific table
            if verbose:
                t.print_count()
        else:
            click.echo(f'{spc} is not a table.\nMore info in duckcard --help.')
            exit()
    else:  # build all of the tables
        for tbl in cfg.tbl_dct.values():
            t = tbl(cfg.data_source, cfg.database)
            t.insert_data(first_time=True)
            if verbose:
                t.print_count()


@duckcard.command()
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display the counting detail of databases.')
@click.option('--specific', '-sp', 'spc',
              help='Only update one specific table.')
@click.argument('date', default=TODAY, required=False)
@pass_config
def update(cfg, verbose, date, spc):
    """ Update the data of specific date, TODAY by default.

        - date    update the data of specific date, TODAY by default.
    """
    if spc:
        if spc in cfg.tbl_dct:
            t = cfg.tbl_dct[spc](cfg.data_source, cfg.database)
            try:
                t.insert_data(date=date)
            except FileNotFoundError:
                click.echo(f'No file to update {spc} on {date if date != TODAY else "today"}!')
                exit()
            if verbose:
                t.print_count()
        else:
            click.echo(f'{spc} is not a table.\nMore info in duckcard --help.')
            exit()
    else:
        for tbl in cfg.tbl_dct.values():
            t = tbl(cfg.data_source, cfg.database)
            try:
                t.insert_data(date=date)
            except FileNotFoundError:
                click.echo(f'No file to update {spc} on {date if date != TODAY else "today"}!')
                continue
            if verbose:
                t.print_count()
