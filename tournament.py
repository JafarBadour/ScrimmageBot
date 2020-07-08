from ScrimmageBot import ScrimmageBot, State
import time
from app import swap_elements_in_array
import requests as req
import json


def read_gridfromfile(filepath):
    f = open('grids/' + filepath)
    res = f.readlines()
    f.close()
    return res


def create_bot(bot_col):
    bot = ScrimmageBot(bot_col)
    bot.loads_database('database.db')
    return bot


def get_json_data(original_state: State, new_state: State):
    return {
        'originalPanel': original_state.json_response(),
        'newPanel': new_state.json_response(),
        'transitions': [{}, new_state.transition_json()]
    }

#
# print(swap_elements_in_array({
#     'originalPanel': {'black': [(1, 2), (2, 3), (3, 4)], 'white': [(6, 7), (9, 8), (10, 12)]},
#     'newPanel':{'black': [(1, 2), (2, 3), (3, 4)], 'white': [(6, 7), (9, 8), (10, 12)]},
#     'transitions': [{}]
# }))
# exit(0)

OG = create_bot('white')
DT = create_bot('black')
starting_state = State().grid_transpose(read_gridfromfile('starting_grid.txt'))
# starting_state = State().grid_transpose(read_gridfromfile('ending_grid.txt'))
print('Tournament is starting!')
# state = State(starting_state)
#
# print(starting_state.show_grid(starting_state.make_grid()))
# print(starting_state.my_pieces, starting_state.opponent_pieces)
#
# print('valid', DT.is_valid_move(((12,3),(13,3)), starting_state))
# print('avail', DT.get_available_moves(starting_state))
# print(DT.score_state(starting_state))
# print(OG.model_weights)
# json_data = get_json_data(starting_state)
#
# final = (DT.optimal_move_draft(json_data))
# print(final.show_grid(final.make_grid()))
# exit(0)
# print(OG.model_weights)
# print(DT.model_weights)

json_data = get_json_data(starting_state, starting_state)
print(starting_state.show_grid(starting_state.make_grid()))

for i in range(1000):
    # time.sleep(2.2)
    print(json_data)
    res = req.post('https://jeffbadour.ml/dtscrimmagebotpost/hard',json=swap_elements_in_array(json_data))
    # res = req.post('http://0.0.0.0:5000/ogscrimmagebotpost/easy', json=swap_elements_in_array(json_data))
    print('Header', res.headers.keys())
    print(res.content)
    # exit(0)
    json_data = swap_elements_in_array(res.json())
    print(json_data)
    starting_state = State().set_state(json_data=json_data, bot_col='black')
    if ScrimmageBot('black').is_winner(starting_state):
        print('Wohooo bot won')
        break
    print(starting_state.show_grid(starting_state.make_grid()))
    print('-----------------------------\n')
    # print(json_data)
    # time.sleep(2.2)
    # print(og_attacked_state.my_pieces, og_attacked_state.opponent_pieces, og_attacked_state.my_last_move, og_attacked_state.opponent_last_move)

    a, b, c, d = map(int, input(
        'Write the move against the bot a,b,c,d where (a,b) is where it was and and (c,d) where it is gonna be:').split(
        ','))
    # a,b,c,d = 5,2,6,3

    print(json_data)

    this_state = State().set_state(json_data, 'black')
    print(this_state.opponent_last_move)
    print(this_state.displacement_transition)
    print(DT.is_valid_move(((a, b), (c, d)), this_state))
    while not DT.is_valid_move(((a, b), (c, d)), this_state):
        a, b, c, d = map(int, input('Do it again a,b,c,d').split(','))
    this_state = this_state.make_move(((a, b), (c, d)))

    print(this_state.show_grid(this_state.make_grid()))
    json_data = get_json_data(starting_state, this_state)
    print(json_data)
    if DT.is_winner(this_state):
        print('Sad bot lost')
    print('-----------------------------\n')
    # print(json_data)
    # input()
