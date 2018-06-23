#!/usr/bin/python
# -*- coding: utf-8 -*-

import discord
import sqlite3 as lite
import sys

import random
from data.data_setup import get_con


async def get_top_words(user_id, server_id, num_words, min_lth, *args):  # sort arguments? that way the @mentions will all come after db_name
    con = get_con('messages', server_id)
    cur = con.cursor()
    words = dict()
    SQLQuery = "SELECT Content FROM " + 'messages' + ' WHERE UserId = ' + user_id
    # print('SQLQuery =',SQLQuery)
    cur.execute(SQLQuery)
    #messages = cur.fetchall()[0]
    filter_words = open('data/prepositions.txt', 'r').read().split('\n')
    for sentence in cur.fetchall():
        for w in sentence[0].split(' '):
            if len(w) > min_lth and w not in filter_words:
                if w in words:
                    words[w] += 1
                else:
                    words[w] = 1

    top_words = [key for key, value in sorted(words.items(), key=lambda t: t[1])]
    #print(top_words[:num_words])
    #print('top_words[-num_words:][::-1 =',top_words[-num_words:][::-1])
    rankings = top_words[-num_words:][::-1]
    for i in range(len(rankings)):
        rankings[i] = str(i+1) + ". " + rankings[i]
    return rankings

