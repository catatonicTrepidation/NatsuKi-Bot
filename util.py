#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
from string import punctuation


def contains_curse_word(sentence):
    sentence = sentence.lower()
    translator = str.maketrans('', '', punctuation)
    sentence = sentence.translate(translator)
    print('sentence =',sentence)
    with open('react/bad_words.txt', errors="ignore") as f:
        word = f.readline()[:-1]
        while word:
            if word in sentence:
                return True
            word = f.readline()[:-1]
    return False

def detect_image(messages):
    N = len(messages)
    msg_to_decode = None
    attch = embed = False
    for i in range(min(20, N)):
        print('thisAttch =',messages[N - i - 1].attachments)
        if len(messages[N - i - 1].attachments) != 0:
            msg_to_decode = messages[N - i - 1]
            attch = True
            break
        print('thisEmbed =',messages[N - i - 1].embeds)
        if len(messages[N - i - 1].embeds) != 0:
            if messages[N - i - 1].embeds[0]['url'][3:] in ['png', 'jpg', 'peg']:
                msg_to_decode = self.ntsk.messages[N - i - 1]
                embed = True
                break
    print(msg_to_decode, attch, embed)
    return msg_to_decode, attch, embed