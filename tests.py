import unittest
from ScrimmageBot import ScrimmageBot, State, dx, dy

state1 = {
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

state2 = {
    'originalPanel': {
        'white': [(6, 2), (6, 3), (6, 4)],
        'black': [(7, 2), (7, 3), (7, 4)]
    },
    'newPanel': {
        'white': [(6, 2), (5, 2), (6, 4)],
        'black': [(7, 2), (7, 3), (6, 3)]
    },
    'transition': {
        'from': {'reel': 5, 'row': 2},
        'to': {'reel': 3, 'row': 6}
    }
}


def read_gridfromfile(filepath):
    f = open('grids/' + filepath)
    res = f.readlines()
    f.close()
    return res


class TestSum(unittest.TestCase):


    def test_is_piece(self):
        state = State().set_state(state1,'white')
        self.assertTrue(all(state.is_piece(p, state.my_pieces) for p in state.my_pieces))

    def test_un_pack(self):
        state = State().set_state(state1,'white')
        mp, op, ol, dt = state.unpack()
        self.assertEqual(mp, list(sorted(state1['newPanel']['white'])), "test_un_pack mp != rmp")
        self.assertEqual(op, list(sorted(state1['newPanel']['black'])), "test_un_pack op != rop")
        transition = state1['transition']
        move = (transition['from']['row'], transition['from']['reel']), (
            transition['to']['row'], transition['to']['reel'])
        self.assertEqual(ol, move, "test_un_pack ol != move")


    def test_grid_transpose(self):
        state = State().set_state(state1,'white')

        rmp, rop, _, _ = state.unpack()

        mp, op, _, _ = state.grid_transpose(state.make_grid()).unpack()

        self.assertEqual(op, rop)
        self.assertEqual(mp, rmp)

    def test_make_move(self):
        state = State().set_state(state1,'white')
        state = state.make_move(((6, 4), (7, 4)))
        self.assertEqual(state.grid_to_str(state.make_grid()),
                         ''.join(read_gridfromfile('gridmove2.txt')), " test_make_move")

    def test_bot_is_valid(self):
        bot = ScrimmageBot('white')
        bot.loads_database('database.db')
        state = State().set_state(state1,'white')

        accepted_moves = [
            ((5, 2), (4, 2)),
            ((6, 2), (7, 3)),
            ((6, 4), (7, 3)),
            ((6, 4), (5, 4)),
            ((6, 4), (7, 4))
        ]
        rejected_moves = []
        for i in range(len(dx)):
            for p in state.my_pieces:
                x, y = p
                x = x + dx[i]
                y = y + dy[i]
                move = (p, (x, y))
                if move in accepted_moves:
                    continue
                rejected_moves.append(move)

        self.assertTrue(all(bot.is_valid_move(move, state) for move in accepted_moves),
                        'Some accepted moves are rejected test_bot_is_valid')
        print(state.displacement_transition)
        for move in rejected_moves:
            if bot.is_valid_move(move, state):
                print('Rej/AC ', move)
        self.assertFalse(any(bot.is_valid_move(move, state) for move in rejected_moves),
                         'Some rejected moves are accepted test_bot_is_valid')

    def test_bot_is_valid_borders(self):
        grid = read_gridfromfile('grid3.txt')
        # print(grid)
        state = State().grid_transpose(grid)
        # print(state.my_pieces, state.opponent_last_move, state.opponent_pieces)
        bot = ScrimmageBot('white')
        rejected_moves = []
        for ddx, ddy in zip(dx,dy):
            rejected_moves.append(((0,0),(ddx, ddy)))
            rejected_moves.append(((5,0),(ddx, ddy)))
            rejected_moves.append(((0,5),(ddx, ddy)))
            rejected_moves.append(((6,6),(ddx, ddy)))
        self.assertFalse(any(bot.is_valid_move(move, state) for move in rejected_moves), "Some rejected moves on the border are accepted")
        self.assertFalse(bot.is_valid_move(((1,2),(0,3)),state),"This move should be illegal")


    def test_make_random_move_bot(self):
        bot = ScrimmageBot('white')
        bot.loads_database('database.db')
        print(bot.optimal_move_draft(state1))


    # def test_make_move_start(self):
    #     move = ((6, 2), (7, 3))
    #     bot = ScrimmageBot()
    #     state = State().set_state(state, 'white')
if __name__ == '__main__':
    unittest.main()
