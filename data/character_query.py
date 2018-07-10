#!/usr/bin/python
# -*- coding: utf-8 -*-

import discord
import sqlite3 as lite
import sys
import random
import json

pfx = "~"


class CharacterQuery:

    def __init__(self):
        self.last_query = None

    async def add_character(self, char_id, server_id):
        data_path = 'data/databases/%s/characters.json' % (server_id,)
        char_data = json.load(open(data_path))
        char_data['characters'][char_id] = {'ntskpoints' : 0, 'quote' : "", "serverpoints" : 0}

    async def get_character_data(self, char_id, field, server_id):
        data_path = 'data/databases/%s/characters.json' % (server_id,)
        with open(data_path, "r+") as chars_file:
            char_data = json.load(chars_file)
            if char_id in char_data['characters']:
                return char_data['characters'][char_id][field]
            return None

    async def set_character_data(self, new_data, char_id, field, server_id):
        data_path = 'data/databases/%s/characters.json' % (server_id,)
        with open(data_path, "r+") as chars_file:
            char_data = json.load(chars_file)
            char_data['characters'][char_id][field] = new_data
            chars_file.seek(0)
            json.dump(char_data, chars_file)
            chars_file.truncate()

    async def get_quote(self, char_id, server_id):
        data_path = 'data/databases/%s/characters.json' % (server_id,)
        with open(data_path, "r+") as chars_file:
            char_data = json.load(chars_file)
            if char_id in char_data['characters']:
                return char_data['characters'][char_id]['quote']
            return None


    async def set_quote(self, quote, char_id, server_id):
        await self.set_character_data()

    async def update_score(self, dp, char_id, server_id, absolute=False):
        data_path = 'data/databases/%s/characters.json' % (server_id,)
        with open(data_path, "r+") as chars_file:
            char_data = json.load(chars_file)
            cur_score = char_data['characters'][char_id]['ntskpoints']
            print('cur_score for %s =' % (char_id,),cur_score)
            if absolute:
                char_data['characters'][char_id]['ntskpoints'] = max(cur_score + dp, 5)
            else:
                char_data['characters'][char_id]['ntskpoints'] = cur_score + dp
            chars_file.seek(0)
            json.dump(char_data, chars_file)
            chars_file.truncate()

    async def update_points(self, dp, char_id, server_id, absolute=False):
        data_path = 'data/databases/%s/characters.json' % (server_id,)
        with open(data_path, "r+") as chars_file:
            char_data = json.load(chars_file)
            cur_score = char_data['characters'][char_id]['serverpoints']
            print('cur_score for %s =' % (char_id,),cur_score)
            if absolute:
                char_data['characters'][char_id]['serverpoints'] = max(cur_score + dp, 5)
            else:
                char_data['characters'][char_id]['serverpoints'] = cur_score + dp
            chars_file.seek(0)
            json.dump(char_data, chars_file)
            chars_file.truncate()

    async def get_points(self, char_id, server_id):
        data_path = 'data/databases/%s/characters.json' % (server_id,)
        with open(data_path, "r") as chars_file:
            char_data = json.load(chars_file)
            return char_data['characters'][char_id]['serverpoints']