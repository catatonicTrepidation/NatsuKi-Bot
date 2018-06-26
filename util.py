#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
from string import punctuation
import re


def contains_curse_word(sentence):
    """
    Checks if sentence contains a curse word/profanity
    :param sentence: sentence to check
    :return: true if has curse word
    """
    translator = str.maketrans('', '', punctuation)
    sentence = sentence.translate(translator)
    sentence = sentence.lower()
    with open('data/react/bad_words.txt', errors="ignore") as f:
        word = f.readline()[:-1]
        while word:
            if word in sentence:
                return True
            word = f.readline()[:-1]
    return False

def valid_bow_message(sentence):
    """
    Checks if sentence is a valid way to praise NatsuKi
    :param sentence: sentence to check
    :return: true if valid praise
    """
    sentence = sentence.split(' ')
    if len(sentence) > 2:
        return False
    bows = ['🙇','🙇🏻','🙇🏼','🙇🏽','🙇🏾','🙇🏿']
    return sentence[0] == '<@422527461591482379>' and sentence[1] in bows or\
           sentence[1] == '<@422527461591482379>' and sentence[0] in bows


def detect_image(messages):
    """
    Detects latest message with curse word
    :param messages: messages in NatsuKi's temporary storage
    :return: matching message ; if it's an attachment ; if it's an embed
    """
    N = len(messages)
    msg_to_decode = None
    attch = embed = False
    i = 0
    j = 0
    orig_message = messages[-1]
    while i < 100 and j < min(20, N):
        print(messages[N - i - 1].channel.id != orig_message.channel.id)
        if messages[N - i - 1].channel.id != orig_message.channel.id:
            i += 1
            continue
        print('detect_image: thisAttch =', messages[N - i - 1].attachments)
        if len(messages[N - i - 1].attachments) != 0:
            msg_to_decode = messages[N - i - 1]
            attch = True
            break
        print('detect_image: thisEmbed =', messages[N - i - 1].embeds)
        if len(messages[N - i - 1].embeds) != 0:
            if messages[N - i - 1].embeds[0]['url'][-3:] in ['png', 'jpg', 'peg']:
                msg_to_decode = messages[N - i - 1]
                embed = True
                break
        i += 1
        j += 1
    print(msg_to_decode, attch, embed)
    return msg_to_decode, attch, embed  # change attach/embed to single var?

async def format_logs(logs, get_user_info):
    formatted_text = ""
    ft_copy = formatted_text

    for content, user_id, username, date in logs:
        formatted_text += date + "\n"
        if username == "Unknown":
            try:
                usr = await get_user_info(user_id)
                formatted_text += usr.name
            except:
                print("couldn't find user")
        else:
            formatted_text += username
        formatted_text += " (" + user_id + "):\n" + content
        formatted_text += "\n\n"

        if len(formatted_text) > 2000:
            break
        ft_copy = formatted_text

    return ft_copy

async def prepare_for_image(logs, get_user_info):
    for i in range(len(logs)):
        content, user_id, username, date = logs[i]
        if username == "Unknown":
            try:
                usr = await get_user_info(user_id)
                logs[i][2] = usr.name

                if usr.avatar_url:
                    logs[i].append(usr.avatar_url)
                else:
                    logs[i].append(usr.default_avatar_url)
            except:
                print("couldn't find user")
        else:
            usr = await get_user_info(user_id)
            logs[i][2] = usr.name

            if usr.avatar_url:
                logs[i].append(usr.avatar_url)
            else:
                logs[i].append(usr.default_avatar_url)

    return logs