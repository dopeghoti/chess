#!/usr/bin/python3
import unittest
from color import Color
from chess_board import ChessBoard, Square
from chess_move import *
from chess_piece import *
from chess_exception import *

from unittest import mock
from io import StringIO

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

        # Calling a subclass without the required 'color' argument should raise a TypeError.
        with self.assertRaises(TypeError):
            Knight() # type: ignore since Pylance doesn't like raising excpetions in purpose

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
        self.assertEqual(repr(light_pawn), 'Pawn( "light" )')

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
        self.assertEqual(repr(dark_rook), 'Rook( "dark" )')

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
        self.assertEqual(repr(light_knight), 'Knight( "light" )')

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
        self.assertEqual(repr(dark_bishop), 'Bishop( "dark" )')

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
        self.assertEqual(repr(light_queen), 'Queen( "light" )')

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
        self.assertEqual(repr(dark_king), 'King( "dark" )')

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
        self.assertIsInstance(self.board.get_piece('a1'), Rook)
        self.assertEqual(self.board.get_piece('a1').color, 'light') # type: ignore
        self.assertIsInstance(self.board.get_piece('e8'), King)
        self.assertEqual(self.board.get_piece('e8').color, 'dark') # type: ignore
        self.assertIsInstance(self.board.get_piece('d2'), Pawn)
        self.assertIsNone(self.board.get_piece('d4'))

    def test_clear_board(self):
        self.board.setup()
        self.board.clear()
        for square in self.board.squares.values():
            self.assertIsNone(square.contains())

    def test_board_moving_pieces(self): 
        # This is just actually the moving if pieces, not rules validataion.
        # Simply, can we move a piece from place to place on the board?
        self.board.setup()
        self.board.move_piece( 'a1', 'd4' )
        self.board.move_piece( 'h1', 'e4' )
        self.board.move_piece( 'a8', 'd5' )
        self.board.move_piece( 'h8', 'e5' )
        self.assertIsNot( any( ( 
            self.board['a1'].is_occupied(), 
            self.board['h1'].is_occupied() , 
            self.board['a8'].is_occupied(), 
            self.board['h8'].is_occupied() 
            ) ), True, "Pieces should have been moved." )
        self.assertIsInstance(self.board.get_piece('d4'), Rook)
        self.assertIsInstance(self.board.get_piece('e4'), Rook)
        self.assertIsInstance(self.board.get_piece('d5'), Rook)
        self.assertIsInstance(self.board.get_piece('e5'), Rook)

class TestEnPassant(unittest.TestCase):

    def setUp(self):
        self.board = ChessBoard()
        self.board.clear()

    def test_light_captures_dark_en_passant(self):
        self.board.setup()

        move_sequence = [
            'a2a4',
            'g8h6',
            'a4a5',
            'b7b5',
            'a5xb5'
        ]
        # Set up the en passant capture
        for move in move_sequence[:-1]:
            cm = ChessMove.from_long_notation( self.board, move )
            cm.execute()
        # Now we can capture en passant
        cm = ChessMove.from_long_notation( self.board, move_sequence[-1])
        self.assertIsInstance( cm, ChessCapture )
        captured = cm.execute()
        self.assertIsNotNone(captured, "Capture should have occurred")
        self.assertTrue(self.board['b6'].is_occupied(), "Capturing pawn should be on e6")
        self.assertFalse(self.board['b5'].is_occupied(), "Square e5 should be empty after capture")

    def test_dark_captures_light_en_passant(self):
        self.board.setup()

        move_sequence = [
            'g1h3',
            'b7b5',
            'h3g1',
            'b5b4',
            'c2c4',
            'b4c4'
        ]
        # Set up the en passant capture
        for move in move_sequence[:-1]:
            cm = ChessMove.from_long_notation( self.board, move )
            cm.execute()
        # Now we can capture en passant
        cm = ChessMove.from_long_notation( self.board, move_sequence[-1])
        self.assertIsInstance( cm, ChessCapture )
        captured = cm.execute()
        self.assertIsNotNone(captured, "Capture should have occurred")
        self.assertTrue(self.board['c3'].is_occupied(), "Capturing pawn should be on e6")
        self.assertFalse(self.board['c4'].is_occupied(), "Square e5 should be empty after capture")

    def test_en_passant_invalid_after_delay(self):
        self.board['e7'].place(Pawn('dark'))
        self.board['d5'].place(Pawn('light'))

        self.board.move_piece( 'e7', 'e5' )
        self.board['e5'].occupant.vulnerable = True
        self.board.end_turn()  # light's turn
        self.board.end_turn()  # back to dark, vulnerability expired

        move = ChessCapture(self.board, 'd5', 'e5' )
        with self.assertRaises(ChessCannotCaptureOutsideCapturePatternException):
            move.validate()

    def test_en_passant_invalid_wrong_square(self):
        self.board['e7'].place(Pawn('dark'))
        self.board['c5'].place(Pawn('light'))

        self.board.move_piece( 'e7', 'e5' )
        self.board['e5'].occupant.vulnerable = True

        move = ChessCapture(self.board,  'c5', 'e5')  # too far
        with self.assertRaises(ChessCannotCaptureOutsideCapturePatternException):
            move.validate()

class TestGeneralCaptures(unittest.TestCase):

    def setUp(self):
        self.board = ChessBoard()
        self.board.clear()

    def test_pawn_captures_diagonally(self):
        self.board['e4'].place(Pawn('light'))
        self.board['d5'].place(Pawn('dark'))

        move = ChessCapture(self.board, 'e4', 'd5')
        self.assertTrue(move.validate(), "Pawn should be able to capture diagonally")
        captured = move.execute()
        self.assertIsNotNone(captured)
        self.assertTrue(self.board['d5'].is_occupied())
        self.board.clear()  # Clear the board for next test

    def test_pawn_cannot_capture_forward(self):
        self.board['e4'].place(Pawn('light'))
        self.board['e5'].place(Pawn('dark'))  # Blocking square

        move = ChessCapture(self.board, 'e4', 'e5')
        with self.assertRaises(ChessCannotCaptureOutsideCapturePatternException):
            move.validate()
        self.board.clear()  # Clear the board for next test

    def test_knight_can_capture_over_pieces(self):
        self.board['g1'].place(Knight('light'))
        self.board['f3'].place(Pawn('dark'))   # Capture target
        self.board['e2'].place(Pawn('light'))  # Obstructing but irrelevant

        move = ChessCapture(self.board, 'g1', 'f3')
        self.assertTrue(move.validate(), "Knight should capture even if blocked along path")
        captured = move.execute()
        self.assertIsNotNone(captured)
        self.assertEqual(captured.color, 'dark')
        self.assertTrue(self.board['f3'].is_occupied())
        self.board.clear()  # Clear the board for next test

    def test_bishop_can_capture_clear_path(self):
        self.board['c1'].place(Bishop('light'))
        self.board['g5'].place(Pawn('dark'))  # Diagonal target

        move = ChessCapture(self.board, 'c1', 'g5')
        self.assertTrue(move.validate(), "Bishop should capture on clear diagonal")
        captured = move.execute()
        self.assertIsNotNone(captured)
        self.assertTrue(self.board['g5'].is_occupied())
        self.board.clear()  # Clear the board for next test

    def test_bishop_cannot_capture_through_obstruction(self):
        self.board['c1'].place(Bishop('light'))
        self.board['e3'].place(Pawn('light'))  # Friendly piece blocking
        self.board['g5'].place(Pawn('dark'))   # Valid capture target

        move = ChessCapture(self.board, 'c1', 'g5')
        with self.assertRaises(ChessCannotCaptureOutsideCapturePatternException):
            move.validate()
        self.board.clear()  # Clear the board for next test

    def test_rook_can_capture_clear_path(self):
        self.board['a1'].place(Rook('light'))
        self.board['a7'].place(Pawn('dark'))

        move = ChessCapture(self.board, 'a1', 'a7')
        self.assertTrue(move.validate(), "Rook should capture along open file")
        captured = move.execute()
        self.assertIsNotNone(captured)
        self.assertEqual(captured.color, 'dark')
        self.board.clear()  # Clear the board for next test

    def test_rook_cannot_capture_through_piece(self):
        self.board['a1'].place(Rook('light'))
        self.board['a3'].place(Pawn('light'))  # Friendly piece obstructing
        self.board['a7'].place(Pawn('dark'))   # Valid target beyond obstruction

        move = ChessCapture(self.board, 'a1', 'a7')
        with self.assertRaises(ChessCannotCaptureOutsideCapturePatternException):
            move.validate()
        self.board.clear()  # Clear the board for next test

    def test_queen_can_capture_long_range(self):
        self.board['d1'].place(Queen('light'))
        self.board['h5'].place(Pawn('dark'))

        move = ChessCapture(self.board, 'd1', 'h5')
        self.assertTrue(move.validate(), "Queen should capture along clear diagonal")
        captured = move.execute()
        self.assertIsNotNone(captured)
        self.assertEqual(captured.color, 'dark')
        self.board.clear()  # Clear the board for next test

    def test_queen_blocked_from_capture(self):
        self.board['d1'].place(Queen('light'))
        self.board['f3'].place(Pawn('light'))  # Obstructing own piece
        self.board['h5'].place(Pawn('dark'))

        move = ChessCapture(self.board, 'd1', 'h5')
        with self.assertRaises(ChessCannotCaptureOutsideCapturePatternException):
            move.validate()
        self.board.clear()  # Clear the board for next test

class TestPawnPromotion(unittest.TestCase):
    def setUp( self ):
        self.board = ChessBoard()

    def setup_pawn( self, color: str ) -> None:
        self.board.clear()
        if color == 'light':
            rank = 7
        elif color == 'dark':
            rank = 2
        else:
            raise ValueError( "Color must be 'light' or 'dark'.  {color=}" )
        file = 'd' # Chosen fairly by meatspace roll of 1d8 applied to a Caesar key.
        self.board.place_piece( Pawn( color ), file, rank )
        self.board.turn = color

    def test_valid_default_light_promotion( self ):
        self.setup_pawn( 'light' )

        move = ChessMove.from_long_notation( self.board, 'd7d8' )
        self.assertTrue( move.validate() )
        move.execute()
        self.assertTrue( self.board['d8'].contains() == Queen( 'light' ) )

class TestCastling(unittest.TestCase):

    def setUp(self):
        self.board = ChessBoard()
        self.board.clear()

    def setup_king_rook_pair(self, color, kingside=True):
        rank = '1' if color == 'light' else '8'
        king_pos = f'e{rank}'
        rook_pos = f'{"h" if kingside else "a"}{rank}'
        self.board[king_pos].place(King(color))
        self.board[rook_pos].place(Rook(color))
        self.board.turn = color

    def test_valid_kingside_castle_light(self):
        self.setup_king_rook_pair('light', kingside=True)
        move = ChessCastle(self.board, 'e1', 'g1')
        self.assertTrue(move.validate())
        move.execute()
        self.assertTrue(isinstance(self.board['g1'].contains(), King))
        self.assertTrue(isinstance(self.board['f1'].contains(), Rook))
        self.board.clear()  # Clear the board for next test

    def test_valid_queenside_castle_dark(self):
        self.setup_king_rook_pair('dark', kingside=False)
        move = ChessCastle(self.board, 'e8', 'c8')
        self.board.turn = 'dark'  # Set turn to dark for this test
        self.assertTrue(move.validate())
        move.execute()
        self.assertTrue(isinstance(self.board['c8'].contains(), King))
        self.assertTrue(isinstance(self.board['d8'].contains(), Rook))
        self.board.clear()  # Clear the board for next test

    def test_blocked_kingside_castle(self):
        self.setup_king_rook_pair('light', kingside=True)
        self.board['f1'].place(Bishop('light'))
        move = ChessCastle(self.board, 'e1', 'g1')
        with self.assertRaises(ChessCannotCastleThroughOccupiedSquaresException):
            move.validate()
        self.board.clear()  # Clear the board for next test

    def test_rook_has_moved_invalidates_castling(self):
        self.setup_king_rook_pair('dark', kingside=True)
        rook = self.board['h8'].contains()
        rook.raise_moved_flag()
        move = ChessCastle(self.board, 'e8', 'g8')
        with self.assertRaises(ChessCannotCastleIfRookHasMovedException):
            move.validate()
        self.board.clear()  # Clear the board for next test

    def test_king_has_moved_invalidates_castling(self):
        self.setup_king_rook_pair('light', kingside=False)
        king = self.board['e1'].contains()
        king.raise_moved_flag()
        move = ChessCastle(self.board, 'e1', 'c1')
        with self.assertRaises(ChessCannotCastleIfKingHasMovedException):
            move.validate()
        self.board.clear()  # Clear the board for next test

    def test_king_is_in_check(self):
        self.setup_king_rook_pair('light', kingside=True)
        self.board['e8'].place(Queen('dark'))  # Queen checks e1
        move = ChessCastle(self.board, 'e1', 'g1')
        with self.assertRaises(ChessCannotCastleOutOfCheckException):
            move.validate()
        self.board.clear()  # Clear the board for next test

    def test_king_moves_through_check(self):
        self.setup_king_rook_pair('dark', kingside=True)
        self.board['f1'].place(Queen('light'))  # Queen attacks f8
        move = ChessCastle(self.board, 'e8', 'g8')
        with self.assertRaises(ChessCannotCastleIntoCheckException):
            move.validate()
        self.board.clear()  # Clear the board for next test

    def test_king_destination_square_under_attack(self):
        self.setup_king_rook_pair('dark', kingside=True)
        self.board['g1'].place(Queen('light'))  # Queen attacks g8
        move = ChessCastle(self.board, 'e8', 'g8')
        with self.assertRaises(ChessCannotCastleIntoCheckException):
            move.validate()
        self.board.clear()  # Clear the board for next test

    def test_invalid_target_square(self):
        self.setup_king_rook_pair('light', kingside=True)
        move = ChessCastle(self.board, 'e1', 'f1')  # Not a valid castle target
        with self.assertRaises(ChessCannotCastleIntoInvalidDestinationException):
            move.validate()
        self.board.clear()  # Clear the board for next test

#class TestDiscoveredChecks( unittest.TestCase ):
#    def setUp( self ):
#        self.board = ChessBoard()
#        self.board.clear()

    



if __name__ == "__main__":
    unittest.main()
