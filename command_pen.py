#!/usr/bin/env python3.5
# coding=utf-8

import discord
import json
import sqlite_broker
from data.data_setup import get_con
import re


from imgclasses.binaryimage import *
import data.data_holder
import data.data_setup
import data.character_query
import data.data_query
import score_react
import util


pfx = "~"


# "Well, not everyone can be a pro like me..."


COMMANDS_STR = data.data_holder.getCommandsString()
COMMANDS_STR = "```hs\n" + COMMANDS_STR + "\n```"


class CommandPen:

    def __init__(self, ntsk):
        self.ntsk = ntsk
        self.CharQuery = data.character_query.CharacterQuery()
        self.scoreReact = score_react.ScoreReact()
        self.f_dict = dict()

        self.f_dict[pfx + 'info'] = self.display_info
        self.f_dict[pfx + 'commands'] = self.commands

        self.f_dict[pfx + 'count'] = self.db_count
        self.f_dict[pfx + 'stats'] = self.display_top_words

        self.f_dict[pfx + 'bin'] = self.encode_bin
        self.f_dict[pfx + 'unbin'] = self.decode_bin
        self.f_dict[pfx + 'qr'] = self.create_qr

        self.f_dict[pfx + 'setquote'] = self.set_quote
        self.f_dict[pfx + 'quote'] = self.get_quote
        self.f_dict[pfx + 'score'] = self.display_score

        self.f_dict[pfx + '😂'] = self.ok_hand
        self.f_dict[pfx + 'yuri'] = self.yuri

        self.f_dict[pfx + '!db'] = self.do_nothing
        self.f_dict[pfx + '!inspire'] = self.do_nothing
        self.f_dict[pfx + '!info'] = self.do_nothing

        self.f_dict[pfx + 'initdata'] = self.init_data
        self.f_dict[pfx + 'leaveserver'] = self.leave_server

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
        con = get_con('messages', msg.server.id)
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
                SQLQuery += "UserId = " + target_usr

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

        if len(*args) == 1:
            await self.ntsk.send_message(msg.channel, "`【！️】You need to include some text, silly【！️】`")
            return False

        start = 1
        img_author = None
        img_recipient = None

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
        success = await binImg.create_image(msg.server.id, img_author, img_recipient)
        if success:
            await self.ntsk.send_file(msg.channel,
                            'data/databases/%s/output/images/binimage.png' % (msg.server.id), filename='binimage.png')
        else:
            await self.ntsk.send_message(msg.channel, "`【？️】Something went wrong...\nPlease use UTF-8 characters only【？️】`")
        #return False or True?

    async def decode_bin(self, msg, *args): # txtfile=False
        binImg = BinaryImage(None)

        msg_to_decode, attch, embed = util.detect_image([msg] + list(self.ntsk.messages))

        if not msg_to_decode:
            print("Couldn't find any images to decode!")
            return

        download_path = 'data/databases/%s' % (msg.server.id,) + '/downloaded/images/imgtodecode.png'
        if attch:
            download.download_image(msg_to_decode.attachments[0]['url'], download_path)
        elif embed:
            download.download_image(msg_to_decode.embeds[0]['url'], download_path)
        # catch error ()

        error, restricted, decoded_text = await binImg.decode_image(download_path, msg.author.id) # decode image

        if error:
            await self.ntsk.send_message(msg.channel, "Oops! There was an error... TT_TT")
        elif restricted:
            await self.ntsk.send_message(msg.channel, "H-Hey!! This is private! >_<")
        else:
            await self.ntsk.send_message(msg.channel, decoded_text)
        return not restricted


    async def create_qr(self, msg, *args):
        await self.ntsk.send_file(msg.channel, "data/images/error/NotImplemented.png", filename="NotImplemented.png")
        print("QR not yet implemented")

    async def set_quote(self, msg, *args):
        quote = ' '.join(args[0][1:])
        await self.CharQuery.set_character_data(quote, msg.author.id, 'quote', msg.server.id)
        await self.ntsk.send_message(msg.channel, "Quote set~!")

    async def get_quote(self, msg, *args):
        quote = await self.CharQuery.get_character_data(msg.author.id, 'quote', msg.server.id)
        await self.ntsk.send_message(msg.channel, quote)

    async def display_score(self, msg, *args):
        score_display_msg = await self.scoreReact.check_score(msg.author.id, msg.server.id)
        await self.ntsk.send_message(msg.channel, score_display_msg)

    async def display_top_words(self, msg, *args):
        top_words = await data.data_query.get_top_words(msg, 20, *args)
        top_words = "```fix\n" + '\n'.join(top_words) + "\n```"
        await self.ntsk.send_message(msg.channel, top_words)

    async def commands(self, msg, *args):
        await self.ntsk.send_message(msg.author, COMMANDS_STR)

    # make !help <command> function
    # document functions

    async def display_info(self, msg, *args):
        if random.randrange(10) == 0:
            # config_data['weight'] etc except don't make it config_data
            print('say something awkward, delay, then post info')
        await self.ntsk.send_message(msg.channel, embed=data.data_holder.getGithubEmbed())

    async def init_data(self, msg, *args):
        if msg.author.id == '232904019415269377':
            data.data_setup.initialize_databases(msg.server)
        else:
            await self.ntsk.send_message(msg.channel, "Unknown command! `" + pfx + "commands` if you can't figure it out...")

    async def ok_hand(self, msg, *args):
        await self.ntsk.send_message(msg.channel, '👌')

    async def yuri(self, msg, *args):
        await self.ntsk.send_file(msg.channel, 'data/images/reactions/natsuvomit.png')

    async def do_nothing(self, msg, *args):
        print('ree, Spock-san~')

    async def leave_server(self, msg, *args):
        if msg.author.id == '232904019415269377':
            await ntsk.leave_server(msg.server)
        else:
            await self.ntsk.send_message(msg.channel, "Unknown command! `" + pfx + "commands` if you can't figure it out...")