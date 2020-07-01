import numpy as np
import random

dx = [1, 1, -1, -1, 1, -1]  # rows
dy = [1, -1, -1, 1, 0, 0]  # cols / reels # these are all possible moves regardless of


# regardless of constraints

class State:
    def __init__(self, another_state=None):
        op, ol, mp, dt, mlv, bc = [], (), [], False, (), 'white'
        if another_state:
            op = another_state.opponent_pieces
            ol = another_state.opponent_last_move
            mp = another_state.my_pieces
            dt = another_state.displacement_transition
            mlv = another_state.my_last_move
            bc = another_state.bot_col
        self.opponent_pieces = op
        self.opponent_last_move = ol
        self.my_pieces = mp
        self.displacement_transition = dt
        self.my_last_move = mlv
        self.bot_col = bc
        self.grid = self.make_grid()

    def make_grid(self):
        grid = [['.'] * 7 for i in range(14)]
        colbot, colopp = 'O', 'D'
        if self.bot_col == 'black':
            colbot, colopp = 'D', 'O'
        grid[0][3] = 'X'
        grid[13][3] = 'X'
        for p in self.my_pieces:
            x, y = p
            grid[x][y] = colbot

        for p in self.opponent_pieces:
            x, y = p
            grid[x][y] = colopp

        return grid

    def is_piece(self, opponent_to, pieces):
        return any(piece == opponent_to for piece in pieces)

    def set_state(self, json_data: dict, bot_col: str):
        original_panel = json_data['originalPanel']
        new_panel = json_data['newPanel']
        # print(json_data.keys())
        a, b = ('black', 'white')
        if bot_col != a:
            a, b = b, a
        self.bot_col = bot_col
        self.my_pieces = list(sorted(original_panel[a]))
        self.opponent_pieces = list(sorted(original_panel[b]))
        if 'transition' in json_data.keys():
            transition = json_data['transition']
            if 'from' in transition.keys():
                move_from, move_to = (transition['from']['row'], transition['from']['reel']), \
                                     (transition['to']['row'], transition['to']['reel'])
                self.opponent_last_move = (move_from, move_to)
                self.displacement_transition = self.is_piece(move_to, self.my_pieces)
            else:
                self.opponent_last_move = ((-3, -3), (-4, -3))  # dummy positions that wont be considered
                self.displacement_transition = False

        # Setting new state
        self.my_pieces = list(sorted(new_panel[a]))
        self.opponent_pieces = list(sorted(new_panel[b]))
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
        colbot, colopp = 'O', 'D'
        if self.bot_col == 'black':
            colbot, colopp = colopp, colbot
        for i in range(n):
            for j in range(m):
                try:
                    c = grid[i][j]
                except:
                    print(i, j, 'Err')
                if c == colbot:
                    mp.append((i, j))
                if c == colopp:
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

        if grid[nx][ny] != '.' and grid[nx][ny] != 'X':
            # if not (nx == 0 and ny == 3):  # last edit
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

    def show_grid(self, grid):
        imp_grid = grid
        for i in range(len(imp_grid)):
            space = ' '
            if i >= 10:
                space = ''
            imp_grid[i] = str(i) + space + ''.join(imp_grid[i])

        res = '\n'.join([''.join(x) for x in reversed(imp_grid)])
        res = res + '\n  0123456'
        return res

    def json_response(self):
        white, black = self.my_pieces, self.opponent_pieces
        if self.bot_col == 'black':
            black, white = white, black
        return {
            'black': black,
            'white': white
        }

    def transition_json(self):
        if not self.my_last_move:
            return {}
        (xf, yf), (xt, yt) = self.my_last_move
        return {
            'from': {
                'reel': yf,
                'row': xf
            },
            'to': {
                'reel': yt,
                'row': xt
            }
        }

    def alter_turn(self, last_move):
        self.my_pieces, self.opponent_pieces = self.opponent_pieces, self.my_pieces
        self.opponent_last_move = last_move
        # TODO
        return self


class ScrimmageBot:
    def __init__(self, bot_col: str):
        self.model_weights = []
        self.state_logs = []
        self.my_finish_cell = (13, 3) if bot_col == 'white' else (0, 3)
        self.bot_col = bot_col

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

    def random_move(self, json_state):
        current_state = State().set_state(json_state, self.bot_col)
        original_state = State(current_state)
        if self.finish_line(original_state):
            return 'Done'

        available_moves = self.get_available_moves(original_state)

        r = random.randint(0, len(available_moves))
        print('Move taken by bot is :', available_moves[r])
        return State(current_state).make_move(available_moves[r])  # .alter_turn(available_moves[r])

    def optimal_move_draft(self, json_state):
        current_state = State().set_state(json_state, self.bot_col)
        print('state dt', current_state.displacement_transition)
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
        optimal_move = available_moves[optimal_index]
        print(f'Move with score {optimal_score} : Col {self.bot_col} :play a move --->{optimal_move}')
        state = State(current_state).make_move(optimal_move)
        return state

    def finish_line(self, state: State):
        _, op, _, _ = state.unpack()
        return any(piece == self.my_finish_cell for piece in op)

    def is_winner(self, state : State):
        mp,_,_,_ = state.unpack()
        return any(piece == (0,3) or piece == (13,3) for piece in mp)

    def process_next_transition(self, depth_minimax):
        pass

    def in_bounds(self, x, y):
        return not (x < 0 or x > 13 or y < 0 or y > 6)

    def on_borders(self, x, y):
        return x == 0 or x == 13 or y == 0 or y == 6

    def score_state(self, state: State):
        grid = state.make_grid()

        rweights = self.model_weights
        weights = rweights[::-1]
        n, m = len(grid), len(grid[0])
        score = 0
        colbot, colopp = 'O', 'D'
        if self.bot_col == 'black':
            weights, rweights = rweights, weights
            colbot, colopp = colopp, colbot
        for i in range(n):
            for j in range(m):
                if grid[i][j] == colbot:
                    score += weights[i][j]
                elif grid[i][j] == colopp:
                    score -= rweights[i][j]

        for a in state.my_pieces:
            for b in state.my_pieces:
                ax, ay = a
                bx, by = b
                score -= 0 * max(abs(ax - bx), abs(ay - by))  # ** 2
                # TODO

        for a in state.opponent_pieces:
            for b in state.opponent_pieces:
                ax, ay = a
                bx, by = b
                score += 0 * max(abs(ax - bx), abs(ay - by))  # ** 2
                # TODO
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
        if abs(dxx) + abs(dyy) > 2 or abs(dxx) + abs(dyy) < 1:
            return False
        if not self.in_bounds(to_x, to_y):
            return False
        if abs(dyy) == 1 and dxx == 0:
            return False
        grid = original_state.make_grid()
        if grid[to_x][to_y] == 'X':
            return abs(dxx) + abs(dyy) == 1
        if self.on_borders(to_x, to_y):
            return False

        colbot, colopp = 'O', 'D'
        if original_state.bot_col == 'black':
            colbot, colopp = colopp, colbot

        if grid[from_x][from_y] != colbot:
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
            'white': [(6, 2), (6, 3), (6, 4)],
            'black': [(7, 2), (7, 3), (7, 4)]
        },
        'newPanel': {
            'white': [(6, 2), (5, 2), (6, 4)],
            'black': [(7, 2), (7, 3), (6, 3)]
        },
        'transition': {
            'from': {'reel': 4, 'row': 7},
            'to': {'reel': 3, 'row': 6}
        }
    }
    state = State().set_state(state, 'white')
    scrimmage_bot.is_valid_move(((6, 2), (7, 3)), state)
