#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

messages_con = lite.connect('messages.db')
wordheist_con = lite.connect('wordheist.db')
uniquewords_con = lite.connect('uniquewords.db')

connections = {'messages': messages_con,'wordheist':wordheist_con, 'uniquewords':uniquewords_con}

def get_con(db_name):
    return connections[db_name]