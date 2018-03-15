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