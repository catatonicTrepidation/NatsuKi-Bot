#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
import sql_setup



def add_message(db_name, msg):
    con = sql_setup.get_con(db_name)
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO " + db_name + " VALUES(?, ?, ?, ?, ?, ?)",
                    (msg.id, msg.author.id, msg.author.nick, msg.channel.name, str(msg.timestamp), msg.content))


# queries word database of uniquewords.db
def add_unique_words(msg):
    con = sql_setup.get_con('uniquewords')

    with con:
        cur = con.cursor()
        cur.execute("SELECT Content FROM " + 'UniqueWords')
        rows = cur.fetchall()

        content = msg.content.split(' ')
        bools = [True]*len(content)
        for row in rows:
            for i in range(len(content)):
                if bools[i] and row[0] == content[i]:
                    bools[i] = False

        for c in range(len(content)):
            if bools[c]: #want to add
                cur.execute("INSERT INTO " + 'UniqueWords' + " VALUES(?, ?, ?, ?, ?, ?)",
                            (msg.id, msg.author.id, msg.author.nick, msg.channel.name, str(msg.timestamp), content[c]))

        return any(bools)


# grabs all full messages, splits each by space. less efficient
def contains_unique_word_by_channel(db_name, channel, msg):
    con = sql_setup.get_con(db_name)
    #print('con =',con)
    with con:
        cur = con.cursor()
        cur.execute("SELECT Content FROM " + db_name + " WHERE Channel LIKE ? ", (channel,))

        rows = cur.fetchall()

        content = msg.content.split(' ')
        print('rows =',rows)
        print('content =', content)
        if not rows:
            return True
        for row in rows:
            print('row[0] =',row[0])
            unique_to_row = False
            for w in content:
                if w not in row[0]:
                    unique_to_row = True
            if not unique_to_row:
                return False
        return True
