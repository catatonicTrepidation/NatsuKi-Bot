# encoding: utf8
import requests
import json
import urllib.parse
import random
from itertools import combinations, permutations

import jaconv

from kanjitesting.romkan.common import to_hepburn, to_kunrei
from kanjitesting.unirest import init

import kanjireq





class AtejiMatcher:

    def __init__(self):
        print('AtejiMatcher initialized!')
        self.name_data = None
        with open('./data/namedataA.json') as f:
            self.name_data = json.load(f)

    def get_all_readings(self, kanji_list):
        # print('kanji_list2 =',kanji_list)

        readings_list = [None]*len(kanji_list)
        for i in range(len(kanji_list)):
            kanji = kanji_list[i]
            onyomi_list, kunyomi_list, nanori_list = kanjireq.get_kanji_readings(kanji)
            readings_list[i] = (kanji, onyomi_list, kunyomi_list, nanori_list)

        return readings_list

    def match_ateji(self, kanji_list):
        print(*kanji_list)
        readings_list = self.get_all_readings(kanji_list) # [(kanji1, [x (on1, dynasty1), ..], [ (kun1, okurigana1), ..], [nanori1, nanori2, ..]), (kanji2, ..)]
        downsized = False
        print()
        print('all readings =',readings_list)
        print()
        print()


        kanji_with_readings = []
        for kanji, on_readings, kun_readings, nanori_readings in readings_list:
            if on_readings:
                for on_r, dyn in on_readings:
                    kanji_with_readings.append((kanji, on_r))
            if kun_readings:
                for kun_r, okuri in kun_readings:
                    kanji_with_readings.append((kanji, jaconv.hira2kata(kun_r)))
            if nanori_readings:
                for nanori_r in nanori_readings:
                    kanji_with_readings.append((kanji, jaconv.hira2kata(nanori_r)))

        print(kanji_with_readings)
        print(len(kanji_with_readings))
        print()
        mxlth = 28
        if len(kanji_with_readings) > mxlth:
            kanji_with_readings = kanji_with_readings[:mxlth]
            downsized = True
        print(kanji_with_readings)
        print(len(kanji_with_readings))
        idx = 0
        matches = []
        for i in range(1,min(6,len(kanji_with_readings)+1)):
            reading_combinations = combinations(kanji_with_readings, i)
            for comb in reading_combinations:
                idx += 1
                # print('comb =',list(comb))
                reading_permutations = permutations(comb)
                for perm in reading_permutations:
                    kj = ""
                    rd = ""
                    for kanji, reading in perm:
                        kj += kanji
                        rd += reading
                    # print(kj,'|',rd)
                    if rd in self.name_data['katakana']:
                        print()
                        print('Match:')
                        print(self.name_data['katakana'][rd] + ":",kj)
                        matches.append((self.name_data['katakana'][rd], rd, kj))
        print(idx)
        return list(set(matches)), downsized

                    # print('r =',perm)
            # print('---')
        # print(reading_combinations)






#
# if __name__ == "__main__":
    # print()
    # TOKEN = requests.post(url="https://opentdb.com/api_token.php?command=request")
    # print(TOKEN.json())
    # resp_code, results = get_trivia_questions()
    # print(resp_code)
    # print(results)
    # print(get_question_and_answer())
    # am1 = AtejiMatcher()
    # print('マリサ' in am1.name_data['katakana'])
    # print(am1.match_ateji(['梃']))
    # print(am1.match_ateji(['梃','魔','子','理','流']))
    # print(am1.match_ateji(['瀬','羅']))
    # am1.match_ateji(['猫','犬','鳥','羊','女','男','魚','髪','日','辺','馬','意','流','図'])



# # TOKEN = requests.post(url="https://opentdb.com/api_token.php?command=request")
# # print(TOKEN.json())