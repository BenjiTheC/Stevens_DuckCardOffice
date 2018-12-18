""" command-line interface(CLI) for the duckcard office solution"""

""" duckcard command group

    init: build JSA, Blackboard, Slate, insert current files.
    - args: file dir, MUST HAVE 3 dir: Blackboard, JSA, Slate -> case-sensitive

    update: update today's file
    - args: date, TODAY by default

    
"""
# TODO:
    #   init: first time -> print info and build + insert data
    #   update: date=TODAY, insert data
    #   get-silly: error distinguish
    #   get-import: to_import
    #   get-print: to_print
    #   get-remind: TODO: functionality under develop
    #   check-import: imported_check

import os
import sqlite3
import click

@click.command()

def main():
    """ Solution for printing cards for 19 spring incoming Stevens students."""
    print('Hello world')
    