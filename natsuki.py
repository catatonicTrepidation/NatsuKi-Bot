#!/usr/bin/env python3.5
# coding=utf-8

import discord
import sqlite_broker
import json
from command_pen import *
from mention_react import MentionReact
import emojihunt
import data.data_setup

import random

config_data = json.load(open('data/config.json','r',encoding="utf-8_sig"))

pfx = '~'


class Natsuki(discord.Client):

    async def on_ready(self):
        self.pen = CommandPen(self)
        self.mentionReact = MentionReact(self)
        # self.emojiHunt = emojihunt.EmojiHunt(ntsk)
        # await self.emojiHunt.main_loop()
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.author.bot:
            return
        print('Message from {0.author}: {0.content} {0.server.id}'.format(message))

        if message.channel.name == "word-heist":  # change to channel ID
            if not sqlite_broker.add_unique_words(message):
                await ntsk.delete_message(message)
                if random.randrange(100) == 1:
                    await ntsk.send_message(message.channel, "You've already used that word, you dope! >_<")

        content_list = message.content.split(' ')

        if  message.content:
            if message.content[0] == pfx:
                await self.pen.take_command(message, *content_list)
                return
            else:
                if ntsk.user.mentioned_in(message):
                    await self.mentionReact.take_mention(message, *content_list)
        sqlite_broker.add_message("messages", message)

    async def on_reaction_add(self, reaction, user):
        if user == ntsk.user:
            return

        if reaction.message.author.bot:
            await self.pen.take_reaction(reaction, user)

    async def on_server_join(self, server):
        print('JOINED SERVER!!!')
        data.data_setup.initialize_databases(server)


ntsk = Natsuki()
ntsk.run(config_data['token'])
