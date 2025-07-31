from chess_piece import Pawn, Rook, Knight, Bishop, Queen, King
from chess_board import *

class ChessMove:
    """Represents a chess move."""
    
    def __init__(self, board: ChessBoard, from_key: str, to_key: str ):
        """Initialize a chess move with the board and the squares involved."""
        if not isinstance(board, ChessBoard):
            raise TypeError("board must be an instance of ChessBoard.")     
        
        if from_key not in board.squares or to_key not in board.squares:
            raise ValueError("from_key and to_key must be valid square keys on the board.")
        
        from_square = board.squares[from_key]
        to_square = board.squares[to_key]

        if not isinstance( from_square.contains(), ChessPiece ):
            raise ValueError("No piece on the from square to move.")
        
        if not isinstance(to_square, Square):
            raise TypeError("to_square must be an instance of Square.")
        
        if not isinstance(from_square, Square):
            raise TypeError("from_square must be an instance of Square.")
        
        self.board = board
        self.from_square = from_square
        self.to_square = to_square

    def __eq__ (self, other) -> bool:
        """Check if two chess moves are equal based on their squares and board state."""
        if not isinstance(other, ChessMove):
            return False
        return (self.from_square == other.from_square and
                self.to_square == other.to_square and
                self.board == other.board)

    def __hash__( self ) -> int:
        """Returns a hash of the move."""
        return hash((self.from_square, self.to_square, self.board.turn))

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
        print( "Passed validate_other_constraints() in base class" )
        return True

    def validate_piece_movement( self ) -> bool:
        """Validation for the actual move, with chess game rule logic"""
        moving_player = self.board.turn
        passive_player = 'light' if moving_player == 'dark' else 'dark'

        # Is the destination in the Piece's movement pattern? (or capture pattern for ChessCapture)
        # TODO: check that this works properly for all pieces, especially sliding pieces.
        if self.to_square.key not in [ key for key in self.board.get_legal_moves( self.from_square.key ) ]:
            return False
            # raise ValueError(f'Cannot move {self.from_square.contains()} from {self.from_square} to {self.to_square}. It is not a valid move.')
        # Alternative for ChessCapture override: return only Squares occupied by passive_player's ChessPieces.

        # Cannot move a King into check
        if isinstance( self.from_square.contains(), King ):
            if self.board.is_in_check_from( self.to_square, passive_player ):
                return False

        # Cannot move if the move would be a discovered check
        # TODO: this
        # Possible means: Make a duplicate board, _force_ the move, and then determine whether the moving_player's King is in check?
        # Possibly move validate_discovered_check() into a new function since we need to do this for every type of move.
        # We will also have to override this for ChessCapture for pawns: the move is to capture laterally but we can only do so if
        # the space in the corresponding Square in the movement_pattern is open to move into.

        # If all of the validation checks pass, return True
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
        return all( ( self.validate_origin_constraints(), self.validate_other_constraints(), self.validate_piece_movement() ) )
    
    def execute(self) -> None | ChessPiece:
        """Executes the move if it is valid."""
        if self.validate():
            self.board.move_piece(self.from_square.key, self.to_square.key)
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

    def validate_is_successful_en_passant( self, capturing_piece: Pawn, captured_piece: ChessPiece ) -> bool:
        """Check if the move is an en passant capture."""
        # Both pieces must be Pawns:
        if not all( ( isinstance(capturing_piece, Pawn), isinstance(captured_piece, Pawn) ) ):
            return False
            # raise ValueError(f'Cannot perform en passant capture with {capturing_piece} and {captured_piece}. They are not both Pawns.'
        # The capture must be one file away and the same rank:
        if abs(ord(self.from_square.file) - ord(self.to_square.file)) != 1 or self.from_square.rank != self.to_square.rank:
            return False
            # raise ValueError(f'Cannot perform en passant capture from {self.from_square} to {self.to_square}. They are not one file away and the same rank.')
        # The captured Pawn must have just moved two squares forward:
        if not captured_piece.vulnerable:
            return False
            # raise ValueError(f'Cannot perform en passant capture on {self.to_square}. The captured Pawn is not vulnerable to en passant.')
        # The space behind the captured Pawn must be empty:
        final_rank = self.to_square.rank + capturing_piece.direction # type: ignore
        final_square_key = f"{self.to_square.file}{final_rank}"
        if self.board.squares[final_square_key].is_occupied():
            return False
            # raise ValueError(f'Cannot perform en passant capture on {self.to_square}. The square behind the captured Pawn is not empty.')
        # If all checks pass, return True

        return True

    def en_passant_final_square( self ) -> Square:
        """Returns the final square for an en passant capture."""
        final_rank = self.to_square.rank + self.from_square.contains().direction # pyright: ignore[reportAttributeAccessIssue]
        final_square_key = f"{self.to_square.file}{final_rank}"
        return self.board.squares[final_square_key]

    def execute(self) -> ChessPiece | None:
        """Executes the move if it is valid."""
        if self.validate():
            capturing_piece = self.from_square.contains()
            captured_piece = self.to_square.contains()
            if self.validate_is_successful_en_passant(capturing_piece, captured_piece): # type: ignore
                self.board[self.to_square.key].remove()  # Remove the captured piece
                self.to_square = self.en_passant_final_square()  # Update to the final square
            else:
                # Regular capture
                self.to_square.remove()  # Remove the captured piece
            self.board.move_piece(self.from_square.key, self.to_square.key)
            self.to_square.occupant.raise_moved_flag() # type: ignore because we know the piece is not None
            self.board.end_turn()
            return captured_piece
        else:
            return None
            # raise ValueError("Invalid capture move.")


    def validate_piece_capture( self ) -> bool:
        """Validation for the actual capture, with chess game rule logic"""
        moving_player = self.board.turn
        passive_player = 'light' if moving_player == 'dark' else 'dark'
        # Is the destination in the Piece's movement pattern? (or capture pattern for ChessCapture)
        # TODO: check that this works properly for all pieces, especially sliding pieces.
        if self.to_square.key not in [ key for key in self.board.get_legal_captures( self.from_square.key ) ]:
            return False
            # raise ValueError(f'Cannot move {self.from_square.contains()} from {self.from_square} to {self.to_square}. It is not a valid move.')
        # Alternative for ChessCapture override: return only Squares occupied by passive_player's ChessPieces.
        # Cannot move a King into check
        if isinstance( self.from_square.contains(), King ):
            if self.board.is_in_check_from( self.to_square, passive_player ):
                return False
        # Cannot move if the move would be a discovered check
        # TODO: this
        # Possible means: Make a duplicate board, _force_ the move, and then determine whether the moving_player's King is in check?
        # Possibly move validate_discovered_check() into a new function since we need to do this for every type of move.
        # We will also have to override this for ChessCapture for pawns: the move is to capture laterally but we can only do so if
        # the space in the corresponding Square in the movement_pattern is open to move into.

        # If all of the validation checks pass, return True
        return True

    def validate( self ) -> bool:
        """Validates the capture according to chess rules (hopefully)."""
        # For now, just return False for invalid moves.  If we end up needing Exceptions, we can do so
        # and will put in the code now, but it will be commented out.
        # We're returning False so that we don't have to lean into exception handling for the game UI loop.

        return all( ( self.validate_origin_constraints(), self.validate_other_constraints(), self.validate_piece_capture() ) )
    


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
        # Verify this works properly.
        match self.to_square.key:
            case 'g1':
                path = ['f1', 'g1']
            case 'c1':
                path = ['d1', 'c1']
            case 'g8':
                path = ['f8', 'g8']
            case 'c8':
                path = ['d8', 'c8']
        for square_key in path: # pyright: ignore[reportPossiblyUnboundVariable]
            square = self.board[square_key]
            if self.board.is_in_check_from( square, 'light' if self.board.turn == 'dark' else 'dark' ):
                return False
                # raise ValueError(f'Cannot castle to {self.to_square}. The square {square} is under attack by {'light' if self.board.turn == 'dark' else 'dark'}.')

        # If all checks pass, return True
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
            return None
            # raise ValueError("Invalid castling move.")
