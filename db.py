#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import sqlite3
from sqlalchemy import create_engine, exc, MetaData, Table, Column, Integer, String, Boolean, Date, Time, DateTime

meta = MetaData()

## MySQL
#
# db_user = 'user'
# db_pass = 'pass'
# db_host = '127.0.0.1'
# db_port = '3306'
# db_name = 'spotify_accounts'
#
# db = create_engine('mysql://' + db_user + ':' + db_pass +                             '@' + db_host + ':' + db_port + '/' + db_name)
#
##

# SQLite
db = create_engine('sqlite:///accounts.db', echo=True)

# spotify.accounts db schema
accounts = Table(
    'accounts', meta,
    Column('id', Integer, primary_key=True),
    Column('first_name', String),
    Column('last_name', String),
    Column('email', String, unique=True),
    Column('password', String),
    Column('display_name', String),
    Column('gender', String),
    Column('birth_date', String),
    Column('verified', Boolean),
    Column('password_reset', Boolean),
    Column('creation_date', DateTime, default=datetime.utcnow),
    Column('last_login', DateTime),
    Column('in_use', Boolean),
    )

# create database/tables if doesn't exist
meta.create_all(db)
