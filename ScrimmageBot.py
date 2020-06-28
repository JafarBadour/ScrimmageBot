import numpy as np
import random

dx = [1, 1, -1, -1, 1, -1]  # rows
dy = [1, -1, -1, 1, 0, 0]  # cols / reels # these are all possible moves regardless of


# regardless of constraints

class State:
    def __init__(self, another_state=None):
        op, ol, mp, dt, mlv = [], (), [], False, ()
        if another_state:
            op = another_state.opponent_pieces
            ol = another_state.opponent_last_move
            mp = another_state.my_pieces
            dt = another_state.displacement_transition
            mlv = another_state.my_last_move
        self.opponent_pieces = op
        self.opponent_last_move = ol
        self.my_pieces = mp
        self.displacement_transition = dt
        self.grid = self.make_grid()
        self.my_last_move = mlv

    def make_grid(self):
        grid = [['.'] * 7 for i in range(14)]

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
        # print(json_data.keys())
        self.my_pieces = list(sorted(original_panel['my_pieces']))
        self.opponent_pieces = list(sorted(original_panel['opponents_pieces']))
        if 'transition' in json_data.keys():
            transition = json_data['transition']
            move_from, move_to = (transition['from']['row'], transition['from']['reel']), \
                                 (transition['to']['row'], transition['to']['reel'])
            self.opponent_last_move = (move_from, move_to)
            self.displacement_transition = self.is_piece(move_to, self.my_pieces)



        # Setting new state
        self.my_pieces = list(sorted(new_panel['my_pieces']))
        self.opponent_pieces = list(sorted(new_panel['opponents_pieces']))
        self.my_last_move = ()
        return self

    def unpack(self):
        return self.my_pieces, self.opponent_pieces, self.opponent_last_move, \
               self.displacement_transition

    def grid_transpose(self, grid):
        grid = list(map(lambda x: x.replace('\n', '') if isinstance(x, str) else x, grid))
        n, m = len(grid), len(grid[0])
        # print(n,m)
        op, ol, mp, dt = [], (), [], False
        for i in range(n):
            for j in range(m):
                try:
                    c = grid[i][j]
                except:
                    print(i, j, 'Err')
                if c == 'O':
                    mp.append((i, j))
                if c == 'D':
                    op.append((i, j))
        self.opponent_pieces = list(sorted(op))
        self.my_pieces = list(sorted(mp))
        return self

    def make_move(self, move):  # TODO
        (px, py), (nx, ny) = move
        dt = False
        grid = self.make_grid()
        dxx, dyy = nx - px, ny - py
        sx, sy = nx + dxx, ny + dyy  # second piece

        if grid[nx][ny] != '.':
            if not (nx == 0 and ny == 3): # last edit
                grid[sx][sy] = grid[nx][ny]
            dt = True

        grid[nx][ny] = grid[px][py]
        grid[px][py] = '.'
        me = State().grid_transpose(grid)
        me.displacement_transition = dt
        me.my_last_move = move
        return me

    def grid_to_str(self, grid):
        return '\n'.join([''.join(x) for x in grid])


class ScrimmageBot:
    def __init__(self):
        self.model_weights = []
        self.state_logs = []
        self.my_finish_cell = (13, 3)

    def loads_database(self, file_path: str):
        self.model_weights = np.loadtxt(file_path)

    def get_available_moves(self, current_state):  # TODO #TOTEST

        available_moves = []
        for p in current_state.my_pieces:
            for mdx, mdy in zip(dx, dy):
                nx, ny = p[0] + mdx, p[1] + mdy
                if not self.is_valid_move((p, (nx, ny)), current_state):
                    continue
                available_moves.append((p, (nx, ny)))
        return available_moves

    def random_move(self, current_state):
        original_state = State(current_state)
        if self.finish_line(original_state):
            return 'Done'

        available_moves = self.get_available_moves(original_state)

        r = random.randint(0, len(available_moves))
        print('Move taken by bot is :', available_moves[r])
        return State(current_state).make_move(available_moves[r])

    def optimal_move_draft(self, current_state):
        original_state = State(current_state)
        if self.finish_line(original_state):
            return 'Done'

        available_moves = self.get_available_moves(original_state)
        boards = [State(current_state).make_move(move) for move in available_moves]
        scores = [self.score_state(board) for board in boards]
        sorted_scoreboard = list(reversed(sorted(zip(scores, list(range(len(boards)))))))
        # for score,i in sorted_scoreboard:
        #     print(score, ' SCORE')
        #     print(boards[i].grid_to_str(boards[i].make_grid()))
        optimal_score, optimal_index = sorted_scoreboard[0]
        print(f'Move with score {optimal_score} play a move --->')
        return State(current_state).make_move(available_moves[0])

    def finish_line(self, state: State):
        _, op, _, _ = state.unpack()
        return any(piece == self.my_finish_cell for piece in op)

    def process_next_transition(self, depth_minimax):
        pass

    def in_bounds(self, x, y):
        return not (x < 0 or x > 13 or y < 0 or y > 6)

    def on_borders(self, x, y):
        return x == 0 or x == 13 or y == 0 or y == 6

    def score_state(self, state: State):
        grid = state.make_grid()

        weights = self.model_weights
        rweights = weights[::-1]
        n, m = len(grid), len(grid[0])
        score = 0
        for i in range(n):
            for j in range(m):
                if grid[i][j] == 'O':
                    score += weights[i][j]
                elif grid[i][j] == 'D':
                    score -= rweights[i][j]

        for a in state.my_pieces:
            for b in state.my_pieces:
                ax, ay = a
                bx, by = b
                score -= (ax - bx) ** 2 + (ay - by) ** 2

        for a in state.opponent_pieces:
            for b in state.opponent_pieces:
                ax, ay = a
                bx, by = b
                score += (ax - bx) ** 2 + (ay - by) ** 2
        return score

    def is_valid_move(self, move, original_state):
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
        if abs(dyy) == 1 and dxx == 0:
            return False
        grid = original_state.make_grid()
        if grid[to_x][to_y] == 'X':
            return abs(dxx) + abs(dyy) == 1
        if self.on_borders(to_x, to_y):
            return False
        if grid[from_x][from_y] != 'O':
            return False

        to_C = grid[to_x][to_y]
        if to_C != '.' and (grid[nx][ny] != '.' or abs(dxx) + abs(dyy) == 1):
            return False
        if abs(dxx) + abs(dyy) == 2 and grid[to_x][to_y] == '.':
            return False

        if original_state.displacement_transition:
            opl = original_state.opponent_last_move
            (ofx, ofy), (otx, oty) = opl
            dxx = otx - ofx
            dyy = oty - ofy
            sx = otx + dxx
            sy = oty + dyy
            # print(sx, sy, otx, oty)
            if move == ((sx, sy), (otx, oty)):
                return False

        return True
        # TO BE DONE


if __name__ == '__main__':
    # np.savetxt`('database.db', np.array([[1,2,3],[1,2,3],[1,2,5]]))
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
    state = State().set_state(state)
    scrimmage_bot.is_valid_move(((6, 2), (7, 3)), state)
