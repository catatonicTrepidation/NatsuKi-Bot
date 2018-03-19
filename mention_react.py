#!/usr/bin/env python3.5
# coding=utf-8

import discord
import json
import sqlite_broker
import re


from util import *
from gen_responses import *

#import people


pfx = "~"


class MentionReact:

    def __init__(self, ntsk):
        self.ntsk = ntsk
        self.respGenerator = ResponseGenerator(ntsk)

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
        elif len(args) == 1:
            resp = await self.respGenerator.get_predefined_response()
            await self.ntsk.send_message(msg.channel, resp)
        elif contains_curse_word(msg.content):
            await self.ntsk.delete_message(msg)
            await self.ntsk.send_message(msg.channel, "Hey! No naughty words!!")
            # players[msg.author.id].penalty += 1

        else:
            #todo: add random wait before sending (implement start_typing()?)
            resp = await self.respGenerator.get_predefined_response()
            await self.ntsk.send_message(msg.channel, resp)