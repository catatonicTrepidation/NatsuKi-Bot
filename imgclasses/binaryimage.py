#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

import math
import random
from PIL import Image

import download



class BinaryImage:

    def __init__(self, message):
        self.message = message
        self.sizes = [10, 20, 50, 100, 200] # why not just make continuous?
        print('initializing')

    async def create_image(self, author=False, recipient=False): # if user allows only himself to decrypt image, send specific message
        print("\nENCODING...")
        b_msg = self.str_bin(self.message)

        full_length = 16 + 64 + 64 + len(b_msg) # text lth indicator + author indicator + recipient indicator + text lth

        # sidelength_lowerbound = math.ceil(math.sqrt(full_length))

        img_side_length = None
        for sz in self.sizes:
            if sz ** 2 >= full_length:  # minimum size that fits
                img_side_length = sz
                break

        if not img_side_length:
            return False

        b_lth = "{0:b}".format(full_length)
        b_lth = b_lth.zfill(16)

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

        b_recip = ''
        if recipient:
            b_recip = int(b_recip)
            b_recip = "{0:b}".format(b_recip)
            b_recip = b_recip.zfill(64)
        else:
            # for i in range(64):
            #     b_auth += str(random.randrange(2))
            b_recip = "0110111001100001011101000111001101110101011010110110100101111110"  # natsuki~


        bin_seq = b_lth + b_auth + b_recip + b_msg

        print('b_lth =',b_lth)
        print('b_auth =',b_auth)
        print('b_recipt =',b_recip)
        print('b_msg =',b_msg)

        print('bin_seq =',bin_seq)


        # image code here
        oncolor = (0, 0, 0)
        offcolor = (255, 255, 255)
        clrs = [offcolor, oncolor]
        side_lth = img_side_length
        img = Image.new('RGB', (side_lth, side_lth), color=offcolor)
        pixels = img.load()

        row = col = 0

        ctr = 0
        for i in range(full_length):  # encode seq lth, author, recipient, text
            bit = int(bin_seq[i])
            pixels[col, row] = clrs[bit]
            ctr += 1
            row = ctr // side_lth
            col = ctr % side_lth

        bits_remaining = side_lth ** 2 - full_length

        for i in range(bits_remaining):  # encode random binary vals
            bit = random.randrange(2)
            pixels[col, row] = clrs[bit]
            ctr += 1
            row = ctr // side_lth
            col = ctr % side_lth

        img.save('output/images/binimage.png')
        return True

    async def decode_image(self, msg): # Consider adding filename param?
        print("\nDECODING...")


        """v DO THIS IN COMMAND_PEN CLASS v"""

        download.download_image(msg.attachments[0]['url'], "downloaded/images/imgtodecode.png")
        img = Image.open("downloaded/images/imgtodecode.png")

        """^ DO THIS IN COMMAND_PEN CLASS ^"""

        author_id = msg.author.id

        # catch error, return False? "Cooldown -- too many requests"?

        # reading pixels
        pixels = img.load()
        side_lth = img.width
        row = col = 0
        ctr = 0

        MEGABINSTRING = ""

        b_vals = {0 : '1', 255 : '0'}

        b_lth = ""
        for i in range(16):  # read length of text
            b_lth += b_vals[pixels[col, row][0]]
            ctr += 1
            row = ctr // side_lth
            col = ctr % side_lth


        full_length = int(b_lth, 2)

        b_auth = ""
        for i in range(64):  # read author
            b_auth += b_vals[pixels[col, row][0]]
            ctr += 1
            row = ctr // side_lth
            col = ctr % side_lth


        img_author = ''
        if b_auth == "0110000101101110011011110110111000101101011100110110000101101110":
            img_author = "anon-san"
        else:
            img_author = str(int(b_auth, 2))

        b_recip = ""
        for i in range(64):  # read recipient
            b_recip += b_vals[pixels[col, row][0]]
            ctr += 1
            row = ctr // side_lth
            col = ctr % side_lth


        img_recipient = ''
        if b_recip == "0110111001100001011101000111001101110101011010110110100101111110":
            img_recipient = "natsuki~"
        else:
            img_recipient = str(int(b_recip, 2))

        print('ctr =', ctr)
        print('side_lth =',side_lth)
        print('b_lth =',b_lth,' | ','full_length =', full_length)
        print('b_auth =',b_auth,' | ','img_author =',img_author)
        print('b_recipt =',b_recip,' | ','img_recipient =',img_recipient)

        MEGABINSTRING += b_lth + b_auth + b_recip

        text_length = full_length - 64 - 64 - 16  # minus auth, recip, lth indicators
        byte = ""
        decoded_text = ""
        for i in range(1, text_length+1):  # read text
            MEGABINSTRING += b_vals[pixels[col, row][0]]
            byte += b_vals[pixels[col, row][0]]
            ctr += 1
            row = ctr // side_lth
            col = ctr % side_lth
            if i % 8 == 0:
                #print('byte =',byte,' ||| ','decoded_text =',decoded_text)
                #print('int(byte, 2) =',int(byte, 2))
                decoded_text += chr(int(byte, 2))
                byte = ""

        print('MEGABIGSTRING =',MEGABINSTRING)
        print('b_msg =',decoded_text)

        return False, False, decoded_text

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
