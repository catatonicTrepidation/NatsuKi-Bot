#!/usr/bin/env python3.5
# coding=utf-8

import discord
import random
from data.character_query import CharacterQuery
from data.data_holder import getResponseList

pfx = "~"





class ResponseGenerator:

    def __init__(self, ntsk):
        self.ntsk = ntsk
        self.charQuery = CharacterQuery()
    #self.usrMentionPattern = re.pattern('<@!?')

    async def get_predefined_response(self, char_id, server_id):
        """
        Get random, predefined response
        :return: response as string
        """
        char_score = await self.charQuery.get_character_data(char_id, 'ntskpoints', server_id)
        idx = max(0, min(char_score//10, 2))
        resp_list = getResponseList(idx)
        r = random.randrange(len(resp_list))
        return resp_list[r]

    async def get_chastice_response(self, char_id, server_id):
        chastice_message = "Hey! No naughty words!!"
        char_score = await self.charQuery.get_character_data(char_id, 'ntskpoints', server_id)
        if char_score > 20:
            chastice_message += " ...I expected better from you... :/"
        return chastice_message

    async def get_praise_response(self, char_id, server_id):
        char_score = await self.charQuery.get_character_data(char_id, 'ntskpoints', server_id)
        if char_score > 20:
            return "D'aww! ^_^"
        if char_score > 10:
            return "Well, thank you." # REPLACE THIS WITH RANDOM FROM GOOD_STANDING_RESPONSES DATABASE
        return "Hmph. About time you learn your place."


    async def gen_custom_response(self, msg, *args):
        """
        Generate custom response [not yet implemented]
        :param msg: message object that mentioned NatsuKi
        :param args: remainder of message
        :return: custom response as string(?) [not yet implemented]
        """
        await self.ntsk.send_file(msg.channel, "data/images/error/NotImplemented.png", filename="NotImplemented.png")
        print("Functionality not yet implemented")


#pen = CommandPen(None)
#pen.take_command('`count')
