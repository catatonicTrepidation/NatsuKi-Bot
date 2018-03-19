#!/usr/bin/env python3.5
# coding=utf-8

import discord
import json
import sqlite_broker
import sql_setup
import re

import random

pfx = "~"


rand_responses = [

    "Hey~",
    "♡",
    "Want to, um, read some manga..?",
    "W-What do you want?",
    "Well, I am a pro.",
    "ニャ〜！"

]


class ResponseGenerator:

    def __init__(self, ntsk):
        self.ntsk = ntsk

    #self.usrMentionPattern = re.pattern('<@!?')

    async def get_predefined_response(self):
        """
        Get random, predefined response
        :return: response as string
        """
        r = random.randrange(len(rand_responses))
        return rand_responses[r]

    async def gen_custom_response(self, msg, *args):
        """
        Generate custom response [not yet implemented]
        :param msg: message object that mentioned NatsuKi
        :param args: remainder of message
        :return: custom response as string(?) [not yet implemented]
        """
        await self.ntsk.send_file(msg.channel, "images/warning/NotImplemented.png", filename="NotImplemented.png")
        print("Functionality not yet implemented")


#pen = CommandPen(None)
#pen.take_command('`count')
