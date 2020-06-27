import numpy as np

dx = [1, 1, -1, -1, 1, -1]  # rows
dy = [1, -1, -1, 1, 0, 0]  # cols / reels # these are all possible moves regardless of
        # regardless of constraints

class State:
    def __init__(self, another_state=None):
        op, ol, mp, dt = [], (), [], False
        if another_state:
            op = another_state.opponent_pirces
            ol = another_state.opponent_last_move
            mp = another_state.my_pieces
            dt = another_state.displacement_transition
        self.opponent_pieces = op
        self.opponent_last_move = ol
        self.my_pieces = mp
        self.displacement_transition = dt

    def set_state(self, json_data: dict):
        original_panel = json_data['originalPanel']
        new_panel = json_data['newPanel']
        transition = json_data['transition']

        self.my_pieces = original_panel['my_pieces']
        self.opponent_pieces = original_panel['opponents_pieces']

        move_from, move_to = (transition['from']['row'], transition['from']['reel']), \
                             (transition['to']['row'], transition['to']['reel'])
        self.opponent_last_move = (move_from, move_to)
        self.displacement_transition = self.is_piece(move_to, self.my_pieces)

        # Setting new state

        self.my_pieces = original_panel['my_pieces']
        self.opponent_pieces = original_panel['opponents_pieces']



class ScrimmageBot:
    def __init__(self):
        self.model_weights = []
        self.state_logs = []

    def is_piece(self, opponent_to, pieces):
        return any(piece == opponent_to for piece in pieces)

    def loads_database(self, file_path: str):
        self.model_weights = np.loadtxt(file_path)

    def calc(self, current_state):

        original_state = State(current_state)


    def finish_line(self, ):

    # def #process_next_transition(self, depth_minimax):


    def __is_valid_move(self, move):
        pos_from, pos_to = iter(move)



if __name__ == '__main__':
    # np.savetxt('database.db', np.array([[1,2,3],[1,2,3],[1,2,5]]))
    scrimmage_bot = ScrimmageBot()
    scrimmage_bot.loads_database('database.db')
    state = {
        'originalPanel': {
            'my_pieces': [(6, 2), (6, 3), (6, 4)],
            'opponents_pieces': [(7, 2), (7, 3), (7, 4)]
        },
        'newPanel': {
            'my_pieces': [(6, 2), (5, 2), (6, 4)],
            'opponents_pieces': [(7, 2), (7, 3), (6, 3)]
        },
        'transition': {
            'from': {'reel': 4, 'row': 7},
            'to': {'reel': 3, 'row': 6}
        }
    }
    state = State()
    state.set_state(state)

    print(state.my_pieces)
