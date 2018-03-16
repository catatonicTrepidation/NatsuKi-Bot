#!/usr/bin/env python3.5
# coding=utf-8

import discord
import json
import sqlite_broker
import sql_setup
import re


from imgclasses.binaryimage import *
import data_holder



pfx = "~"


# "Well, not everyone can be a pro like me..."


COMMANDS_STR = data_holder.getCommandsString()


class CommandPen:

    def __init__(self, ntsk):
        self.ntsk = ntsk
        self.f_dict = dict()

        self.f_dict[pfx + 'info'] = self.display_info
        self.f_dict[pfx + 'commands'] = self.commands

        self.f_dict[pfx + 'count'] = self.db_count
        self.f_dict[pfx + 'qr'] = self.create_qr
        self.f_dict[pfx + 'bin'] = self.encode_bin
        self.f_dict[pfx + 'unbin'] = self.decode_bin

        self.f_dict[pfx + '😂'] = self.ok_hand

        self.f_dict[pfx + '!db'] = self.do_nothing
        self.f_dict[pfx + '!inspire'] = self.do_nothing
        self.f_dict[pfx + '!info'] = self.do_nothing

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

    async def encode_bin(self, msg, *args):
        print('msg =',msg)
        print('args =',args)
        if len(*args) == 1:
            await self.ntsk.send_message(msg.channel, "`【！️】You need to include some text, silly【！️】`")
            return False
        text = ' '.join(args[0][1:])
        binImg = BinaryImage(text)
        success = await binImg.create_image()
        if success:
            await self.ntsk.send_file(msg.channel, 'output/images/binimage.png', filename='binimage.png')
        else:
            await self.ntsk.send_message(msg.channel, "`【？️】Something went wrong...\nPlease use UTF-8 characters only【？️】`")
        #return False or True?

    async def decode_bin(self, msg, *args): # txtfile=False
        binImg = BinaryImage(None)
        decoded_text = None
        if len(msg.attachments) != 0:
            error, restricted, decoded_text = await binImg.decode_image(msg)
        else:
            msg_to_decode = None
            for i in range(min(10, len(self.ntsk.messages))):
                print(self.ntsk.messages[i].attachments)
                if len(self.ntsk.messages[i].attachments) != 0:
                    msg_to_decode = self.ntsk.messages[i]

            if not msg_to_decode:
                print("Couldn't find any images to decode!")
                return False

            error, restricted, decoded_text = await binImg.decode_image(msg_to_decode)

        if error:
            await self.ntsk.send_message(msg.channel, "Oops! There was an error... :(")
        elif restricted:
            await self.ntsk.send_message(msg.channel, "H-Hey!! This is private! >_<")
        else:
            await self.ntsk.send_message(msg.channel, decoded_text)
        return not restricted


    async def create_qr(self, msg, *args):
        await self.ntsk.send_file(msg.channel, "images/warning/NotImplemented.png", filename="NotImplemented.png")
        print("QR not yet implemented")

    async def commands(self, msg, *args):
        await self.ntsk.send_message(msg.channel, COMMANDS_STR)

    async def display_info(self, msg, *args):
        if random.randrange(10) == 0:
            # config_data['weight'] etc exceot don't make it config_data
            print('say something awkward, delay, then post info')

        await self.ntsk.send_message(msg.channel, embed=data_holder.getGithubEmbed())

    async def ok_hand(self, msg, *args):
        await self.ntsk.send_message(msg.channel, '👌')

    async def do_nothing(self, msg, *args):
        print('ree, Spock-san~')


#pen = CommandPen(None)
#pen.take_command('`count')
