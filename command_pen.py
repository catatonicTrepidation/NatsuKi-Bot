#!/usr/bin/env python3.5
# coding=utf-8

import discord
import json
import sqlite_broker
import sql_setup
import re

from imgclasses.binaryimage import *



pfx = "~"


def formatCmdDesc(cmd, params, desc):
    return '{message:{fill}{align}}'.format(
            message="`" + pfx + cmd + "` " + params, fill=' ',align='<90') + " :: " + desc



COMMANDS_DICT = {pfx + "count":formatCmdDesc("count","<text> [channel] [user] [.like]","Get number of messages in database"),
            pfx + "commands":formatCmdDesc("commands","","Get list of commands🖊"),
            pfx + "qr":formatCmdDesc("qr","[text]","Turn text into QR code")}

COMMANDS_DICT = {
                pfx + "count"    : "`" + pfx + "count` <text> [channel] [user] [.like] :: Get number of messages in database",
                pfx + "commands" : "`" + pfx + "commands`                                                   :: Get list of commands🖊",
                pfx + "qr"       : "`" + pfx + "qr` [text]                                                     :: Turn text into QR code"
                }


CMD_LEGEND = "*Legend: <> specifies required arguments, [] specifies optional arguments*"

COMMANDS_STR = ""
for cmd, desc in COMMANDS_DICT.items():
    COMMANDS_STR += desc + "\n"

               # "```\n" + ... + "```
COMMANDS_STR = CMD_LEGEND + "\n\n" + COMMANDS_STR





class CommandPen:

    def __init__(self, ntsk):
        self.ntsk = ntsk
        self.f_dict = dict()
        self.f_dict[pfx + 'count'] = self.db_count
        self.f_dict[pfx + 'commands'] = self.commands
        self.f_dict[pfx + 'qr'] = self.create_qr
        self.f_dict[pfx + 'bin'] = self.create_bin

        self.f_dict[pfx + '😂'] = self.ok_hand

        self.f_dict[pfx + '!db'] = self.do_nothing
        self.f_dict[pfx + '!inspire'] = self.do_nothing

        #self.usrMentionPattern = re.pattern('<@!?')

    async def take_command(self, msg, *args):
        print('args =',args)
        if len(args) == 0:
            return 0
        else:
            if args[0] in self.f_dict:
                await self.f_dict[args[0]](msg, args)
                return 1
            await self.ntsk.send_message(msg.channel, "Unknown command! `" + pfx + "commands` if you can't figure it out...")
            print("Unknown command! ~commands if you can't figure it out...")

    async def db_count(self, msg, *args): # sort arguments? that way the @mentions will all come after db_name
        con = sql_setup.get_con('messages')
        cur = con.cursor()
        num_msgs = 0
        print('args =',*args)
        SQLQuery = "SELECT count(*) FROM " + 'messages'
        if len(*args) == 1:
            cur.execute(SQLQuery)
            num_msgs = cur.fetchall()[0][0]
            await self.ntsk.send_message(msg.channel, str(num_msgs) + " messages logged~")
            print(str(num_msgs) + " messages logged~")
        else:

            params = list(args[0])[1:]
            like = False
            usr_mention = False
            target_usr = '%'
            chn_mention = False
            target_chn_name = '%'
            target_chn_id = '%'
            msgQuery = ''

            if len(msg.raw_mentions) != 0:
                usr_mention = True
                target_usr = msg.raw_mentions[0]
            if len(msg.channel_mentions) != 0:
                chn_mention = True
                target_chn_name = msg.channel_mentions[0].name
                target_chn_id = msg.channel_mentions[0].id
            for p in params:
                if not like and p == '.like':
                    like = True
                    continue
                if usr_mention and p == '<@' + target_usr + '>' or p == '<@!' + target_usr + '>':
                    continue
                if chn_mention and p == '<#' + target_chn_id + '>' or p == '<#!' + target_chn_id + '>':
                    continue
                msgQuery += p + ' '
            msgQuery = msgQuery[:-1]

            print('params =',params)
            print('raw_mentions =',msg.raw_mentions)
            print('channel_mentions =',msg.channel_mentions)

            equals = 'LIKE' if like else '='
            op = '%' if like else ''

            MQ = False
            if msgQuery != '':
                MQ = True
                SQLQuery += " WHERE Content " + equals + ' ' + "'" + op + msgQuery + op + "'"

            if usr_mention:
                if MQ:
                    SQLQuery += " AND "
                else:
                    SQLQuery += " WHERE "
                SQLQuery += "Username = " + target_usr

            if chn_mention:
                if MQ or usr_mention:
                    SQLQuery += " AND "
                else:
                    SQLQuery += " WHERE "
                SQLQuery += "Channel = " + "'" + target_chn_name + "'"

            print('SQLQuery =',SQLQuery)
            cur.execute(SQLQuery)
            num_msgs = cur.fetchall()[0][0]
            await self.ntsk.send_message(msg.channel, str(num_msgs) + " messages matched your query!")

    async def create_bin(self, msg, *args):
        print('msg =',msg)
        print('args =',args)
        binImg = BinaryImage(msg.content)
        await binImg.create_image()
        await self.ntsk.send_file(msg.channel, 'output/binimage.png', filename='binimage.png')

    async def create_qr(self, msg, *args):
        await self.ntsk.send_file(msg.channel, "images/warning/NotImplemented.png", filename="NotImplemented.png")
        print("QR not yet implemented")

    async def commands(self, msg, *args):
        await self.ntsk.send_message(msg.channel, COMMANDS_STR)

    async def ok_hand(self, msg, *args):
        await self.ntsk.send_message(msg.channel, '👌')

    async def do_nothing(self, msg, *args):
        print('ree, Spock-san~')


#pen = CommandPen(None)
#pen.take_command('`count')
