#!/usr/bin/env python3.5
# coding=utf-8

import discord
import json
import sqlite_broker
import re

from util import *
from data.character_query import CharacterQuery



#import people


pfx = "~"


class ScoreReact:

    def __init__(self):
        self.charQuery = CharacterQuery()

        #self.usrMentionPattern = re.pattern('<@!?')

    async def check_score(self, char_id, server_id):
        char_score = await self.charQuery.get_character_data(char_id, 'ntskpoints', server_id)
        resp = ""
        if char_score > 20:
            resp = "We're buddies~ ♡"
        elif char_score > 10:
            resp = "You're alright, I guess..."
        else:
            resp = "Bleugh. Get away."
        resp += " [%s]" % (char_score,)
        return resp
