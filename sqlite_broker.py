#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

from string import punctuation
from data.data_setup import get_con, get_meta



def add_message(db_name, msg):
    """
    Add discord message to database
    :param db_name: database to augment
    :param msg: message to add
    """
    #metadata = get_meta(msg.server.id)
    #count = metadata['count'] + 1

    con = get_con(db_name, msg.server.id)
    msg_content = msg.content
    if len(msg.attachments) > 0:
        temp1 = temp2 = msg_content
        for atch in msg.attachments:
            temp2 += "\n" + atch['url']
            if len(temp2) > 2000:
                break
            temp1 = temp2
        msg_content = temp1

    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO " + db_name + " VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                    (None, msg_content, msg.id, msg.author.id, msg.author.name, msg.channel.id, str(msg.timestamp), msg.server.id))

    # catch exception? return True for success?


def add_unique_words(msg):
    """
    Checks if message contains at least one unique word, adds unique words if true
    :param msg:
    :return:
    """
    con = get_con('uniquewords', msg.server.id)
    content = msg.content
    translator = str.maketrans('', '', punctuation)
    content = content.translate(translator)
    content = content.lower().split(' ')

    valid, bools = contains_unique_word(con, content)
    if not valid:
        return False

    with con:
        cur = con.cursor()
        for c in range(len(content)):
            if bools[c]:  # want to add
                cur.execute("INSERT INTO " + 'UniqueWords' + " VALUES(?, ?, ?, ?, ?, ?, ?)",
                            (content[c], msg.id, msg.author.id, msg.author.name, msg.channel.id, str(msg.timestamp), msg.server.id))

    return True

def contains_unique_word(con, content):
    """
    Checks if message contains at least one unique word (relative to uniquewords.db)
    :param con: connection to uniquewords.db
    :param content: list of words in message
    :return: true if contains unique word ; list of booleans corresponding to words in content (whether unique or not)
    """
    with con:
        cur = con.cursor()
        cur.execute("SELECT Word FROM " + 'UniqueWords')
        rows = cur.fetchall()

        bools = [True]*len(content)
        for row in rows:
            for i in range(len(content)):
                if bools[i] and row[0] == content[i]:
                    bools[i] = False

    return any(bools), bools



# grabs all full messages, splits each by space. less efficient
def contains_unique_word_by_channel(db_name, channel, msg):
    con = get_con(db_name, msg.server.id)
    with con:
        cur = con.cursor()
        cur.execute("SELECT Content FROM " + db_name + " WHERE Channel LIKE ? ", (channel,))

        rows = cur.fetchall()

        content = msg.content.split(' ')
        if not rows:
            return True
        for row in rows:
            unique_to_row = False
            for w in content:
                if w not in row[0]:
                    unique_to_row = True
            if not unique_to_row:
                return False
        return True
