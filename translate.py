import requests
import json


api_data = json.load(open('data/yandexdata.json'))
KEY = api_data['key']
DIRS = api_data['dirs']


def get_translation(lang, text):
    lang = lang.lower()
    if not is_valid_dir(lang):
        if "jp" in lang:
            return False, ["This translator doesn't know moon runes T_T"]
        return False, ["Can't translate those languages... :/"]

    base_url = 'https://translate.yandex.net/api/v1.5/tr.json/translate?key='
    full_url = base_url + KEY + "&text=" + text + "&lang=" + lang
    response = requests.post(url=full_url)
    trans_data = response.json()

    if response.status_code == 413:
        return False, ["Exceeded the maximum text size :c"]
    elif response.status_code == 422:
        return False, ["An unknown error has occurred . . !"]

    print(response.text)
    return True, trans_data['text']


def is_valid_dir(param):
    return param in DIRS


def get_valid_langs():
    base_url = 'https://translate.yandex.net/api/v1.5/tr.json/getLangs?key='
    full_url = base_url + KEY
    response = requests.post(url=full_url)

    print(response.text)

#print(get_translation('en-ru','hello'))
#get_valid_langs()
