#!/usr/bin/env python3.5
# coding=utf-8

"""
RSA LIBRARY BY: Sybren A. Stüvel
https://github.com/sybrenstuvel/python-rsa
"""

import rsa
from rsa import key
import codecs
import binascii

import json
import discord





class Encryptor:

    def __init__(self):
        print('initializing encryptor')
        self.key_pairs, self.prime_pairs, self.n_vals = self.load_rsa_data()


    def load_rsa_data(self):
        rsa_data = json.load(open("data/rsadata.json", 'r'))
        return rsa_data["keypairs"], rsa_data["primepairs"], rsa_data["nvals"]

    async def encrypt_message(self, text, idxflag=1):
        idxflag-=1
        N = self.n_vals[idxflag]
        e, d = self.key_pairs[idxflag]
        hex_text = self.encrypt(text, N, e)
        return hex_text

    def encrypt(self, msg, N, e):
        enc_msg = rsa.encrypt(bytes(msg, 'utf-8'), rsa.key.PublicKey(N, e))
        hex_text = binascii.b2a_base64(enc_msg).decode('utf-8') #b2a_hex

        return hex_text

    async def decrypt_message(self, hex_text, idxflag=1):
        idxflag -= 1
        N = self.n_vals[idxflag]
        e, d = self.key_pairs[idxflag]
        p, q = self.prime_pairs[idxflag]
        dec_msg = self.decrypt(hex_text, N, e, d, p, q)

        return dec_msg


    def decrypt(self, hex_text, N, e, d, p, q):
        enc_msg = binascii.a2b_base64(hex_text) #a2b_hex
        dec_msg = rsa.decrypt(enc_msg, rsa.key.PrivateKey(N, e, d, p, q)).decode('utf-8')

        return dec_msg

    # ---math---

    def gcd(self, a, b):
        while b != 0:
            c = a % b
            a = b
            b = c
        return a

    def multiplicative_inverse(self, e, phi):
        d = 0
        x1 = 0
        x2 = 1
        y1 = 1
        temp_phi = phi

        while e > 0:
            temp1 = temp_phi // e
            temp2 = temp_phi - temp1 * e
            temp_phi = e
            e = temp2

            x = x2 - temp1 * x1
            y = d - temp1 * y1

            x2 = x1
            x1 = x
            d = y1
            y1 = y

        if temp_phi == 1:
            return d + phi


    def generate_keypair(self, p, q):
        """kudos to whoever made this function"""

        import random
        # Phi is the totient of n

        phi = (q-1)*(p-1)
        # Choose an integer e such that e and phi(n) are coprime
        e = random.randrange(1, phi)

        # Use Euclid's Algorithm to verify that e and phi(n) are comprime
        g = self.gcd(e, phi)
        while g != 1:
            e = random.randrange(1, phi)
            g = self.gcd(e, phi)

        # Use Extended Euclid's Algorithm to generate the private key
        d = self.multiplicative_inverse(e, phi)

        return (e, d)


#enc1 = Encryptor()
#print(enc1.generate_keypair(259117086013202627776246767922441530941818887553125427303974923161874019266586362086201209516800483406550695241733194177441689509238807017410377709597512042313066624082916353517952311186154862265604547691127595848775610568757931191017711408826252153849035830401185072116424747461823031471398340229288074545677907941037288235820705892351068433882986888616658650280927692080339605869308790500409503709875902119018371991620994002568935113136548829739112656797303241986517250116412703509705427773477972349821676443446668383119322540099648994051790241624056519054483690809616061625743042361721863339415852426431208737266591962061753535748892894599629195183082621860853400937932839420261866586142503251450773096274235376822938649407127700846077124211823080804139298087057504713825264571448379371125032081826126566649084251699453951887789613650248405739378594599444335231188280123660406262468609212150349937584782292237144339628858485938215738821232393687046160677362909315071,
#                           190797007524439073807468042969529173669356994749940177394741882673528979787005053706368049835514900244303495954950709725762186311224148828811920216904542206960744666169364221195289538436845390250168663932838805192055137154390912666527533007309292687539092257043362517857366624699975402375462954490293259233303137330643531556539739921926201438606439020075174723029056838272505051571967594608350063404495977660656269020823960825567012344189908927956646011998057988548630107637380993519826582389781888135705408653045219655801758081251164080554609057468028203308718724654081055323215860189611391296030471108443146745671967766308925858547271507311563765171008318248647110097614890313562856541784154881743146033909602737947385055355960331855614540900081456378659068370317267696980001187750995491090350108417050917991562167972281070161305972518044872048331306383715094854938415738549894606070722584737978176686422134354526989443028353644037187375385397838259511833166416134323695660367676897722287918773420968982326089026150031515424165462111337527431154890666327374921446276833564519776797633875503548665093914556482031482248883127023777039667707976559857333357013727342079099064400455741830654320379350833236245819348824064783585692924881021978332974949906122664421376034687815350484991))
# x = "hello"

# print(enc1.encrypt_message(x))
# print(enc1.decrypt_message(enc1.encrypt_message(x)))
