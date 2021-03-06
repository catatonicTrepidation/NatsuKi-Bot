#!/usr/bin/env python3.5
# coding=utf-8

import discord
import json
import sqlite_broker
from data.data_setup import get_con
import re
import sched
import asyncio
import time


from imgclasses.binaryimage import *
import data.data_holder
import data.data_setup
import data.character_query
import data.data_query
import data.danbooru_request
import data.danbooru_query
import google_search
import score_react
import encrypt
import translate
import log_drawer
import text_automata
import trivia
import timer
#import emojihunt
import kanji_quiz
import ateji_to_word
import util


pfx = "~"


# "Well, not everyone can be a pro like me..."


COMMANDS_STR = data.data_holder.getCommandsString()
COMMANDS_STR = "```hs\n" + COMMANDS_STR + "\n```"

DANBO_CONTROLS_EMOJI = {":left_arrow:" : -1, ":right_arrow:" : 1}


class CommandPen:

    def __init__(self, ntsk):
        self.ntsk = ntsk
        self.CharQuery = data.character_query.CharacterQuery()
        self.scoreReact = score_react.ScoreReact()
        self.messageEncryptor = encrypt.Encryptor()
        self.kanjiQuiz = kanji_quiz.KanjiQuiz()
        self.googleSearcher = google_search.googleimagesdownload()
        self.searchArgs = {"keywords": "neko", "safe_search": False, "metadata": False, "limit": 5,
                 "no_directory": True, "output_directory": "birdy", "keywords_from_file" : None, "size":None, "format": None,
                 "time":None, "time_range":None, 'suffix_keywords':None, 'prefix_keywords':None,'url':None, 'similar_images':None,'specific_site':None,
                 'single_image':None,'proxy':None,'image_directory':None,'thumbnail':None,'language':None,'exact_size':None,
                 'color':None,'color_type':None,'usage_rights':None,'type':None,'aspect_ratio':None,'offset':None}


        danbooru_config = json.load(open('data/config.json','r',encoding="utf-8_sig"))
        self.danbooruRequest = data.danbooru_request.DanbooruRequest(danbooru_config['danbooru_user'], danbooru_config['danbooru_key'])
        self.danbooruQuery = data.danbooru_query.DanbooruQuery(servers=list(map(lambda s : s.id, self.ntsk.servers)))
        self.timerHolder = timer.TimerHolder(servers=list(map(lambda s : s.id, self.ntsk.servers)))
        self.atejiMatcher = ateji_to_word.AtejiMatcher()
        #self.timerHolder = timer_holder.TimerHolder() # holds timers for each server, each with info on the user who created it, etc...
        #self.scheduler = sched.scheduler() # scheduler(time.time, time.sleep) implied ((wow, asyncio.sleep() seems good for now))

        self.f_dict = dict()

        self.f_dict[pfx + 'info'] = self.display_info
        self.f_dict[pfx + 'commands'] = self.get_commands

        self.f_dict[pfx + 'count'] = self.db_count
        self.f_dict[pfx + 'stats'] = self.display_top_words
        self.f_dict[pfx + 'logs'] = self.get_logs


        self.f_dict[pfx + 'bin'] = self.encode_bin
        self.f_dict[pfx + 'unbin'] = self.decode_bin
        self.f_dict[pfx + 'qr'] = self.create_qr
        self.f_dict[pfx + 'enc'] = self.get_encryption
        self.f_dict[pfx + 'dec'] = self.get_decryption

        self.f_dict[pfx + 'trans'] = self.translate

        self.f_dict[pfx + 'danbo'] = self.post_danbooru
        self.f_dict[pfx + 'google'] = self.google_images
        self.f_dict[pfx + 'vgoogle'] = self.google_videos

        self.f_dict[pfx + 'setquote'] = self.set_quote
        self.f_dict[pfx + 'quote'] = self.get_quote

        self.f_dict[pfx + 'points'] = self.show_points

        self.f_dict[pfx + 'automata'] = self.automata
        self.f_dict[pfx + 'trivia'] = self.ask_trivia
        self.f_dict[pfx + 'kanji'] = self.ask_kanji_quiz

        self.f_dict[pfx + 'kmatch'] = self.match_ateji

        self.f_dict[pfx + 'futuresay'] = self.future_say

        self.f_dict[pfx + 'matrix'] = self.matrix

        self.f_dict[pfx + 'lmgtfy'] = self.lmgtfy

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


    async def get_logs(self, msg, *args):
        params = args[0][1:]
        if len(params) == 0:
            print('-default')
            #sqlquery.query_logs(msg.server.id, 10,
        rand_flag = None
        target_id = None
        start_idx = None
        img_flag = None
        num_msgs = 3

        if len(msg.raw_mentions) != 0:
            target_id = msg.raw_mentions[0]
            num_msgs = 1

        range_pat = re.compile(r'^-?[0-9]+:[0-9]+$')
        idx_pat = re.compile(r'^-?[0-9]+$')
        for p in params:
            if not target_id:
                try:
                    usr = await self.ntsk.get_user_info(params[1])
                    target_id = usr.id
                    num_msgs = 1
                    start_idx = None
                    break
                except:
                    print('param not usr')
                if p in ('.rand', '.random'):
                    rand_flag = True
                elif range_pat.match(p):
                    a, b = p.split(':')
                    start_idx = int(a)
                    num_msgs = int(b)
                    print(a,b,start_idx,num_msgs)
                elif idx_pat.match(p):
                    if rand_flag or start_idx:
                        num_msgs = int(p)
                    else:
                        start_idx = int(p)
                elif p in (".image", ".img"):
                    img_flag = True
            #if none of these things, return malformed command error? hmm

        result = None
        #img_flag=False
        if rand_flag:
            print('-rand')
            success, result = await data.data_query.rand_query(msg.server.id, target_id, num_msgs, img_flag)
        else:
            print('-specific')
            success, result = await data.data_query.id_query(msg.server.id, start_idx, num_msgs, img_flag)

        if not img_flag:
            result = await util.format_logs(result, self.ntsk.get_user_info)
            await self.ntsk.send_message(msg.channel, result)
        else:
            print('-image')
            prepped_logs = await util.prepare_for_image(result, self.ntsk.get_user_info)
            logs_img = log_drawer.draw_logs(prepped_logs)  # saved logs.jpg
            logs_img.save('data/databases/%s/downloaded/images/logs.jpg' % (msg.server.id,))
            await self.ntsk.send_file(msg.channel, 'data/databases/%s/downloaded/images/logs.jpg' % (msg.server.id,), filename="logs.jpg")
            #logs_img.save('data/' + str(msg.server.id) + '/downloaded/images/logs.jpg')
            #self.ntsk.send_file('data/' + str(msg.server.id) + '/downloaded/images/logs.jpg')

        #embed = embed(result)



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

    async def get_encryption(self, msg, *args):

        params = list(args[0])[1:]
        if len(params) == 0:
            await self.ntsk.send_message(msg.channel, "You can't encrypt nothing, silly~")
            return False

        e_idx = 1 # default is 1. i guess instead of having multiple N vals, we could just change the e vals lol
        if args[0][1][0] == ".":
            encryption_flag = args[0][1][1:]
            if encryption_flag in ["2", "3", "4", "5"]:
                e_idx = int(encryption_flag)
                params = params[1:]

        try:
            hex_text = await self.messageEncryptor.encrypt_message(' '.join(params), idxflag=e_idx)
            await self.ntsk.send_message(msg.channel, hex_text)
        except Exception as e:
            print(e)
            await self.ntsk.send_message(msg.channel, "I can't encrypt this..!!!!")

    async def get_decryption(self, msg, *args):

        params = list(args[0])[1:]
        if len(params) == 0:
            await self.ntsk.send_message(msg.channel, "You can't decrypt nothing, silly~")
            return False

        e_idx = 1 # default is 1. i guess instead of having multiple N vals, we could just change the e vals lol
        if args[0][1][0] == ".":
            encryption_flag = args[0][1][1:]
            if encryption_flag in ["2", "3", "4", "5"]:
                e_idx = int(encryption_flag)
                params = params[1:]

        try:
            dec_msg = await self.messageEncryptor.decrypt_message(' '.join(params), idxflag=e_idx)
            await self.ntsk.send_message(msg.channel, dec_msg)
        except Exception as e:
            print(e)
            await self.ntsk.send_message(msg.channel, "This is too hard to decrypt... :(")

    async def post_danbooru(self, msg, *args):
        params = (args[0])[1:]

        # check if space open
        embed_idx = self.timerHolder.find_free_space(msg.author.id, msg.server.id)
        if embed_idx == -1: # timers full
            print("Already at max num of timers!")
            await self.ntsk.send_message(msg.channel, "Already have three embeds... Give me a break......")
            return

        # decipher query
        query, is_private = await self.danbooruQuery.get_query_from_params(params)
        print('is_private =',is_private)
        # download danbooru info
        num_posts, error_message = self.danbooruRequest.download_danbooru_info(msg.server.id, embed_idx, query)
        if error_message:
            if error_message == "The database timed out running your query.":
                await self.ntsk.send_message(msg.channel, "Database timed out...")
            else:
                await self.ntsk.send_message(msg.channel, error_message)
            return False
        if num_posts == 0:
            await self.ntsk.send_message(msg.channel, "No results! Aww..")
            return False


        self.timerHolder.set_timer(msg.author.id, msg.server.id, embed_idx, wait_time=60) # move this to last, i think?

        # post danbooru posts
        self.danbooruQuery.embed_data[msg.server.id][embed_idx]["last_query"] = 0
        self.danbooruQuery.embed_data[msg.server.id][embed_idx]["num_posts"] = num_posts
        self.danbooruQuery.embed_data[msg.server.id][embed_idx]["private"] = is_private

        # get first post of query
        post_data = await self.danbooruQuery.get_post(msg.server.id, embed_idx)

        # set up embed with post data
        page_status = "%s/%s" % (1, num_posts)
        id_info = "id: %s" % (post_data['id'],)
        artist_info = "artist: %s" % (post_data["tag_string_artist"], )
        danbo_embed = discord.Embed(title=page_status, description=artist_info) #  description="No descriptions yet..." ['artist_commentary']
        if 'file_url' in post_data:
            danbo_embed.set_image(url=post_data['file_url'])
        else:
            danbo_embed.set_image(url='http://i68.tinypic.com/1kb9h.png')
        danbo_embed.set_footer(text=post_data['source'])

        embed_msg = await self.ntsk.send_message(msg.channel, embed=danbo_embed)

        # pair msg id with that embed in json file
        self.timerHolder.pair_msg_with_index(msg.server.id, embed_idx, embed_msg.id)

        # add left/right emoji to embed message
        await self.ntsk.add_reaction(embed_msg, '⬅')
        await self.ntsk.add_reaction(embed_msg, '➡')
        await self.ntsk.add_reaction(embed_msg, '🔼')
        await self.ntsk.add_reaction(embed_msg, '❌')

        print("i should've send a message")

        return True

    async def google_images(self, msg, *args):
        params = args[0]
        num_result_limit = 100
        lang = None
        safe_search = False
        page = 1
        # if not msg.channel.is_nsfw():
        #     safe_search = True
        keywords = []
        for p in params[1:]:
            if p.startswith('.lang=') or p.startswith('.language='):
                lang = p.split('=')[1]
            elif p == ('.safe'):
                safe_search = True
            elif p.startswith('.') and len(p) >= 2 and p[1:].isdigit() and int(p[1:]) < num_result_limit:
                page = int(p[1:])
            else:
                keywords.append(p)

        keywords = " ".join(keywords)
        self.searchArgs["keywords"] = keywords
        self.searchArgs["language"] = lang
        self.searchArgs["safe_search"] = safe_search
        image_objects = self.googleSearcher.download(self.searchArgs)
        print('len() =',len(image_objects))
        print(image_objects)
        await self.ntsk.send_message(msg.channel, image_objects[page-1]['image_link'])

    async def google_videos(self, msg, *args):
        params = args[0]
        lang = None
        safe_search = False
        # if not msg.channel.is_nsfw():
        #     safe_search = True
        keywords = []
        for p in params[1:]:
            if p.startswith('.lang=') or p.startswith('.language='):
                lang = p.split('=')[1]
            elif p == ('.safe'):
                safe_search = True
            else:
                keywords.append(p)

        keywords = " ".join(keywords)
        self.searchArgs["keywords"] = keywords
        self.searchArgs["language"] = lang
        self.searchArgs["safe_search"] = safe_search
        video_objects = self.googleSearcher.download_videos(self.searchArgs)

        await self.ntsk.send_message(msg.channel, video_objects[0])

        # async def google_images(self, msg, *args):
        #     params = (args[0])[1:]
        #
        #     # check if space open
        #     embed_idx = 0
        #     num_results = 0
        #     image_objects = []
        #     with open('data/databases/{}/google_embed_data.json'.format(msg.server.id),'w+',encoding='utf-8') as google_embed_data:
        #         embed_idx = google_embed_data['embed_idx']
        #         num_results = google_embed_data['num_results']
        #         image_objects = google_embed_data['image_objects']
        #
        #
        #     # post danbooru posts
        #     self.danbooruQuery.embed_data[msg.server.id][embed_idx]["last_query"] = 0
        #     self.danbooruQuery.embed_data[msg.server.id][embed_idx]["num_posts"] = num_posts
        #     self.danbooruQuery.embed_data[msg.server.id][embed_idx]["private"] = is_private
        #
        #     post_data
        #
        #     # set up embed with post data
        #     page_status = "%s/%s" % (1, num_posts)
        #     id_info = "id: %s" % (post_data['id'],)
        #     artist_info = "artist: %s" % (post_data["tag_string_artist"],)
        #     danbo_embed = discord.Embed(title=page_status,
        #                                 description=artist_info)  # description="No descriptions yet..." ['artist_commentary']
        #     if 'file_url' in post_data:
        #         danbo_embed.set_image(url=post_data['file_url'])
        #     else:
        #         danbo_embed.set_image(url='http://i68.tinypic.com/1kb9h.png')
        #     danbo_embed.set_footer(text=post_data['source'])
        #
        #     embed_msg = await self.ntsk.send_message(msg.channel, embed=danbo_embed)
        #
        #     # pair msg id with that embed in json file
        #     self.timerHolder.pair_msg_with_index(msg.server.id, embed_idx, embed_msg.id)
        #
        #     # add left/right emoji to embed message
        #     await self.ntsk.add_reaction(embed_msg, '⬅')
        #     await self.ntsk.add_reaction(embed_msg, '➡')
        #     await self.ntsk.add_reaction(embed_msg, '🔼')
        #     await self.ntsk.add_reaction(embed_msg, '❌')
        #
        #     print("i should've send a message")
        #
        #     return True


    async def translate(self, msg, *args):
        params = args[0]
        if len(params) < 3:
            format_err_msg = "Oh! That's not how you format ~translate! >_<\n"
            #await self.ntsk.send_message(msg.channel, format_err_msg + data.TRANSLATE_FORMAT)
            await self.ntsk.send_message(msg.channel, format_err_msg)

        text = ' '.join(params[2:])
        success, trans = translate.get_translation(params[1], text)

        trans = trans[0]

        if len(trans) > 2000:
            lth_err_msg = "The translation is too loong~!"
            await self.ntsk.send_message(msg.channel, lth_err_msg)
            return False

        await self.ntsk.send_message(msg.channel, trans)
        #return success

    async def set_quote(self, msg, *args):
        quote = ' '.join(args[0][1:])
        await self.CharQuery.set_character_data(quote, msg.author.id, 'quote', msg.server.id)
        await self.ntsk.send_message(msg.channel, "Quote set~!")

    async def get_quote(self, msg, *args):
        quote = await self.CharQuery.get_character_data(msg.author.id, 'quote', msg.server.id)
        await self.ntsk.send_message(msg.channel, quote)

    async def matrix(self, msg, *args):
        x = ' '.join(msg.content.split(' ')[1:]) # + " "
        s = ""
        for i in range(len(x)):
            s += x[i:] + x[0:i] + "\n"

        s = s[:-1]
        if len(s) > 2000:
            await self.ntsk.send_message(msg.channel, "Text too biiiig...~")
        else:
            await self.ntsk.send_message(msg.channel, s)

    async def display_score(self, msg, *args):
        score_display_msg = await self.scoreReact.check_score(msg.author.id, msg.server.id)
        await self.ntsk.send_message(msg.channel, score_display_msg)

    async def display_top_words(self, msg, *args):

        params = args[0][1:]

        min_lth = 4 # default
        punct_flag = False
        usr_mention_id = None
        if len(msg.raw_mentions) != 0:
            usr_mention_id = msg.raw_mentions[0]

        for p in params:
            if p.isdigit() and len(p) < 5: # second if checks if not usr id, roughly
                min_lth = int(p)
            elif p in ('.punct', '.punctuation'):
                print('.punct found')
                punct_flag = True
            elif p in ('me', '.me'):
                usr_mention_id = msg.author.id
            elif not usr_mention_id:
                try:
                    usr = await self.ntsk.get_user_info(p)
                    usr_mention_id = usr.id
                except Exception as e:
                    print(e)

        # message author is no longer default
        # default is the whole server
        # if not usr_mention_id:
        #     usr_mention_id = msg.author.id
        #     print('hello?')
        #     print(usr_mention_id)


        top_words = await data.data_query.get_top_words(usr_mention_id, msg.server.id, 20, min_lth, punct_flag)
        top_words = "```fix\n" + '\n\n'.join(top_words) + "\n```"
        await self.ntsk.send_message(msg.channel, top_words)

    async def match_ateji(self, msg, *args):
        params = args[0][1:]
        kanji_list = params
        matches, too_long = self.atejiMatcher.match_ateji(kanji_list)

        output = last_output = ""
        for romaji, katakana, kanji in matches:
            output += romaji + ": " + kanji + "（" + katakana + "）\n"

        if too_long:
            output += "\nSkipped certain kanji readings to save time..."
        # output = '\n'.join(matches)
        await self.ntsk.send_message(msg.channel, output)

    async def future_say(self, msg, *args):
        params = args[0][1:]
        hours = minutes = seconds = 0

        time_offset = [0, 0, 0]

        if len(params) < 4:
            await self.ntsk.send_message(msg.channel, "Hmm! I don't understand that format!~\n Please try `" + pfx + "futuresay hr min sec <text>!`")
            return False

        for i in range(3):
            if params[i].isnumeric():
                time_offset[i] = int(params[i])
            else:
                await self.ntsk.send_message(msg.channel, "That syntax doesn't seem right... If you need my help, just use " + pfx + "commands :cat::ok_hand:")
                return False

        h, m, s = time_offset
        time_offset = 3600*h + 60*m + s
        text = ' '.join(params[3:])
        await asyncio.sleep(time_offset)
        await self.ntsk.send_message(msg.channel, text)


    async def automata(self, msg, *args):

        # max 5 chars allowed
        # min 2
        # must be space separated

        params = args[0][1:]

        chrs = []
        for p in params:
            if len(p) == 1:
                # found char
                chrs.append(p)


        if len(chrs) < 2:
            chrs = ['👌','😂','🔥']
        elif len(chrs) > 5:
            chrs = chrs[:5]

        chrs_dict, board = text_automata.init_automata(chrs)

        last_msg = await self.ntsk.send_message(msg.channel, '_ _\n' + '\n'.join([''.join(x) for x in board]))

        num_frames = 15
        for i in range(num_frames):
            board = text_automata.game_loop(chrs_dict, len(chrs), board)
            time.sleep(1)
            last_msg = await self.ntsk.edit_message(last_msg, new_content='_ _\n' + '\n'.join([''.join(x) for x in board]))

        return True


    async def lmgtfy(self, msg, *args):
        params = args[0][1:]
        output = "Here you go, silly~\n"
        output += "http://lmgtfy.com/?q="
        output += '+'.join(params)
        await self.ntsk.send_message(msg.channel, output)

    async def ask_trivia(self, msg, *args):
        config = json.load(open("data/databases/" + msg.server.id + "/" + 'opentdb_config.json'))

        TOKEN = config['token']

        params = args[0][1:]
        difficulty = category = type = None
        # for p in params:
        #     if
        # num_questions = 1
        resp_code, questions = trivia.get_trivia_questions(TOKEN, amt=1)
        if resp_code == 3:
            import requests
            data = requests.post(url="https://opentdb.com/api_token.php?command=request")
            TOKEN = data.json()["token"]
            config["token"] = TOKEN
            resp_code, questions = trivia.get_trivia_questions(TOKEN, amt=1)
        #prompts, correct_answers, incorrect_answers = [], [], []
        prompt, correct_answer, incorrect_answers = questions[0]['question'], questions[0]['correct_answer'], questions[0]['incorrect_answers']
        prompt += "\n"

        ans_list = [correct_answer] + incorrect_answers
        random.shuffle(ans_list)
        ans_list_copy = ans_list[:]

        correct_idx = None
        for i, s in enumerate(ans_list):
            prompt += "\n({}) {}".format(i+1, s)
            ans_list_copy.append(str(i+1))
            if s == correct_answer:
                correct_idx = str(i+1)

        await self.ntsk.send_message(msg.channel, prompt)

        await self.CharQuery.update_points(-1, msg.author.id, msg.server.id)

        ans_list = [x.lower() for x in ans_list_copy]

        #print('ans_list =', ans_list)

        chk = lambda m : m.content.lower() in ans_list and m.channel.id == msg.channel.id

        resp_msg = await self.ntsk.wait_for_message(timeout=10, author=msg.author, check=chk)
        if not resp_msg:
            await self.ntsk.send_message(msg.channel, "Bzzt! Took too long to respond...!")
            return

        guess = resp_msg.content.lower()
        if guess in (correct_answer.lower(), correct_idx):
            # correct answer!
            # add points to profile
            await self.CharQuery.update_points(3, msg.author.id, msg.server.id)
            await self.ntsk.send_message(resp_msg.channel, "That's right! Yay!")
            return

        await self.ntsk.send_message(resp_msg.channel, "Aww... You're wrong...")

    async def ask_kanji_quiz(self, msg, *args):
        params = args[0][1:]

        grade = None
        if len(params) >= 1:
            if params[0] in ('1','2','3','4','5','6'):
                grade = params[0]
            elif params[0] in ('.grade=1', '.grade=2', '.grade=3', '.grade=4', '.grade=5', '.grade=6')\
                or params[0] in ('.level=1', '.level=2', '.level=3', '.level=4', '.level=5', '.level=6'):
                grade = params[0].split('=')[1]

        kanji, answers = self.kanjiQuiz.get_question_and_answers(grade)
        prompt = "「" + kanji + "」"
        await self.ntsk.send_message(msg.channel, prompt)

        #await self.CharQuery.update_points(-1, msg.author.id, msg.server.id)

        resp_msg = await self.ntsk.wait_for_message(timeout=10, author=msg.author)
        if not resp_msg:
            if random.randrange(10) == 3:
                await self.ntsk.send_message(msg.channel, "遅いぞー！")
            else:
                await self.ntsk.send_message(msg.channel, "Bzzt! Took too long to respond...!")
            return

        guess = resp_msg.content.lower()
        if guess in answers:
            # correct answer!
            # add points to profile
            #await self.CharQuery.update_points(3, msg.author.id, msg.server.id)
            if random.randrange(10) == 3:
                await self.ntsk.send_message(resp_msg.channel, "正解！")
            else:
                await self.ntsk.send_message(resp_msg.channel, "That's right! Yay!")
            return

        if random.randrange(10) == 3:
            await self.ntsk.send_message(resp_msg.channel, "違うよー")
        else:
            await self.ntsk.send_message(resp_msg.channel, "Aww... You're wrong...")


    async def show_points(self, msg, *args):
        params = args[0][1:]
        server_points = await self.CharQuery.get_points(msg.author.id, msg.server.id)

        resp = "{} has {} points!".format(msg.author.name, server_points)

        import random
        if server_points > 10 and random.randrange(10) == 2:
            resp += " Wow! No life~ :3"

        await self.ntsk.send_message(msg.channel, resp)
        return



    async def get_commands(self, msg, *args):
        await self.ntsk.send_message(msg.author, COMMANDS_STR)

    # make !help <command> function
    # document functions

    async def display_info(self, msg, *args):
        await self.ntsk.send_message(msg.channel, "nya")
        # if random.randrange(10) == 0:
        #     # config_data['weight'] etc except don't make it config_data
        #     print('say something awkward, delay, then post info')
        # await self.ntsk.send_message(msg.channel, embed=data.data_holder.getGithubEmbed())

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
            await self.ntsk.leave_server(msg.server)
        else:
            await self.ntsk.send_message(msg.channel, "Unknown command! `" + pfx + "commands` if you can't figure it out...")

    async def take_reaction(self, reaction, user):

        print(reaction.emoji)
        # check if on one of the embed messages
        embed_idx = self.timerHolder.get_embed_idx(reaction.message.server.id, reaction.message.id)
        print('embed_idx =',embed_idx)
        if embed_idx:
            print("%s put a reaction on embed message!" % (user.name,))
            if reaction.custom_emoji:
                return False # or maybe just do something else?

            controller_emoji = None
            num_posts = self.danbooruQuery.embed_data[reaction.message.server.id][str(embed_idx)]["num_posts"]
            last_query = self.danbooruQuery.embed_data[reaction.message.server.id][str(embed_idx)]["last_query"]

            if reaction.emoji in '⬅➡' and self.danbooruQuery.embed_data[reaction.message.server.id][str(embed_idx)]["private"] \
                    and user.id != self.timerHolder.get_embed_creator(reaction.message.server.id, embed_idx-1):
                print("Someone tried to change someone else's embed...")
                return

            if reaction.emoji == '⬅':
                self.danbooruQuery.embed_data[reaction.message.server.id][str(embed_idx)]["last_query"] = (num_posts + last_query - 1)%num_posts
                controller_emoji = '⬅'
            elif reaction.emoji == '➡':
                self.danbooruQuery.embed_data[reaction.message.server.id][str(embed_idx)]["last_query"] = (last_query + 1)%num_posts
                controller_emoji = '➡'
            elif reaction.emoji == '❌':
                # delete post if this is orig user
                if user.id == self.timerHolder.get_embed_creator(reaction.message.server.id, embed_idx-1):
                    await self.ntsk.delete_message(reaction.message)
                    # end that timer
                    self.timerHolder.make_embed_replaceable(reaction.message.server.id, embed_idx)
                    return
                print('used X')
            elif reaction.emoji == '🔼':
                # "save pic" by PMing to user

                # get pic info
                post_data = await self.danbooruQuery.get_post(reaction.message.server.id, embed_idx)

                # set up PM embed with post data
                artist_info = "artist: %s" % (post_data["tag_string_artist"],)
                id_info = "id: %s" % (post_data['id'],)
                danbo_pm_embed = discord.Embed(title=id_info, description=artist_info, colour=discord.Color(0xF5F5FF))  # description="No descriptions yet..." ['artist_commentary']
                danbo_pm_embed.set_image(url=post_data['large_file_url'])
                danbo_pm_embed.set_footer(text=post_data['source'])

                # send PM embed to user
                await self.ntsk.send_message(user, embed=danbo_pm_embed)
                await self.ntsk.remove_reaction(reaction.message, '🔼', user)
                return

            if controller_emoji:
                post_data = await self.danbooruQuery.get_post(reaction.message.server.id, embed_idx)

                # set up embed with post data
                page_status = "%s/%s" % (self.danbooruQuery.embed_data[reaction.message.server.id][str(embed_idx)]["last_query"]+1, num_posts)
                id_info = "id: %s" % (post_data['id'],)
                artist_info = "artist: %s" % (post_data["tag_string_artist"],)
                danbo_embed = discord.Embed(title=page_status,
                                            description=artist_info)  # description="No descriptions yet..." ['artist_commentary']
                if 'file_url' in post_data:
                    danbo_embed.set_image(url=post_data['file_url'])
                else:
                    danbo_embed.set_image(url='http://i68.tinypic.com/1kb9h.png')
                danbo_embed.set_footer(text=post_data['source'])

                # edit message with embed
                await self.ntsk.edit_message(reaction.message, embed=danbo_embed)
                await self.ntsk.remove_reaction(reaction.message, controller_emoji, user)


