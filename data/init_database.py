#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys, os
import json

def initialize_databases(server):

    dir = 'databases/%s/' % (server.id,)
    if not os.path.exists(dir):
        os.makedirs(dir)

    con = lite.connect(dir + 'messages.db')
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Messages("
                    "Content TEXT, Id TEXT, Username TEXT, Nick TEXT, Channel TEXT, Time TEXT,"
                    "Server TEXT, SequentialId TEXT)")

    con = lite.connect(dir + 'uniquewords.db')
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS UniqueWords("
                    "Content TEXT, Id TEXT, Username TEXT, Nick TEXT, Channel TEXT, Time TEXT,"
                    "Server TEXT, SequentialId TEXT)")

    if not os.path.exists(dir + 'meta.json'):
        data = {'count', 0}
        with open(dir + 'meta.json', 'w') as outfile:
            json.dump(data, outfile)


class Server:
    def __init__(self, id):
        self.id = id

s = Server('123456789')
initialize_databases(s)