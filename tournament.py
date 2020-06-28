from ScrimmageBot import ScrimmageBot, State
import time


def read_gridfromfile(filepath):
    f = open('grids/' + filepath)
    res = f.readlines()
    f.close()
    return res


def create_bot():
    bot = ScrimmageBot()
    bot.loads_database('database.db')
    return bot


OG = create_bot()
DT = create_bot()
starting_state = State().grid_transpose(read_gridfromfile('starting_grid.txt'))
print('Tournament is starting!')
state = State(starting_state)
print(state.json_response())
print(state.transition_json())
print(state.displacement_transition)
json_data = {
    'originalPanel': state.json_response(),
    'newPanel': state.json_response(),
}
print(json_data)
for i in range(30):
    time.sleep(1.1)
    print('Offense bot is playing')
    state = State().set_state(json_data, 'white')
    new_state = OG.optimal_move_draft(state)
    print(new_state.show_grid(new_state.make_grid()))

    # time.sleep(3)
    print('Defensive bot is playing')
    json_data = {
        'originalPanel': state.json_response(),
        'newPanel': new_state.json_response(),
        'transition': new_state.transition_json()
    }
    print(json_data)
    state = State().set_state(json_data, 'black')
    print(state.displacement_transition,'DISPLACEMENT TRANSITION')
    print(state.opponent_last_move, 'Opponent last move')
    print('DT pieces:', state.my_pieces)
    new_state = DT.optimal_move_draft(state)
    # time.sleep(3)
    print(new_state.show_grid(new_state.make_grid()))


