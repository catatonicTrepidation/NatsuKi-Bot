#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import random

pfx = "~"

def download_image(url, filename):
    """
    Download image from url
    :param url: URL of image to download
    :param filename: Filename to call saved image
    """
    r = requests.get(url)
    open(filename, 'wb').write(r.content)



