""" Building the database application for Slate, Blackboard, JSA, etc with SQLAlchemy ORM."""

import os
from sqlalchemy import create_engine, Column, Integer, String, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#import sqlite3

db = 'sqlite:///duckcard_test.db'
engine = create_engine(db)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Slate(Base):
    """ Slate table mapping"""
    __tablename__ = 'Slate'

    cwid = Column(String, primary_key=True)
    first = Column(String)
    middle = Column(String)
    last = Column(String)
    raw_first = Column(String)
    raw_middle = Column(String)
    raw_last = Column(String)
    raw_email = Column(String)
    raw_username = Column(String)
    received_date = Column(DATETIME)

    def __repr__(self):
        return f'Slate student:\n\tcwid: {self.cwid}\n\tfirst: {self.raw_first}\n\tmiddle: {self.raw_middle}\n\tlast: {self.raw_last}'

class Blackboard(Base):
    """ Blackboard table mapping"""
    __tablename__ = 'Blackboard'

    cwid = Column(String, primary_key=True)
    first = Column(String)
    middle = Column(String)
    last = Column(String)
    raw_first = Column(String)
    raw_middle = Column(String)
    raw_last = Column(String)
    received_date = Column(DATETIME)

    def __repr__(self):
        return f'Blackboard student:\n\tcwid: {self.cwid}\n\tfirst: {self.raw_first}\n\tmiddle: {self.raw_middle}\n\tlast: {self.raw_last}'


class JSA(Base):
    """ JSA table mapping"""
    __tablename__ = 'JSA'

    cwid = Column(String, primary_key=True)
    first = Column(String)
    last = Column(String)
    status = Column(String)
    submit_date = Column(DATETIME)
    received_date = Column(DATETIME)

    def __repr__(self):
        return f'JSA student:\n\tcwid: {self.cwid}\n\tfirst: {self.first}\n\tlast: {self.last}'

class FacStaff(Base):
    """ FacStaff table mapping"""
    __tablename__ = 'FacStaff'

    cwid = Column(String, primary_key=True)
    first = Column(String)
    middle = Column(String)
    last = Column(String)
    email = Column(String)
    phone = Column(String)
    received_date = Column(DATETIME)

    def __repr__(self):
        return f'Faculty/Staff:\n\tcwid: {self.cwid}\n\tfirst: {self.first}\n\tmiddle: {self.middle}\n\tlast: {self.last}'

class StudentInfo(Base):
    """ StudentInfo table mapping"""
    __tablename__ = 'Students_18F'

    cwid = Column(String, primary_key=True)
    first = Column(String)
    last = Column(String)
    stevens_e = Column(String)
    personal_e = Column(String)
    exit_term = Column(String)
    level = Column(String)
    received_date = Column(DATETIME)

    def __repr__(self):
        return f'StudentInfo student:\n\tcwid: {self.cwid}\n\tfirst: {self.first}\n\tlast: {self.last}'
