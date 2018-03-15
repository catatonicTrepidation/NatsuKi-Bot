#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

import math
import random
from PIL import Image


class BinaryImage:

    def __init__(self, message):
        self.message = message
        self.sizes = [10, 20, 50, 100, 200]
        print('initializing')

    async def create_image(self, author=False):
        print('starting create_image...')

        b_msg = self.str_bin(self.message)

        full_length = len(b_msg) + 8 + 64  # text lth + text lth indicator + author indicator

        # sidelength_lowerbound = math.ceil(math.sqrt(full_length))

        img_side_length = None
        for sz in self.sizes:
            if sz ** 2 >= full_length:  # minimum size that fits
                img_side_length = sz
                break

        if not img_side_length:
            return False

        b_lth = "{0:b}".format(full_length)
        b_lth = b_lth.zfill(8)

        b_auth = ''
        if author:
            translator = str.maketrans('', '', '<@!>')
            b_auth = self.message.author.id
            b_auth = b_auth.translate(translator)
            b_auth = int(b_auth)
            b_auth = "{0:b}".format(b_auth)
            b_auth = b_auth.zfill(64)
        else:
            # for i in range(64):
            #     b_auth += str(random.randrange(2))
            b_auth = "0110000101101110011011110110111000101101011100110110000101101110"  # anon-san

        bin_seq = b_lth + b_auth + b_msg

        # image code here
        oncolor = (255, 0, 0)
        offcolor = (255, 255, 255)
        clrs = [offcolor, oncolor]
        side_lth = img_side_length
        img = Image.new('RGB', (side_lth, side_lth), color=offcolor)
        pixels = img.load()

        row = col = 0

        ctr = 0
        for i in range(full_length):
            bit = int(bin_seq[i])
            pixels[col, row] = clrs[bit]
            row = ctr // side_lth
            col = ctr % side_lth
            ctr += 1

        bits_remaining = side_lth ** 2 - full_length

        for i in range(bits_remaining + 1):
            bit = random.randrange(2)
            pixels[col, row] = clrs[bit]
            row = ctr // side_lth
            col = ctr % side_lth
            ctr += 1
            # print(pixels[col, row],bit)
        print('YES')
        img.save('output/binimage.png')
        return True

    def str_bin(self, s_str):
        binary = []
        for s in s_str:
            if s == ' ':
                binary.append('00100000')
            else:
                binary.append(bin(ord(s)))
        b_str = ''.join(str(s) for s in binary)  # array to string
        b_str = b_str.replace('b', '')  # get rid of binary indicator
        return b_str
