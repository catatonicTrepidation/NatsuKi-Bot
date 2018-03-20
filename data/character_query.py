#!/usr/bin/python
# -*- coding: utf-8 -*-

import discord
import sqlite3 as lite
import sys

import random

pfx = "~"




class CharacterQuery:

    def __init__(self):
        self.last_query = None

    



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