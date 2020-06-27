import unittest
from ScrimmageBot import ScrimmageBot, State

class TestSum(unittest.TestCase):

    def test_make_grid(self):
        bot = ScrimmageBot()
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
        grid = state.make_grid()
        supposed_to_be = ''.join(open('./grids/starting_move1.txt').readlines())
        print(grid)
        self.assertEqual('\n'.join(''.join(grid)), supposed_to_be, "grids are not equal line 25")



if __name__ == '__main__':
    unittest.main()
