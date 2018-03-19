#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
from string import punctuation


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
        print(messages[N - i - 1].channel.name != orig_message.channel.name)
        if messages[N - i - 1].channel.name != orig_message.channel.name:
            i += 1
            continue
        print('thisAttch =', messages[N - i - 1].attachments)
        if len(messages[N - i - 1].attachments) != 0:
            msg_to_decode = messages[N - i - 1]
            attch = True
            break
        print('thisEmbed =', messages[N - i - 1].embeds)
        if len(messages[N - i - 1].embeds) != 0:
            if messages[N - i - 1].embeds[0]['url'][3:] in ['png', 'jpg', 'peg']:
                msg_to_decode = self.ntsk.messages[N - i - 1]
                embed = True
                break
        i += 1
        j += 1
    print(msg_to_decode, attch, embed)
    return msg_to_decode, attch, embed  # change attach/embed to single var?
