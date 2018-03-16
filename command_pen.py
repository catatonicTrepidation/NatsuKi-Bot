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
COMMANDS_STR = "```hs\n" + COMMANDS_STR + "\n```"


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

    async def encode_bin(self, msg, *args): # txtfile=False, author = False, Recipient = False
        """
        Encodes text as binary image
        :param msg: Message object whose text should be encoded
        :param args: <text file>, <author>, <specified recipient>, <remaining text>
        :return:
        """
        print('msg =',msg)
        print('args =',args)
        if len(*args) == 1:
            await self.ntsk.send_message(msg.channel, "`【！️】You need to include some text, silly【！️】`")
            return False

        start = 1
        img_author = None
        img_recipient = None

        print('args[0][1] =',args[0][1])

        bool_strings = ['true','false']


        if args[0][1].lower() in bool_strings:
            img_author = msg.author.id
            start = 2

        if start == 1 or len(args[0]) > 2:
            try:
                print(args[0][start])
                usr = await self.ntsk.get_user_info(args[0][start])
                img_recipient = usr.id
                start += 1
            except:
                translator = str.maketrans('', '', '<@!>')
                x = args[0][start].translate(translator)
                if x in msg.raw_mentions:
                    img_recipient = x
                    start += 1

        if len(args[0]) <= start:
            await self.ntsk.send_message(msg.channel, "`【！️】You need to include some text, silly【！️】`")
            return False


        text = ' '.join(args[0][start:])
        binImg = BinaryImage(text)
        success = await binImg.create_image(img_author, img_recipient)
        if success:
            await self.ntsk.send_file(msg.channel, 'output/images/binimage.png', filename='binimage.png')
        else:
            await self.ntsk.send_message(msg.channel, "`【？️】Something went wrong...\nPlease use UTF-8 characters only【？️】`")
        #return False or True?

    async def decode_bin(self, msg, *args): # txtfile=False
        binImg = BinaryImage(None)
        decoded_text = None
        embed = attch = False
        msg_to_decode = None
        if len(msg.attachments) != 0:
            msg_to_decode = msg
            attch = True
        elif len(msg.embeds) != 0:
            print("msg.embeds[0]['url'][-3:] =",msg.embeds[0]['url'][-3:])
            if msg.embeds[0]['url'][-3:] in ['png', 'jpg']:
                msg_to_decode = msg
                embed = True
        else:
            N = len(self.ntsk.messages)
            for i in range(min(10, N)):
                print(self.ntsk.messages[N-i-1].attachments)
                if len(self.ntsk.messages[N-i-1].attachments) != 0:
                    msg_to_decode = self.ntsk.messages[N-i-1]
                    attch = True
                    break
                if len(self.ntsk.messages[N-i-1].embeds) != 0:
                    print("self.ntsk.messages[N-i-1].embeds[0]['url'][-3:] =", self.ntsk.messages[N-i-1].embeds[0]['url'][-3:])
                    if self.ntsk.messages[N-i-1].embeds[0]['url'][-3:] in ['png','jpg']:
                        print('trueee',self.ntsk.messages[N-i-1].content)
                        msg_to_decode = self.ntsk.messages[N-i-1]
                        embed = True
                        break

            if not msg_to_decode:
                print("Couldn't find any images to decode!")
                return False

            # GET IMG URL HERE
            if attch:
                download.download_image(msg_to_decode.attachments[0]['url'], "downloaded/images/imgtodecode.png")
            elif embed:
                download.download_image(msg_to_decode.embeds[0]['url'], "downloaded/images/imgtodecode.png")
            # catch error ()

        error, restricted, decoded_text = await binImg.decode_image("downloaded/images/imgtodecode.png", msg) # decode image

        if error:
            await self.ntsk.send_message(msg.channel, "Oops! There was an error... TT_TT")
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
