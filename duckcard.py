""" command-line interface(CLI) for the duckcard office solution"""

import os
#import sqlite3
from datetime import datetime
import click
from stevens_systems import JSA, Blackboard, Slate, FacStaff, StudentInfo
from nerdy_ben import NerdyBen

os.chdir(os.path.abspath(os.path.dirname(__file__)))

def unfinished(s):
    """ To display not finished function."""
    print(f'functionality is still under developed. -- {s}')

class Config:
    """ Set the default source file path and database path and first_time flag"""
    
    duckcard_data = os.path.abspath(os.path.join(os.pardir, 'DuckCard_data'))
    today = datetime.today().strftime('%y%m%d')

    def __init__(self):
        self.db = os.path.join(Config.duckcard_data, 'duckcard_DB.db')
        self.slate = os.path.join(Config.duckcard_data, 'Slate')
        self.bb = os.path.join(Config.duckcard_data, 'Blackboard')
        self.jsa = os.path.join(Config.duckcard_data, 'JSA')
        self.sis = os.path.join(Config.duckcard_data, 'StudentInfo')
        self.facsta = os.path.join(Config.duckcard_data, 'FacStaff')
        self.first_time = False
        self.write_to = os.path.join(Config.duckcard_data, 'NerdyBen')
        self.date = Config.today

pass_duckcard = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--set-sourcefile', '-sf', 'source_file', type=click.Path(), default=None,
              help='Change the default source file path.')
@click.option('--set-database', '-db', 'database', type=click.Path(), default=None,
              help='Change the default database path.')
@click.option('--first-time/--not-first-time', is_flag=True, default=False,
              help='Only applicable when first time building the database.')
@click.option('--date', default=None,
              help='update the data of the specific date')
@pass_duckcard
def duckcard(config, source_file, database, first_time, date):
    """ Made by Benji, for Stevens DuckCard office"""
    if source_file:
        click.echo(f'reset source file path: {config.duckcard_data} -> {source_file}')
        config.duckcard_data = source_file
    if database:
        click.echo(f'reset database link: {config.db} -> {database}')
        config.db = database
    if first_time:
        config.date = None
        config.first_time = first_time
    if date:
        config.date = date
    if config.first_time and config.date:
        click.echo("You can't do first_time and on date at the same time!")

@duckcard.command()
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display the counting detail of databases.')
@pass_duckcard
def init(config, verbose):
    """ Building the database for the first time, will take about five minutes"""
    if not config.first_time:
        click.echo('This is not your first time building the database, the command should not be used!')
        exit()
    click.echo('This operation will take about 5 minutes to finish, please do not close the terminal...')

    click.echo('\nBuilding the Blackboard database...')
    Blackboard(config.bb, config.db).insert_data(first_time=config.first_time)
    click.echo('Blackboard database built.')

    click.echo('\nBuilding the Slate database...')
    Slate(config.slate, config.db).insert_data(first_time=config.first_time)
    click.echo('Slate database built')

    click.echo('\nBuilding the JSA database...')
    JSA(config.jsa, config.db).insert_data(first_time=config.first_time)
    click.echo('JSA database built')

    click.echo('\nBuilding the Students 18F database...')
    StudentInfo(config.sis, config.db).insert_data(first_time=config.first_time)
    click.echo('Students 18F built')

    click.echo('\nBuilding the FacStaff database...')
    FacStaff(config.facsta, config.db).insert_data(first_time=config.first_time)
    click.echo('FacStaff built')

    if verbose:
        Blackboard(config.bb, config.db).print_count()
        Slate(config.slate, config.db).print_count()
        JSA(config.jsa, config.db).print_count()
        StudentInfo(config.sis, config.db).print_count()
        FacStaff(config.facsta, config.db).print_count()

    click.echo('\nAll databases built.')

@duckcard.command()
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display the counting detail of databases.')
@pass_duckcard
def update(config, verbose):
    """ Update the data of specific date, TODAY by default."""
    try:
        Blackboard(config.bb, config.db).insert_data(date=config.date)
    except FileNotFoundError:
        click.echo('No data to update Blackboard.')

    try:
        Slate(config.slate, config.db).insert_data(date=config.date)
    except FileNotFoundError:
        click.echo('No data to update Slate.')
    
    try:
        JSA(config.jsa, config.db).insert_data(date=config.date)
    except FileNotFoundError:
        click.echo('No data to update Slate')

    try:
        StudentInfo(config.sis, config.db).insert_data(date=config.date)
    except FileNotFoundError:
        click.echo('No data to update StudentInfo')

    try:
        FacStaff(config.facsta, config.db).insert_data(date=config.date)
    except FileNotFoundError:
        click.echo('No data to update FacStaff')

    if verbose:
        Blackboard(config.bb, config.db).print_count()
        Slate(config.slate, config.db).print_count()
        JSA(config.jsa, config.db).print_count()
        StudentInfo(config.sis, config.db).print_count()
        FacStaff(config.facsta, config.db).print_count()

@duckcard.command()
@click.argument('action')
@pass_duckcard
def get(config, action):
    """ Get the required data, select the action from the action pool\n
        Action pool:\n
          - silly: error_prone_distinguish\n
          - import: to_import\n
          - print: to_print\n
          - check: doublecheck_imported\n
          - continue: under developed\n
          - remind: under developed\n
    """
    benji = NerdyBen(config.db, config.write_to)
    date = config.date
    action_pool = {
        'silly': benji.error_prone_distinguish,
        'import': benji.to_import,
        'print': benji.to_print,
        'check': benji.doublecheck_imported,
        'continue': unfinished,
        'remind': unfinished
    }

    if action in action_pool:
        action_pool[action](date)
    else:
        click.echo('Error: The action you enter is not in the action pool.')
        click.echo('action pool: {silly, import, print, check, continue, remind}')
        exit()

@duckcard.command()
@pass_duckcard
def display(config):
    """ Display the count of databases"""
    Blackboard(config.bb, config.db).print_count()
    Slate(config.slate, config.db).print_count()
    JSA(config.jsa, config.db).print_count()
    StudentInfo(config.sis, config.db).print_count()
    FacStaff(config.facsta, config.db).print_count()
