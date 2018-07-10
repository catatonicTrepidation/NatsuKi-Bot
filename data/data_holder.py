#!/usr/bin/python
# -*- coding: utf-8 -*-

import discord
import sqlite3 as lite
import sys

import random

pfx = "~"

github_avatars = ["https://i.imgur.com/0KAft3O.jpg",
                  "https://i.imgur.com/rEVHUBw.jpg",
                  "https://i.imgur.com/5MnxW87.jpg"]

GITHUB = "https://github.com/catatonicTrepidation/NatsuKi-Bot#natsuki-bot"

NTSK_INFO = "Hi~ I'm NatsuKi, and you'd better not forget it! " \
            "I'll beat up dumb-dumbs who think my poems are cute!\n\n" \
            "If you want to get to know me, follow the link below..."

GITHUB_EMBED = discord.Embed(url=GITHUB, description=NTSK_INFO, colour=discord.Color(0xF17B9F))
GITHUB_EMBED.set_footer(text=GITHUB, icon_url="https://i.imgur.com/0RkZBe1.png")




# COMMANDS_DICT = {
#                 pfx + "commands" : "`" + pfx + "commands`                                                                   :: Get list of commands🖊",
#                 pfx + "info"     : "`" + pfx + "info`                                                                            :: Learn about me~!",
#                 pfx + "bin"      : "`" + pfx + "bin <text>`                                                               :: Convert text to binary image",
#                 pfx + "unbin"    : "`" + pfx + "unbin <image|URL>`                                               :: Decode binary image",
#                 pfx + "count"    : "`" + pfx + "count <text> [channel] [user] [.like]` :: Query number of messages in database",
#                 pfx + "qr"       : "`" + pfx + "qr [text]`                                                                 :: Turn text into QR code"
#                 }

COMMANDS_DICT = {
                pfx + "commands" : pfx + "commands                              :: Get list of commands🖊\n",
                pfx + "info"     : pfx + "info                                  :: Learn about me~!\n",
                pfx + "bin"      : pfx + "bin   <text> [bool] [ID]              :: Convert text to binary image\n",
                pfx + "unbin"    : pfx + "unbin <image|URL>                     :: Decode binary image\n",
                pfx + "enc"      : pfx + "enc [.1-5] <text>                     :: Encode text with RSA\n",
                pfx + "dec"      : pfx + "dec [.1-5] <text>                     :: Decode text with RSA\n",

                pfx + "trans"    : pfx + "trans <lang-dir> <text>               :: Translate text (e.g. " + pfx + "trans en-es hello)\n",

                pfx + "setquote" : pfx + "setquote <text>                       :: Set favorite quote\n",
                pfx + "quote"    : pfx + "quote                                 :: Natsuki says your quote\n",
                pfx + "futuresay": pfx + "futuresay h m s <text>                :: Natsuki says what you tell her -- in the future!\n",
                pfx + "count"    : pfx + "count <text> [channel] [user] [.like] :: Query number of messages in database\n",
                pfx + "stats"    : pfx + "stats [me|mention|ID] [num] [.punct]  :: Get top used words\n",
                pfx + "logs"     : pfx + "logs [.rand] [.image] [db id] [num]   :: Get messages from the logs\n",
                pfx + "qr"       : pfx + "qr    [text]                          :: Turn text into QR code"
                }


CMD_LEGEND = "Legend: <> specifies required params, [] specifies optional params"



bad_responses = [

    "...",
    "Just go away...",
    "No thank you.",
    "You can leave now.",
    "I don't need to hear it from *you.*",
    "Oh no, you again... " + b'\xF0\x9F\x98\xA3'.decode('utf-8')

]

neutral_responses = [

    "Want to, um, read some manga..?",
    "W-What do you want?",
    "Well, I am a pro.",
    "Hmm?"

]

good_responses = [

    "♡",
    "Hey~",
    "Let's read manga~ :3",
    "ニャ〜！",
    "H-How do I look?",
    "I made cupcakes..!"

]

all_responses = [bad_responses, neutral_responses, good_responses]


# COMMANDS_DICT = {pfx + "count":formatCmdDesc("count","<text> [channel] [user] [.like]","Query number of messages in database"),
#             pfx + "commands":formatCmdDesc("commands","","Get list of commands🖊"),
#             pfx + "qr":formatCmdDesc("qr","[text]","Turn text into QR code")}



def getGithubEmbed():
    GITHUB_EMBED.set_thumbnail(url=getGitAvi())  # pick random embed image
    return GITHUB_EMBED

def getGitAvi():
    r = random.randrange(len(github_avatars))
    return github_avatars[r]



def formatCmdDesc(cmd, params, desc):
    return '{message:{fill}{align}}'.format(
            message="`" + pfx + cmd + "` " + params, fill=' ',align='<90') + " :: " + desc



def getCommandsString():
    COMMANDS_STR = ""
    for cmd, desc in COMMANDS_DICT.items():
        COMMANDS_STR += desc + "\n"
    COMMANDS_STR = CMD_LEGEND + "\n\n" + COMMANDS_STR
    return COMMANDS_STR

def getResponseList(idx):
    return all_responses[idx]
