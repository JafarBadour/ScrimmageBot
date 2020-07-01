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


def get_json_data(original_state: State, new_state: State):
    return {
        'originalPanel': original_state.json_response(),
        'newPanel': new_state.json_response(),
        'transition': new_state.transition_json()
    }


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
for i in range(1000):
    # time.sleep(2.2)
    og_attacked_state = OG.optimal_move_draft(json_data)
    json_data = get_json_data(starting_state, og_attacked_state)
    starting_state = og_attacked_state
    if OG.is_winner(starting_state):
        print('Wohooo bot won')
        break
    print(og_attacked_state.show_grid(og_attacked_state.make_grid()))
    print('-----------------------------\n')
    # print(json_data)
    # time.sleep(2.2)
    # print(og_attacked_state.my_pieces, og_attacked_state.opponent_pieces, og_attacked_state.my_last_move, og_attacked_state.opponent_last_move)
    a, b, c, d = map(int,input(
        'Write the move against the bot a,b,c,d where (a,b) is where it was and and (c,d) where it is gonna be:').split(','))

    this_state = State().set_state(json_data, 'black')
    print(this_state.opponent_last_move)
    while not DT.is_valid_move(((a, b), (c, d)), this_state):
        a, b, c, d  = map(int,input('Do it again a,b,c,d').split(','))
    this_state = this_state.make_move(((a,b),(c,d)))

    print(this_state.show_grid(this_state.make_grid()))
    json_data = get_json_data(starting_state, this_state)
    print(json_data)
    if DT.is_winner(this_state):
        print('Sad bot lost')
    print('-----------------------------\n')
    # print(json_data)
    # input()
