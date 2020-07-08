from flask import Flask, render_template, redirect, url_for, request, session, jsonify, Response
import json

app = Flask(__name__)

from ScrimmageBot import ScrimmageBot, State
import time


def read_gridfromfile(filepath):
    f = open('grids/' + filepath)
    res = f.readlines()
    f.close()
    return res


def create_bot(bot_col):
    bot = ScrimmageBot(bot_col)
    bot.loads_database('database.db')
    return bot


def get_json_data(original_state: State, new_state: State, last_moves : list):
    return {
        'originalPanel': original_state.json_response(),
        'newPanel': new_state.json_response(),
        'transitions':[new_state.transition_json()]
    }


@app.route('/')
def hello_world():
    routes = [
        '<h2>/ogscrimmagebotpost</h2> You post an http request to the bot (white bot) make sure that this bot will play as white or OG following the criteria in the end',
        '<h2>/dtscrimmagebotpost</h2> You post an http request to the bot (black bot) make sure that this bot will play as black or DT following the criteria in the end']
    routes.append('<br>'.join(open('httpRequestForm.txt', 'r').readlines()))
    routes = '<br>'.join(routes)
    return f'<h1>Hello this is the ScrimmageBot the following routes are useful {routes}</h1>'


@app.route('/ogscrimmagebotpost/<string:difficulty>', methods=['POST'])
def og_bot_post(difficulty):
    return play_bot('white', difficulty)


@app.route('/dtscrimmagebotpost/<string:difficulty>', methods=['POST'])
def dt_bot_post(difficulty):
    return play_bot('black',difficulty)


def swap_elements_in_array(json_data):
    keys = ['newPanel', 'originalPanel']

    for key in keys:
        black = json_data[key]['black']
        white = json_data[key]['white']
        black = list(map(lambda x: (x[1], x[0]), black))
        white = list(map(lambda x: (x[1], x[0]), white))
        json_data[key]['black'] = black
        json_data[key]['white'] = white
    return json_data

def play_bot(col: str, difficulty : str):
    req = request
    data = (request.data)
    json_data = json.loads(data.decode())
    json_data = swap_elements_in_array(json_data)
    bot = create_bot(col)

    # = json.loads(req.data.decode())
    print(data)
    transitions = json_data['transitions']
    json_data['transition'] = json_data['transitions'][-1]
    last_moves =  json_data['transitions']

    starting_state = State().set_state(json_data, col)
    if difficulty == 'medium' or difficulty == 'hard':
        bot_attacked_state = bot.optimal_move_draft(json_data)
    elif difficulty == 'easy':
        bot_attacked_state = bot.random_move(json_data)
    json_data = get_json_data(starting_state, bot_attacked_state, last_moves)

    if bot.is_winner(bot_attacked_state):
        print('Wohooo bot won')

    resp = jsonify(swap_elements_in_array(json_data))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,ssl_context='adhoc')

#######
# 'originalPanel': {
#           'white': [[6, 2], [6, 3], [6, 4]],
#           'black': [[7, 2], [7, 3], [7, 4]]
#       },
#       'newPanel': {
#           'white': [[6, 2], [5, 2], [6, 4]],
#           'black': [[7, 2], [7, 3], [6, 3]]
#       },
#       'transitions': [{'from': {'reel': 4, 'row': 7},
#           'to': {'reel': 3, 'row': 6}}, {'from': {'reel': 4, 'row': 7},
#           'to': {'reel': 3, 'row': 6}}]
#           'from': {'reel': 4, 'row': 7},
#           'to': {'reel': 3, 'row': 6}
#       }}));
