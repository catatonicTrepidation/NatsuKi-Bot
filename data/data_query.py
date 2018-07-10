#!/usr/bin/python
# -*- coding: utf-8 -*-

import discord
import sqlite3 as lite
import sys
import math
import string

import random
from data.data_setup import get_con


async def get_top_words(user_id, server_id, num_words, min_lth, punct_flag=False):  # sort arguments? that way the @mentions will all come after db_name
    con = get_con('messages', server_id)
    cur = con.cursor()
    words = dict()
    SQLQuery = "SELECT Content FROM " + 'messages'
    if user_id:
        SQLQuery += ' WHERE UserId = ' + user_id
    # print('SQLQuery =',SQLQuery)
    cur.execute(SQLQuery)
    #messages = cur.fetchall()[0]
    filter_words = open('data/prepositions.txt', 'r').read().split('\n')
    translator = str.maketrans('','',string.punctuation)
    for sentence in cur.fetchall():
        for w in sentence[0].split(' '):
            if not punct_flag:
                w = w.translate(translator).lower()
            if len(w) > min_lth and w not in filter_words:
                if w in words:
                    words[w] += 1
                else:
                    words[w] = 1

    top_words = [[key, value] for key, value in sorted(words.items(), key=lambda t: t[1])]
    #print(top_words[:num_words])
    #print('top_words[-num_words:][::-1 =',top_words[-num_words:][::-1])
    rankings = top_words[-num_words:][::-1]
    for i in range(len(rankings)):
        rankings[i] = str(i+1) + ". " + rankings[i][0] + " (" + str(rankings[i][1]) + ")"
    return rankings

#i don't want to make this one rn #async def get_logs()

async def rand_query(server_id, target_usr, num_msgs, img_flag=False):

    try:
        con = get_con('messages', server_id)
        cur = con.cursor()

        getCountQuery = "SELECT count(*) FROM " + 'messages'
        cur.execute(getCountQuery)
        cnt = int(cur.fetchall()[0][0])

        msg_results = []
        for i in range(num_msgs):

            rand_id = random.randrange(cnt) + 1

            randMsgQuery = "SELECT Content, UserId, Username, Time FROM messages WHERE DatabaseId = " + str(rand_id)
            if target_usr:
                randMsgQuery += " AND UserId = " + str(target_usr) # LOL no, this goes in the getCountQuery part (sorta)

            cur.execute(randMsgQuery)

            x = list(cur.fetchall()[0])
            #print('msg =', x)

            msg_results.append(x)

        print(msg_results)

        return True, msg_results
    except:
        print('THERE WAS A FAILURE!')
        return False, None


async def id_query(server_id, start_idx, num_msgs, img_flag=False):
    try:
        con = get_con('messages', server_id)
        cur = con.cursor()

        getCountQuery = "SELECT count(*) FROM " + 'messages'
        cur.execute(getCountQuery)
        cnt = int(cur.fetchall()[0][0])
        print('cnt =',cnt)
        print("type(start_idx) =",type(start_idx))

        if start_idx > cnt:
            return False, "That ID too high!!!!!!!!"

        #start_idx = (cnt + start_idx)%cnt + 1
        if start_idx < 0:
            start_idx = cnt + start_idx + 1

        print('start_idx =',start_idx)

        lftovr = 0
        right_idx = start_idx + num_msgs//2
        if cnt < right_idx:
            lftovr += right_idx - cnt
            right_idx = cnt

        left_idx = start_idx - math.ceil(num_msgs/2)
        if 1 > left_idx:
            left_idx = 1
            right_idx = min(right_idx + (1 - left_idx))

        left_idx = max(left_idx - lftovr, 1)

        idMsgQuery = "SELECT Content, UserId, Username, Time FROM messages WHERE DatabaseId = "
        msg_results = []

        print(left_idx, "|",right_idx)
        for i in range(left_idx+1, right_idx+1):
            cur.execute(idMsgQuery + str(i))
            #content, author, date = cur.fetchall()[0]
            x = list(cur.fetchall()[0])
            print('x =',x)
            msg_results.append(x)
        print('msg_results:')
        print(msg_results)
        return True, msg_results
    except Exception as e:
        print('error querying messages:')
        print(e)

    return False, "Error getting logs... :*("

