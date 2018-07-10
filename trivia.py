import requests
import json

import base64
def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

def decode_base64(strg):
    lens = len(strg)
    lenx = lens - (lens % 4 if lens % 4 else 4)
    return base64.decodestring(strg[:lenx])

# config = json.load(open('opentdb_config.json'))

#TOKEN = config['token']

def get_trivia_questions(TOKEN, amt="10", diff=None, catergory=None, type=None, encoding="base64"):
    base_url = "https://opentdb.com/api.php?token=" + TOKEN
    request_url = base_url + "&amount=" + str(amt)
    if diff:
        request_url += "&difficulty=" + diff
    if catergory:
        request_url += "&catergory=" + catergory
    if type:  # "multiple" "boolean"
        request_url += "&type=" + type
    if encoding:
        request_url += "&encode=" + encoding

    response = requests.post(url=request_url)
    d = response.json()

    if d['response_code'] == 2:
        print('invalid parameter..')
        return 2, None
    elif d['response_code'] == 3:
        print('Session token not found!')
        return 3, None
    elif d['response_code'] == 4:
        print('Empty token. Reset, yeah?')
        _ = requests.post(url=base_url+"?command=reset")
        return 4, None
    elif d['response_code'] == 1 and len(d['results']) == 0:
        return 1, None

    if encoding == "base64":
        decoded_results = dict(d)
        for i in range(len(d['results'])):
            print("d['results'][i]['question'] =",d['results'][i]['question'])
            decoded_results['results'][i]['question'] = base64ToString(d['results'][i]['question'])
            decoded_results['results'][i]['correct_answer'] = base64ToString(d['results'][i]['correct_answer'])
            for j in range(len(d['results'][i]['incorrect_answers'])):
                decoded_results['results'][i]['incorrect_answers'][j] = base64ToString(d['results'][i]['incorrect_answers'][j])
        print(decoded_results)
        return 0, decoded_results['results']

    return 0, d['results']




# def ask_trivia(msg, *args):
#     params = args[0][1:]
#     difficulty = category = type = None
#     # for p in params:
#     #     if
#     # num_questions = 1
#     resp_code, questions = get_trivia_questions(amt=1)
#     #prompts, correct_answers, wrong_answers = [], [], []
#     prompt, correct_answer, wrong_answers = questions[0]['question'], questions[0]['correct_answer'], questions[0]['wrong_answers']
#     for i, s in enumerate(wrong_answers):
#         prompt += "\n({}) {}".format((i, s))
#
#     await self.ntsk.send_message(msg.channel, prompt)
#
#     ans_list = wrong_answers.append(correct_answer)
#     ans_list = [x.lower() for x in ans_list]
#
#     chk = lambda x : x in ans_list
#
#     resp_msg = await self.ntsk.wait_for_message(timeout=8, author=msg.author, check=chk)
#     guess = resp_msg.content
#     if guess.lower() == correct_answer:
#         # correct answer!
#         # add points to profile
#         await ntsk.send_message("That's right! Yay!")
#         return
#     await ntsk.send_message("Aww... You're wrong...")












#if __name__ == "__main__":
    #TOKEN = requests.post(url="https://opentdb.com/api_token.php?command=request")
    #print(TOKEN.json())
    #resp_code, results = get_trivia_questions()
    #print(resp_code)
    #print(results)