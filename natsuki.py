#!/usr/bin/env python3.5
# coding=utf-8

import discord
import sqlite_broker
import json
from command_pen import *
from mention_react import *
import data.sql_setup

import random

config_data = json.load(open('data/config.json'))

pfx = '~'


class Natsuki(discord.Client):

    async def on_ready(self):
        self.pen = CommandPen(self)
        self.mentionReact = MentionReact(self)
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.author.bot:
            return
        print('Message from {0.author}: {0.content} {0.server.id}'.format(message))

        if message.content == '~leaveserver':
            print('which server?')
            if message.server.id == '425418182329892866':
                print('correct server!')
                await ntsk.leave_server(message.server)


        if message.channel.name == "word-heist":  # change to channel ID
            if not sqlite_broker.add_unique_words(message):
                await ntsk.delete_message(message)
                if random.randrange(100) == 1:
                    await ntsk.send_message(message.channel, "You've already used that word, you dope! >_<")

        content_list = message.content.split(' ')
        if not message.content:
            return
        if message.content[0] == pfx:
            await self.pen.take_command(message, *content_list)
        else:
            sqlite_broker.add_message("messages", message)

            if ntsk.user.mentioned_in(message):
                await self.mentionReact.take_mention(message, *content_list)

    async def on_server_join(self, server):
        print('JOINED SERVER!!!')
        data.sql_setup.initialize_databases(server)


ntsk = Natsuki()
ntsk.run(config_data['token'])
