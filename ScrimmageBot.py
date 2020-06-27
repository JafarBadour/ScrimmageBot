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
        self.grid = self.make_grid()

    def make_grid(self):
        grid = [['.'] * 7] * 14
        grid[0][3] = 'X'
        grid[13][3] = 'X'
        for p in self.my_pieces:
            x, y = p
            grid[x][y] = 'O'

        for p in self.opponent_pieces:
            x, y = p
            grid[x][y] = 'D'

        return grid

    def is_piece(self, opponent_to, pieces):
        return any(piece == opponent_to for piece in pieces)

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
        return self

    def unpack(self):
        return self.my_pieces, self.opponent_pieces, self.opponent_last_move, \
               self.displacement_transition

    def grid_transpose(self):
        n, m = len(self.grid), len(self.grid[0])
        op, ol, mp, dt = [], (), [], False
        for i in range(n):
            for j in range(m):
                c = self.grid[i][j]
                if c == 'O':
                    mp.append((i, j))
                if c == 'D':
                    op.append((i, j))
        self.opponent_pieces = op
        self.my_pieces = mp
        return self

    def make_move(self, move):  # TODO
        (px, py), (nx, ny) = move
        grid = self.grid
        dxx, dyy = nx - px, ny - py
        sx, sy = nx + dxx, ny + dyy  # second piece
        if grid[nx][ny] != '.':
            grid[sx][sy] = grid[nx][ny]
        grid[nx][ny] = grid[px][py]
        grid[px][py] = '.'
        self.grid_transpose()
        return self


class ScrimmageBot:
    def __init__(self):
        self.model_weights = []
        self.state_logs = []
        self.my_finish_cell = (13, 3)

    def loads_database(self, file_path: str):
        self.model_weights = np.loadtxt(file_path)

    def random_move(self, current_state):
        original_state = State(current_state)
        if self.finish_line(original_state):
            return 'Done'
        import random
        r = random.randint(0, 5)
        p = original_state.my_pieces[r]
        available_moves = []
        for mdx, mdy in zip(dx, dy):
            nx, ny = p[0] + mdx, p[1] + mdy
            if not self.__is_valid_move((p, (nx, ny)), original_state):
                continue
            available_moves.append((p, (nx, ny)))
        r = random.randint(0, len(available_moves))
        return State(current_state).make_move(available_moves[r])

    def finish_line(self, state: State):
        _, op, _, _ = state.unpack()
        return any(piece == self.my_finish_cell in op)

    def process_next_transition(self, depth_minimax):
        pass

    def in_bounds(self, x, y):
        return not (x < 0 or x > 13 or y < 0 or y > 6)

    def __is_valid_move(self, move, original_state):
        pos_from, pos_to = iter(move)
        to_x, to_y = pos_to
        from_x, from_y = pos_from
        if not self.in_bounds(to_x, to_y):
            return False
        dxx = to_x - from_x
        dyy = to_y - from_y
        nx, ny = dxx + to_x, dyy + to_y
        if not self.in_bounds(nx, ny):
            return False

        grid = original_state.make_grid()
        if grid[to_x][to_y] != '.' and (grid[nx][ny] != '.' or abs(dxx) + abs(dyy) == 1):
            return False

        # TO BE DONE


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
