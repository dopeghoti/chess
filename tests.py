#!/usr/bin/python3
import unittest
from color import Color
from chess_board import ChessBoard, Square
from chess_piece import *

class TestColor(unittest.TestCase):
    def test_fg(self):
        result = f"{Color.BLUE('hello')} there"
        self.assertEqual(result, "\x1b[34mhello\x1b[0m there")

    def test_fg_bold(self):
        result = f"{Color.BLUE('hello', bold = True)} there"
        self.assertEqual(result, "\x1b[64mhello\x1b[0m there")

    def test_bg(self):
        result = f"{Color.WHITE('hello', bg=Color.BLUE)} there"
        self.assertEqual(result, "\x1b[44mhello\x1b[0m there")

    def test_bg_bold(self):
        result = f"{Color.WHITE('hello', bold = True, bg = Color.BLUE)} there"
        self.assertEqual(result, "\x1b[67;44mhello\x1b[0m there")

    def test_rgb(self):
        result = f"{Color.rgb(1, 2, 3, 'hello')} there"
        self.assertEqual(result, "\x1b[38;2;1;2;3mhello\x1b[0m there")

    def test_rgb_bold(self):
        result = f"{Color.rgb(1, 2, 3, 'hello', bg = True)} there"
        self.assertEqual(result, "\x1b[48;2;1;2;3mhello\x1b[0m there")

    def test_inline(self):
        result = f'{Color.BLUE.set(fg = True)}hello{Color.reset()}'
        self.assertEqual( result, Color.BLUE('hello') )

    def test_call( self ):
        result = f'{Color.BLUE("hello")} there'
        self.assertEqual( result,  "\x1b[34mhello\x1b[0m there" )        

class TestChessPieces(unittest.TestCase):

    def test_base_class_exceptions(self):
        """
        Verify that the base ChessPiece class cannot be instantiated directly
        and that it enforces color requirements.
        """
        # Attempting to instantiate the base class should fail
        with self.assertRaisesRegex(NotImplementedError, "ChessPiece should not be instantiated directly"):
            ChessPiece('light')

        # CORRECTED: Calling a subclass without the required 'color' argument 
        # should raise a TypeError.
        with self.assertRaises(TypeError):
            Knight()

        # Instantiating any piece with an invalid color should still fail with a ValueError
        with self.assertRaisesRegex(ValueError, "Color must be either 'light' or 'dark'"):
            Pawn('blue')

    def test_piece_equality_and_hash(self):
        """
        Tests the __eq__ and __hash__ methods for chess pieces.
        """
        # Create several piece instances for comparison
        light_rook1 = Rook('light')
        light_rook2 = Rook('light')
        dark_rook = Rook('dark')
        light_knight = Knight('light')

        # 1. Test for equality
        self.assertEqual(light_rook1, light_rook2, "Pieces of same type and color should be equal")
        self.assertTrue(light_rook1 == light_rook2, "Equality operator should work")

        # 2. Test for inequality
        self.assertNotEqual(light_rook1, dark_rook, "Pieces of different colors should not be equal")
        self.assertNotEqual(light_rook1, light_knight, "Pieces of different types should not be equal")
        self.assertNotEqual(light_rook1, "Rook", "Piece should not be equal to a string or other object")
        self.assertFalse(light_rook1 == dark_rook, "Inequality operator should work")

        # 3. Test hashing
        self.assertEqual(hash(light_rook1), hash(light_rook2), "Hashes of equal pieces should be equal")
        self.assertNotEqual(hash(light_rook1), hash(dark_rook), "Hashes of unequal pieces should not be equal")

        # 4. Test set membership (relies on both __eq__ and __hash__)
        piece_set = {light_rook1, dark_rook}
        self.assertIn(light_rook2, piece_set, "An equivalent piece should be found in the set")
        self.assertNotIn(light_knight, piece_set, "A different piece should not be found in the set")


    def test_pawn(self):
        """Tests the Pawn piece."""
        light_pawn = Pawn('light')
        dark_pawn = Pawn('dark')

        # Test attributes
        self.assertEqual(light_pawn.color, 'light')
        self.assertEqual(dark_pawn.color, 'dark')
        self.assertEqual(light_pawn.name, 'pawn')
        self.assertEqual(Pawn.symbol, '') # Pawns have no symbol in algebraic notation

        # Test string representation (glyph)
        self.assertEqual(str(light_pawn), '♙')
        self.assertEqual(str(dark_pawn), '♟')

        # Test representation
        self.assertEqual(repr(light_pawn), 'light pawn')

    def test_rook(self):
        """Tests the Rook piece."""
        light_rook = Rook('light')
        dark_rook = Rook('dark')

        # Test attributes
        self.assertEqual(light_rook.color, 'light')
        self.assertEqual(dark_rook.color, 'dark')
        self.assertEqual(light_rook.name, 'rook')
        self.assertEqual(Rook.symbol, 'R')

        # Test string representation (glyph)
        self.assertEqual(str(light_rook), '♖')
        self.assertEqual(str(dark_rook), '♜')

        # Test representation
        self.assertEqual(repr(dark_rook), 'dark rook')

    def test_knight(self):
        """Tests the Knight piece."""
        light_knight = Knight('light')
        dark_knight = Knight('dark')

        # Test attributes
        self.assertEqual(light_knight.color, 'light')
        self.assertEqual(dark_knight.color, 'dark')
        self.assertEqual(light_knight.name, 'knight')
        self.assertEqual(Knight.symbol, 'N') # 'N' is standard for Knight

        # Test string representation (glyph)
        self.assertEqual(str(light_knight), '♘')
        self.assertEqual(str(dark_knight), '♞')

        # Test representation
        self.assertEqual(repr(light_knight), 'light knight')

    def test_bishop(self):
        """Tests the Bishop piece."""
        light_bishop = Bishop('light')
        dark_bishop = Bishop('dark')

        # Test attributes
        self.assertEqual(light_bishop.color, 'light')
        self.assertEqual(dark_bishop.color, 'dark')
        self.assertEqual(light_bishop.name, 'bishop')
        self.assertEqual(Bishop.symbol, 'B')

        # Test string representation (glyph)
        self.assertEqual(str(light_bishop), '♗')
        self.assertEqual(str(dark_bishop), '♝')

        # Test representation
        self.assertEqual(repr(dark_bishop), 'dark bishop')

    def test_queen(self):
        """Tests the Queen piece."""
        light_queen = Queen('light')
        dark_queen = Queen('dark')

        # Test attributes
        self.assertEqual(light_queen.color, 'light')
        self.assertEqual(dark_queen.color, 'dark')
        self.assertEqual(light_queen.name, 'queen')
        self.assertEqual(Queen.symbol, 'Q')

        # Test string representation (glyph)
        self.assertEqual(str(light_queen), '♕')
        self.assertEqual(str(dark_queen), '♛')

        # Test representation
        self.assertEqual(repr(light_queen), 'light queen')

    def test_king(self):
        """Tests the King piece."""
        light_king = King('light')
        dark_king = King('dark')

        # Test attributes
        self.assertEqual(light_king.color, 'light')
        self.assertEqual(dark_king.color, 'dark')
        self.assertEqual(light_king.name, 'king')
        self.assertEqual(King.symbol, 'K')

        # Test string representation (glyph)
        self.assertEqual(str(light_king), '♔')
        self.assertEqual(str(dark_king), '♚')

        # Test representation
        self.assertEqual(repr(dark_king), 'dark king')

class TestChessBoard(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()

    def test_board_initialization(self):
        self.assertEqual(len(self.board.squares), 64)
        self.assertIsInstance(self.board.squares['a1'], Square)
        self.assertEqual(self.board.squares['a1'].color, 'dark')
        self.assertEqual(self.board.squares['h8'].color, 'dark')
        self.assertEqual(self.board.squares['a8'].color, 'light')


    def test_board_setup(self):
        self.board.setup()
        # Test a few key pieces
        self.assertIsInstance(self.board.squares['a1'].occupant, Rook)
        self.assertEqual(self.board.squares['a1'].occupant.color, 'light')
        self.assertIsInstance(self.board.squares['e8'].occupant, King)
        self.assertEqual(self.board.squares['e8'].occupant.color, 'dark')
        self.assertIsInstance(self.board.squares['d2'].occupant, Pawn)
        self.assertIsNone(self.board.squares['d4'].occupant)

    def test_clear_board(self):
        self.board.setup()
        self.board.clear()
        for square in self.board.squares.values():
            self.assertIsNone(square.occupant)


if __name__ == "__main__":
    unittest.main()
