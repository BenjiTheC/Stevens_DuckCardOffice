""" command-line interface(CLI) for the duckcard office solution"""

import os
import json
#import sqlite3
from datetime import datetime
import click
from stevens_systems import JSA, Blackboard, Slate, FacStaff, StudentInfo
from nerdy_ben import NerdyBen
from protective_case import entrance

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
            self.tbl_dct = {
                'bb': Blackboard(self.data_source, self.database),
                'sla': Slate(self.data_source, self.database),
                'jsa': JSA(self.data_source, self.database),
                'facsta': FacStaff(self.data_source, self.database),
                'sis': StudentInfo(self.data_source, self.database)
                }
            self.write_to = os.path.join(os.path.abspath(os.path.join(self.data_source, os.pardir)), 'NerdyBen')
            self.benji = NerdyBen(self.database, self.write_to)

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
        [x] silly	Distinguish error prone students
        [x] toimport	Get all students info that ready to be imported into Blackboard
        [x] toprint	Get all students who have their photos uploaded but ID cards not printed
        [x] remind	Get all students who are imported into the Blackboard but haven't uploaded their photos
        [x] check 	Check if our dear friends Kristen has or has not imported the data we send to her

        \b
        Recording issued protective case
            case    Protective case issue recording.
    """


@duckcard.command()
@click.argument('data_source')
@click.argument('database', default=os.path.abspath(os.path.join(os.curdir, 'dbfortest.db')), required=False)
def meta(data_source, database):
    """ Set the metadata for the CLI."""

    meta_data = {
        'data_source': os.path.abspath(data_source),
        'database': os.path.abspath(database)
        }
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
            tbl.print_count()

    else:
        for ali in tbls: # ali for alias, key of dictionary
            if ali in cfg.tbl_dct:
                cfg.tbl_dct[ali].print_count()
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
            t = cfg.tbl_dct[spc]
            t.insert_data(first_time=True)  # initialize the specific table
            if verbose:
                t.print_count()
        else:
            click.echo(f'{spc} is not a table.\nMore info in duckcard --help.')
            exit()
    else:  # build all of the tables
        for tbl in cfg.tbl_dct.values():
            tbl.insert_data(first_time=True)
            if verbose:
                tbl.print_count()


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
            t = cfg.tbl_dct[spc]
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
            try:
                tbl.insert_data(date=date)
            except FileNotFoundError:
                click.echo(f'No file to update {spc} on {date if date != TODAY else "today"}!')
                continue
            if verbose:
                tbl.print_count()


@duckcard.command()
#TODO: verbose mode
@click.argument('date', default=TODAY, required=False)
@pass_config
def silly(cfg, date):
    """ Distinguish the error prone student information."""
    cfg.benji.error_prone_distinguish(date=date)


@duckcard.command()
#TODO: verbose mode
@click.argument('date', default=TODAY, required=False)
@pass_config
def toimport(cfg, date):
    """ Get all students ready to be imported into Blackboard."""
    cfg.benji.to_import(date=date)


@duckcard.command()
#TODO: verbose mode
@click.argument('date', default=TODAY, required=False)
@pass_config
def toprint(cfg, date):
    """ Get all studens who have uploaded theri photos and not printed."""
    cfg.benji.to_print(date=date)


@duckcard.command()
#TODO: verbose mode
@click.argument('date', default=TODAY, required=False)
@pass_config
def remind(cfg, date):
    """ Get all list for mail merge to remind them about DuckCard."""
    cfg.benji.to_remind(date=date)


@duckcard.command()
#TODO: verbose mode
@click.argument('date', default=TODAY, required=False)
@pass_config
def check(cfg, date):
    """ Check if Kristen has imported the data we send to her."""
    cfg.benji.doublecheck_imported(date=date)

<<<<<<< HEAD

=======
>>>>>>> 0fd40bf010b6785f4811f2f17cc1b83c425447d1
@duckcard.command()
@click.argument('write_to', required=False)
@pass_config
def case(cfg, write_to):
    """ Protective case issue recording."""
    if not write_to:
        write_to = os.path.join(cfg.write_to, 'protective_cases_issued.csv')

    entrance(write_to)


def main():
    """ entrance"""
    test = Config()
    print(test.write_to)
    print('')

if __name__ == '__main__':
    main()
