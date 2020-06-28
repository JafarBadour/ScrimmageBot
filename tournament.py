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
    state = State().set_state(starting_state)
    print(bot.optimal_move_draft(state))


starting_state = read_gridfromfile('starting_grid.txt')

for i in range(10):
    time.sleep(1.1)
