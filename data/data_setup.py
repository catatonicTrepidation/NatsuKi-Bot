#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys, os
import json



def initialize_databases(server):
    print('INITIALIZING DATABASES FOR SERVER', server.id)

    dir = 'data/databases/%s/' % (server.id,)
    if not os.path.exists(dir):
        os.makedirs(dir)
        os.makedirs(dir + '/output/images/')
        os.makedirs(dir + '/downloaded/images/')

    print('DIR =',dir)

    con = lite.connect(dir + 'messages.db')
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Messages("
                    "Content TEXT, Id TEXT, UserId TEXT, Username TEXT, ChannelId TEXT, Time TEXT,"
                    "ServerId TEXT, SequentialId TEXT)")

    con = lite.connect(dir + 'uniquewords.db')
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS UniqueWords("
                    "Word TEXT, Id TEXT, UserId TEXT, Username TEXT, ChannelId TEXT, Time TEXT,"
                    "ServerId TEXT)")

    if not os.path.exists(dir + 'meta.json'):
        data = {'count': 0}
        with open(dir + 'meta.json', 'w') as outfile:
            json.dump(data, outfile)

    if not os.path.exists(dir + 'characters.json'):
        chars = {}
        for member in server.members:
            chars[member.id] = {'score': 0, 'quote': ''}

        data = {'characters': chars}
        with open(dir + 'characters.json', 'w') as outfile:
            json.dump(data, outfile)



def get_con(db_name, server_id):
    con = lite.connect('data/databases/%s/%s.db' % (server_id, db_name))
    return con

def get_meta(server_id):
    metadata = json.load(open('data/databases/%s/meta.json' % (server_id,)))
    return metadata
