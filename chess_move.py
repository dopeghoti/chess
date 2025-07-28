from chess_piece import Pawn, Rook, Knight, Bishop, Queen, King
from chess_board import *

class ChessMove:
    """Represents a chess move."""
    
    def __init__(self, board: ChessBoard, from_square: Square, to_square: Square):
        if not isinstance( from_square.contains(), ChessPiece ):
            raise ValueError("No piece on the from square to move.")
        
        if not isinstance(to_square, Square):
            raise TypeError("to_square must be an instance of Square.")
        
        if not isinstance(from_square, Square):
            raise TypeError("from_square must be an instance of Square.")
        
        self.board = board
        self.from_square = from_square
        self.to_square = to_square

    def flag_movement( self, piece: ChessPiece ) -> None:
        """Flag the piece as having moved.  This is used for castling."""
        piece.raise_moved_flag() # type: ignore because we know the piece is not None

    def validate_origin_constraints( self ) -> bool:
        """Validates constraints for the moving piece and its square."""
        if self.from_square == self.to_square:
            return False
            # raise ValueError("Cannot move a piece to the same square.")

        if self.from_square.contains().color != self.board.turn: # type: ignore because we know the color is not None
            return False
            # raise ValueError(f'Cannot move {self.from_square.contains()} from {self.from_square} to {self.to_square}. It is not your turn.')

        if not self.from_square.is_occupied():
            return False
            # raise ValueError(f'No piece on {self.from_square} to move.')

        return True

    def validate_other_constraints( self ) -> bool:
        """Validates constraints for the destination square and others, if applicable (e. g. castling)."""
        if self.to_square.is_occupied():
            return False
            # raise ValueError(f'Cannot move to {self.to_square}. It is already occupied by {self.to_square.contains()}.')

        return True

    def validate( self ) -> bool:
        """Validates the move according to chess rules (eventually)."""
        # This is a placeholder for move validation logic.
        # Actual validation would depend on the piece type and game state.
        # But we can get started with some fundamental checks.

        # For not, just return False for invalid moves.  If we end up needing Exceptions, we can do so
        # and will put in the code now, but it will be commented out.

        # TODO: handle castling, en passant, promotion, etc.
        # TODO: implement ChessBoard.move() to handle moving a piece (NOT to be confused with a chess move)

        return all( ( self.validate_origin_constraints(), self.validate_other_constraints() ) )
    
    def execute(self) -> None | ChessPiece:
        """Executes the move if it is valid."""
        if self.validate():
            self.board.move_piece(self.from_square, self.to_square)
            self.to_square.occupant.raise_moved_flag() # type: ignore because we know the piece is not None
            self.board.end_turn()

    def __str__(self):
        return f"{self.from_square.contains().name} moves from {self.from_square} to {self.to_square}" # type: ignore because we know the piece is not None

    def __repr__(self):
        return f"ChessMove({self.board}, {self.from_square}, {self.to_square})"
    
class ChessCapture(ChessMove):
    """Represents a chess capture move."""

    def validate_other_constraints(self) -> bool:
        """Validates constraints for the destination square and others, if applicable (e. g. castling)."""
        if not self.to_square.is_occupied():
            return False
            # raise ValueError(f'Cannot capture on {self.to_square}. It is not occupied by any piece.')

        if self.to_square.contains().color == self.from_square.contains().color: # type: ignore because we know the colors are not None
            return False
            # raise ValueError(f'Cannot capture {self.to_square.contains()} on {self.to_square}. It is a friendly piece.')

        return True

    def execute(self) -> ChessPiece | None:
        """Executes the move if it is valid."""
        # TODO - the very odd case of en pessant is not handled.
        captured_piece = self.to_square.contains()
        if self.validate():
            self.board.move_piece(self.from_square, self.to_square)
            self.to_square.occupant.raise_moved_flag() # type: ignore because we know the piece is not None
            self.board.end_turn()
            return captured_piece
        else:
            return None
            # raise ValueError("Invalid capture move.")

class ChessCastle(ChessMove):
    """Represents a chess castling move."""
    
    def validate_other_constraints(self) -> bool:
        if not isinstance( self.from_square.contains(), King ):
            return False
            # raise ValueError(f'Cannot castle with {self.from_square.contains()}. It is not a King.')

        if self.from_square.contains().has_moved: # type: ignore because we know the piece is not None
            return False
            # raise ValueError(f'Cannot castle with {self.from_square.contains()}. It has already moved.')

        if self.from_square.contains().has_been_in_check: # type: ignore because we know the piece is a King
            return False
            # raise ValueError(f'Cannot castle with {self.from_square.contains()}. It is or has been in check.')

        if self.board.turn == 'light':
            if self.to_square.key not in ['g1', 'c1']:
                return False
                # raise ValueError(f'Cannot castle to {self.to_square}. It is not a valid castling square for light pieces.')
            if self.from_square.key != 'e1':
                return False
                # raise ValueError(f'Cannot castle from {self.from_square}. It is not a valid castling square for light pieces.')
            if self.to_square.key == 'g1':
                if self.board['f1'].is_occupied():
                    return False
                rook_key = 'h1'
                    # raise ValueError(f'Cannot castle to {self.to_square}. The squares between the King and Rook are not empty.')
            elif self.to_square.key == 'c1':
                if any( ( self.board['d1'].is_occupied(), self.board['b1'].is_occupied() ) ):
                    return False
                rook_key = 'a1'
                    # raise ValueError(f'Cannot castle to {self.to_square}. The squares between the King and Rook are not empty.')
        else:
            if self.to_square.key not in ['g8', 'c8']:
                return False
                # raise ValueError(f'Cannot castle to {self.to_square}. It is not a valid castling square for dark pieces.')
            if self.from_square.key != 'e8':
                return False
                # raise ValueError(f'Cannot castle from {self.from_square}. It is not a valid castling square for dark pieces.')
            if self.to_square.key == 'g8':
                if self.board['f8'].is_occupied():
                    return False
                    # raise ValueError(f'Cannot castle to {self.to_square}. The squares between the King and Rook are not empty.')
                rook_key = 'h8'
            elif self.to_square.key == 'c8':
                if any( ( self.board['d8'].is_occupied(), self.board['b8'].is_occupied() ) ):
                    return False
                    # raise ValueError(f'Cannot castle to {self.to_square}. The squares between the King and Rook are not empty.')
                rook_key = 'a8'

        # Validate the Rook has not moved and that the piece in the Rook's spot is indeed a Rook:
        rook = self.board[rook_key].contains() # pyright: ignore[reportPossiblyUnboundVariable]
        if not isinstance(rook, Rook):
            return False
            # raise ValueError(f'Cannot castle with {rook}. It is not a Rook.')
        if rook.has_moved:
            return False
            # raise ValueError(f'Cannot castle with {rook}. It has already moved.')

        # TODO: check if the squares the King moves through are not under attack.
        # This is a complex check that requires knowledge of the game state and all pieces' positions
        # and their possible moves. This will come later.
        return True

    def execute(self) -> None:
        """Executes the castling move if it is valid."""
        if self.validate():
            king = self.from_square.remove()
            if king.color == 'light':
                rook_key = 'h1' if self.to_square.key == 'g1' else 'a1'
                rook_to_key = 'f1' if self.to_square.key == 'g1' else 'd1'
            else:
                rook_key = 'h8' if self.to_square.key == 'g8' else 'a8'
                rook_to_key = 'f8' if self.to_square.key == 'g8' else 'd8'
            rook = self.board[rook_key].remove()
            
            # Place the King and Rook in their new positions
            self.board.place_piece(king, self.to_square.file, self.to_square.rank ) # type: ignore (suppress Pylance warning for type we know is not None)
            self.board.place_piece(rook, rook_to_key[0], int(rook_to_key[1]) )
            
            # Mark the King and Rook as having moved
            king.raise_moved_flag()
            rook.raise_moved_flag()
            
            self.board.end_turn()
        else:
            raise ValueError("Invalid castling move.")