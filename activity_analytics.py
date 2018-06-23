#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
from PIL import Image
from datetime import datetime
from string import punctuation

from data.data_setup import get_con, get_meta




def plot_activity(db_name, server_id, author_id=None, key_word=None):
    con = get_con(db_name, server_id)

    sql_query = "SELECT UserId, Time FROM messages"
    msg_list = []
    with con:
        cur = con.cursor()
        cur.execute(sql_query)

        msg_list = cur.fetchall()

    #print('msg_list =',msg_list)
    print('length is',len(msg_list))
    print(msg_list[0],'\n',msg_list[-1])
    print()

    fmt1 = '%Y-%m-%d %H:%M:%S.%f'  # or w/e you have
    fmt2 = '%Y-%m-%d %H:%M:%S'  # or w/e you have
    start_date = datetime.strptime('2018-03-19 22:00:06.006000', fmt1)  # make dynamic (obviously)
    end_date = datetime.strptime('2018-04-07 04:02:31.681000', fmt1)
    time_span = end_date - start_date
    time_span_days = time_span.days
    # want 1600x800 image
    img_width = 1600
    img_height = 800
    img = Image.new('RGB', (img_width, img_height), color=(255,255,255))
    pixels = img.load()

    col_dict = dict()
    diff = None
    print('time_span_days =',time_span_days)
    print()
    for author_id, send_date in msg_list:
        #print(author_id, '|', send_date)
        if '.' not in send_date:
            diff = datetime.strptime(send_date, fmt2) - start_date
        else:
            diff = datetime.strptime(send_date, fmt1) - start_date
        diff_days = diff.days
        #print('diff_days =',diff_days)
        col = int((img_width-1) * (diff_days / time_span_days))  # img_width-1 ?
        if col in col_dict:
            col_dict[col] += 1
        else:
            col_dict[col] = 1

    max_col_val = max(col_dict.values())
    min_col_val = min(col_dict.values())
    print(col_dict)

    line_color = (0, 0, 255)

    def draw_line(c1, r1, c2, r2):
        line = get_line(c1, r1, c2, r2)
        for x, y in line:
            pixels[x, y] = line_color


    prev_col, prev_row = 0,0
    for col, val in col_dict.items():
        #print('val / max_col_val =',((val - min_col_val) / max_col_val))  # (val / max_col_val)? not relative to min?
        row = int((img_height-1) * (val / max_col_val))
        draw_line(prev_col, prev_row, col, row)
        prev_col, prev_row = col, row

    img.save('message_graph.png')


def get_line(x1, y1, x2, y2):
    # Setup initial conditions
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

plot_activity('messages', '232903861373763585')


