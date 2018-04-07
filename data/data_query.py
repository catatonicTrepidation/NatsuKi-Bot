#!/usr/bin/python
# -*- coding: utf-8 -*-

import discord
import sqlite3 as lite
import sys

import random
from data.data_setup import get_con


async def get_top_words(msg, num_words, *args):  # sort arguments? that way the @mentions will all come after db_name
    con = get_con('messages', msg.server.id)
    cur = con.cursor()
    words = dict()
    SQLQuery = "SELECT Content FROM " + 'messages' + ' WHERE UserId = ' + msg.author.id
    # print('SQLQuery =',SQLQuery)
    cur.execute(SQLQuery)
    #messages = cur.fetchall()[0]
    filter_words = open('data/prepositions.txt', 'r').read().split('\n')
    for sentence in cur.fetchall():
        for w in sentence[0].split(' '):
            if len(w) > 8 and w not in filter_words:
                if w in words:
                    words[w] += 1
                else:
                    words[w] = 1

    top_words = [key for key, value in sorted(words.items(), key=lambda t: t[1])]
    #print(top_words[:num_words])
    #print('top_words[-num_words:][::-1 =',top_words[-num_words:][::-1])
    return top_words[-num_words:][::-1]
    #await self.ntsk.send_message(msg.channel, str(num_msgs) + " messages matched your query!")

