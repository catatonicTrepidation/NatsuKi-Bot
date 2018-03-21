#!/usr/bin/env python3.5
# coding=utf-8

import discord
import json
import sqlite_broker
import re

from gen_responses import ResponseGenerator
from util import *
from data.character_query import CharacterQuery



#import people


pfx = "~"


class MentionReact:

    def __init__(self, ntsk):
        self.ntsk = ntsk
        self.respGenerator = ResponseGenerator(ntsk)
        self.charQuery = CharacterQuery()

        #self.usrMentionPattern = re.pattern('<@!?')

    async def take_mention(self, msg, *args):
        """
        Handles messages that mention NatsuKi
        :param msg: message object with mention
        :param args: string of message's content
        :return:
        """
        if len(args) == 0:
            return 0
        if len(args) > 1:
            print('valid bow message =',valid_bow_message(msg.content))
            if contains_curse_word(msg.content):
                await self.ntsk.delete_message(msg)
                chastice_message = await self.respGenerator.get_chastice_response(msg.author.id, msg.server.id)
                await self.ntsk.send_message(msg.channel, chastice_message)
                await self.charQuery.update_score(-5, msg.author.id, msg.server.id, absolute=True)
            elif valid_bow_message(msg.content):
                praise_message = await self.respGenerator.get_praise_response(msg.author.id, msg.server.id)
                await self.ntsk.send_message(msg.channel, praise_message)
                await self.charQuery.update_score(3, msg.author.id, msg.server.id, absolute=True)
        else:
            #todo: add random wait before sending (implement start_typing()?)
            resp = await self.respGenerator.get_predefined_response(msg.author.id, msg.server.id)
            await self.ntsk.send_message(msg.channel, resp)