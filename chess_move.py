from chess_piece import Pawn, Rook, Knight, Bishop, Queen, King
from chess_board import *
from chess_exception import *

class ChessMetaMove():
    """An abstract representation of a chess move.  Not to be instantiated directly.
    
    Exceptions for move validation failures had been commented out and replaced with
    False returns for the sake of allowing for usage withing a game loop without crashing
    the entire program.  I'm instead implementing custom ChessExceptions that the game loop,
    once it is made, can look for specifically."""
    def __init__( self, board: ChessBoard, from_key: str, to_key: str):
        if not isinstance( board, ChessBoard):
            raise TypeError( 'Board must be an instance of ChessBoard.' )
        if from_key not in board.squares or to_key not in board.squares:
            raise ValueError("from_key and to_key must be valid square keys on the board.")
        if type( self ) == ChessMetaMove:
            raise NotImplementedError( 'ChessMetaMove is an abstract class and must be instantiated via a subclass.' )
        self.board = board
        self.move_from = {
            'key':      from_key,
            'square':   self.board.squares[from_key]
        }
        self.move_to = {
            'key':      to_key,
            'square':   self.board.squares[to_key]
        }

    def __eq__( self, other ) -> bool:
        if not isinstance( other, type(self) ):
            return False
        return (
            self.move_from == other.move_from and
            self.move_to == other.move_to and
            self.board == other.board
        )
    
    def __hash__( self ) -> int:
        return hash( ( self.board, self.move_to, self.move_from ) )
    
    @classmethod
    def from_long_notation( cls, board: ChessBoard, notation: str ):
        """Factory to create appropriate Move instance based on long
        move notation, i. e. 'e2e4'."""
        # Local import to avoid circular dependency issues
        from chess_notation import ChessNotationConverter as CC
        converter = CC( board )
        return converter.create_move_from_long_notation( notation )

    def to_notation( self ) -> str:
        """Represent this move in standard algebraic notataion."""
        # Local import to avoid circular dependency issues
        from chess_notation import ChessNotationConverter as CC
        converter = CC( self.board )
        long_notation = f"{self.move_from['key']}{self.move_to['key']}"
        return converter.long_to_algebraic( long_notation )

    def to_long_notation( self ) -> str:
        """Represent this move in explicit long algebraic notation."""
        long_notation = f"{self.move_from['key']}{self.move_to['key']}"
        return long_notation

    def flag_movement( self, piece: Pawn | Rook | King ) -> None:
        """ Raises the has_moved flag on appropriate ChessPiece objects"""
        piece.raise_moved_flag()

    def flag_vulnerable( self, piece: Pawn ) -> None:
        piece.raise_passant_flag()

    def validate_origin_constraints( self ) -> bool:
        """Validates constraints for the moving piece and its square."""
        if self.move_from['square'] == self.move_to['square']:
            # return False
            raise ChessCannotMoveToOriginSquareException( f'Attempting to move from a square to itself, namely {self.move_from["key"]}.')

        if not self.move_from['square'].is_occupied():
            # return False
            raise ChessCannotMoveFromEmptySquareException( f'Attempting to move from empty square at {self.move_from["key"]}.' )
            # raise ValueError(f'No piece on {self.from_square} to move.')

        if self.move_from['square'].contains().color != self.board.turn: # type: ignore because we know the color is not None
            # return False
            piece = self.move_from['square'].contains()
            raise ChessCannotMoveOutOfTurnException( f'Attempting to move {piece.color} while the ChessBoard sees it to be {self.board.turn}\'s turn.' )
        return True
    
    def validate_other_constraints( self ) -> bool:
        raise NotImplementedError( 'other_constraints need to be defined by a ChessMetaMove subclass.' )
    
    def validate_piece_movement( self ) -> bool:
        raise NotImplementedError( 'piece_movement needs to be defined by a ChessMetaMove subclass.' )
    
    def validate_check_rules( self ) -> bool:
        # Discovered checks are handled by ChessBoard.get_legal_(moves|captures).
        moving_player = self.board.turn
        passive_player = 'light' if moving_player == 'dark' else 'dark'

        # Cannot move a King into check
        if isinstance( self.move_from['square'].contains(), King ):
            if self.board.is_in_check_from( self.move_to['square'], passive_player ):
                return False
        return True

    def validate( self ) -> bool:
        try:
            return (
                self.validate_origin_constraints() and
                self.validate_other_constraints() and
                self.validate_piece_movement() and 
                self.validate_check_rules()
            )
        except ChessException as e:
            raise e
        

class ChessMove(ChessMetaMove):
    """Represents a normal, non-capturing chess move."""
    
    def __init__(self, board: ChessBoard, from_key: str, to_key: str ):
        super().__init__( board, from_key, to_key )
        self.piece = self.move_from['square'].contains()

    def validate_other_constraints( self ) -> bool:
        """Validates constraints for the destination square."""
        if self.move_to['square'].is_occupied():
            # return False
            piece = self.move_from['square'].contains()
            blocker = self.move_to['square'].contains()
            raise ChessCannotMoveIntoOccupiedSquareException( f'Attempting to move {piece.name} from {self.move_from["key"]} to {self.move_to["key"]} which is occupied by a {blocker.color} {blocker.name}.' )
        return True

    def validate_piece_movement( self ) -> bool:
        """Validation for the actual move, with chess game rule logic"""

        # Is the destination in the Piece's movement pattern?
        if self.move_to['square'] not in [ key for key in self.board.get_legal_moves( self.move_from['key'] ) ]:
            # return False
            raise ChessCannotMoveOutsideMovementPatternException( f'Attempting to move {self.piece.name} illegally from {self.move_from["key"]} to {self.move_to["key"]}.' ) 
        # If all of the validation checks pass, return True
        return True

    def execute(self) -> None:
        """Executes the move if it is valid."""
        if self.validate():
            if isinstance( self.piece, Pawn ) and abs( self.move_from['square'].rank - self.move_to['square'].rank ) == 2:
                self.flag_vulnerable( self.piece )
            self.board.move_piece(self.move_from['key'], self.move_to['key'] )
            if type(self.piece) in ( Pawn, King, Rook ):
                self.flag_movement( self.piece )
            self.board.end_turn()

    def __str__(self):
        return f"{self.piece.name} moves from {self.move_from['key']} to {self.move_to['key']}" 

    def __repr__(self):
        return f"ChessMove({self.board}, {self.move_from['key']}, {self.move_to['key']}"

class ChessCapture(ChessMetaMove):
    """Represents a chess capture move."""
    def __init__(self, board: ChessBoard, from_key: str, to_key: str ):
        super().__init__( board, from_key, to_key )
        self.piece = self.move_from['square'].contains()

    def validate_other_constraints(self) -> bool:
        """Validates constraints for the destination square."""
        if not self.move_to['square'].is_occupied():
            # return False
            raise ChessCannotCaptureIntoEmptySquareException( f'Cannot capture from empty square at {self.move_to["key"]}.' )
        if self.move_to['square'].contains().color == self.piece.color: # type: ignore because we know the colors are not None
            # return False
            blocker = self.move_to['square'].contains()
            raise ChessCannotCaptureFriendlyPieceException( f'Cannot capture friendly {blocker.color} {blocker.name} at {self.move_to["key"]}.' )
        return True

    def validate_is_successful_en_passant( self, capturing_piece: Pawn, captured_piece: ChessPiece ) -> bool:
        """Check if the move is an en passant capture.
        
        Currently this is both checking whether a move even _is_ an en passant attempt and _also_ validating its legality.  We
        don't want to throw Exceptions until this is broken into separate identification (which will not throw) and validation
        (which will).  For now, continue to return False but I have the exceptions here ready for when the logic flow is ready."""
        # Both pieces must be Pawns:
        if not all( ( isinstance(capturing_piece, Pawn), isinstance(captured_piece, Pawn) ) ):
            blocker = self.move_to['square'].contains()
            # raise ChessCannotCaptureNonPawnEnPassantException( f'A {self.piece.name} cannot capture a {blocker.name} en passant.' )
            return False
        # The capture must be one file away and the same rank:
        if abs(ord(self.move_from['square'].file) - ord(self.move_to['square'].file)) != 1 or self.move_from['square'].rank != self.move_to['square'].rank:
            # raise ChessCannotCaptureEnPassantRemotelyException( f'Cannot capture en-passant from {self.move_from["key"]} to {self.move_to["key"]}.' )
            return False
        # The captured Pawn must have just moved two squares forward:
        if not captured_piece.vulnerable:
            # raise ChessCannotCaptureEnPassantWhenNotVulnerableException ( 'Target of en passant capture is not vulnerable.' )
            return False
        # The space behind the captured Pawn must be empty:
        final_rank = self.move_to['square'].rank + capturing_piece.direction # type: ignore
        final_square_key = f"{self.move_to['square'].file}{final_rank}"
        if self.board.squares[final_square_key].is_occupied():
            blocker = self.board[final_square_key].contains()
            # raise ChessCannotCaptureEnPassantWhenFinalSquareNotEmptyException( f'Somehow a {blocker.name} is occupying destination square {final_square_key}.' )
            return False
        # If all checks pass, return True
        return True

    def en_passant_final_square( self ) -> Square:
        """Returns the final square for an en passant capture."""
        final_rank = self.move_to['square'].rank + self.move_from['square'].contains().direction
        final_square_key = f"{self.move_to['square'].file}{final_rank}"
        return self.board.squares[final_square_key]

    def execute(self) -> Optional[ChessPiece]:
        """Executes the move if it is valid."""
        if self.validate():
            capturing_piece = self.move_from['square'].contains()
            captured_piece = self.move_to['square'].contains()
            if isinstance( capturing_piece, Pawn ) and isinstance( captured_piece, Pawn ) and \
                    self.move_from['square'].rank == self.move_to['square'].rank: # This is a lateral move, presumptively this is en-passant
                if self.validate_is_successful_en_passant( capturing_piece, captured_piece ):
                    # En-passant capture
                    self.board.remove_piece( self.move_to['key'] )  # Remove the captured piece
                    final_square = self.en_passant_final_square()
                    self.board.move_piece( self.move_from['key'], final_square.key )
                    self.flag_movement( final_square.contains() ) # type: ignore because we know the piece is
            else:
                # Regular capture
                self.board.remove_piece( self.move_to['key'] )  # Remove the captured piece
                self.board.move_piece(self.move_from['key'], self.move_to['key'])
                self.flag_movement( self.piece ) # type: ignore because we know the piece is)
                # self.move_to['square'].occupant.raise_moved_flag() # type: ignore because we know the piece is not None
            self.board.end_turn()
            return captured_piece
        else:
            return None
            # raise ValueError("Invalid capture move.")

    def validate_piece_movement( self ) -> bool:
        """Validation for the actual capture, with chess game rule logic"""
        moving_player = self.board.turn
        passive_player = 'light' if moving_player == 'dark' else 'dark'
        # Is the destination in the Piece's capture pattern?
        if self.move_to['square'] not in self.board.get_legal_captures( self.move_from['key'] ):
            # return False
            raise ChessCannotCaptureOutsideCapturePatternException ( f'Attempting to capture with {self.piece.name} illegally from {self.move_from["key"]} to {self.move_to["key"]}. {repr(self)}' ) 
        # If all of the validation checks pass, return True
        return True
    
    def __str__(self):
        return f"{self.piece.name} takes from {self.move_from['key']} to {self.move_to['key']}" 
    
    def __repr__(self):
        return f"ChessCapture({self.board}, {self.move_from['key']}, {self.move_to['key']}"


class ChessCastle(ChessMetaMove):
    """Represents a chess castling move."""
    def __init__(self, board: ChessBoard, from_key: str, to_key: str ):
        super().__init__( board, from_key, to_key )
        self.piece = self.move_from['square'].contains()

    def validate_other_constraints(self) -> bool:
        if not isinstance( self.piece, King ):
            # return False
            raise ChessCannotCastleWithNonKingException ( f'Attempting to castle but we need a King, not a {self.piece.name}.' )

        if self.piece.has_moved:
            # return False
            raise ChessCannotCastleIfKingHasMovedException

        if self.piece.has_been_in_check: # type: ignore because we know the piece is a King
            # return False
            raise ChessCannotCastleIfKingHasBeenInCheckException

        if self.board.is_in_check_from( self.move_from['square'], 'light' if self.board.turn == 'dark' else 'dark' ):
            # return False
            raise ChessCannotCastleOutOfCheckException

        if self.board.turn == 'light':
            if self.move_to['key'] not in ['g1', 'c1']:
                # return False
                raise ChessCannotCastleIntoInvalidDestinationException( f'Attempting illegal castle from {self.move_from["key"]} to {self.move_to["key"]}.' )
            if self.move_from['key'] != 'e1':
                # return False
                raise ChessCannotCastleIntoInvalidDestinationException( f'Attempting illegal castle from {self.move_from["key"]} to {self.move_to["key"]}.' )
            if self.move_to['key'] == 'g1':
                if self.board['f1'].is_occupied():
                    # return False
                    raise ChessCannotCastleThroughOccupiedSquaresException( 'Cannot castle through occupied square f1.' )
                rook_key = 'h1'
            elif self.move_to['key'] == 'c1':
                if any( ( self.board['b1'].is_occupied(), self.board['c1'].is_occupied(), self.board['d1'].is_occupied() ) ):
                    # return False
                    raise ChessCannotCastleThroughOccupiedSquaresException( 'Cannot castle through occupied squares b1, c1.' )
                rook_key = 'a1'
        else:
            if self.move_to['key'] not in ['g8', 'c8']:
                # return False
                raise ChessCannotCastleIntoInvalidDestinationException( f'Attempting illegal castle from {self.move_from["key"]} to {self.move_to["key"]}.' )
            if self.move_from['key'] != 'e8':
                # return False
                raise ChessCannotCastleIntoInvalidDestinationException( f'Attempting illegal castle from {self.move_from["key"]} to {self.move_to["key"]}.' )
            if self.move_to['key'] == 'g8':
                if self.board['f8'].is_occupied():
                    # return False
                    raise ChessCannotCastleThroughOccupiedSquaresException( 'Cannot castle through occupied square f8.' )
                rook_key = 'h8'
            elif self.move_to['key'] == 'c8':
                if any( ( self.board['b8'].is_occupied(), self.board['c8'].is_occupied(), self.board['d8'].is_occupied() ) ):
                    # return False
                    raise ChessCannotCastleThroughOccupiedSquaresException( 'Cannot castle through occupied squares b8, b8.' )
                rook_key = 'a8'

        # Validate the Rook has not moved and that the piece in the Rook's spot is indeed a Rook:
        rook = self.board[rook_key].contains() # pyright: ignore[reportPossiblyUnboundVariable]
        if not isinstance(rook, Rook):
            # return False
            raise ChessCannotCastleWithoutRookException( f'Cannot castle to {rook_key} as there is no rook there.' ) # pyright: ignore[reportPossiblyUnboundVariable]
        if rook.has_moved:
            # return False
            raise ChessCannotCastleIfRookHasMovedException( f'Cannot castle as root at {rook_key} has already moved.' ) # pyright: ignore[reportPossiblyUnboundVariable]

        # TODO: check if the squares the King moves through are not under attack.
        # Verify this works properly.
        match self.move_to['key']: # We're probably double-checking that the King is not moving into check because of the base class validation.  Maybe move g1/c1/g8/c8 from these Lists?
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
                # return False
                raise ChessCannotCastleIntoCheckException( f'Cannot castle into {square_key} which is in check.' )

        # If all checks pass, return True
        return True

    def validate_piece_movement( self ) -> bool:
        """Validation for the actual castling move, with chess game rule logic."""
        # Castling is a special move, so we don't need to check the piece's movement pattern.
        # We already checked the constraints in validate_other_constraints().
        return True

    def execute(self) -> None:
        """Executes the castling move if it is valid."""
        if self.validate():
            king = self.move_from['square'].remove()
            if king.color == 'light':
                rook_key = 'h1' if self.move_to['key'] == 'g1' else 'a1'
                rook_to_key = 'f1' if self.move_to['key'] == 'g1' else 'd1'
            else:
                rook_key = 'h8' if self.move_to['key'] == 'g8' else 'a8'
                rook_to_key = 'f8' if self.move_to['key'] == 'g8' else 'd8'
            rook = self.board[rook_key].remove()

            # Place the King and Rook in their new positions
            self.board.place_piece(king, self.move_to['square'].file, self.move_to['square'].rank ) # type: ignore (suppress Pylance warning for type we know is not None)
            self.board.place_piece(rook, rook_to_key[0], int(rook_to_key[1]) )

            # Mark the King and Rook as having moved
            self.flag_movement( king )
            self.flag_movement( rook ) # type: ignore since we know it's a Rook by now

            self.board.end_turn()
        else:
            return None
            # raise ValueError("Invalid castling move.")

    def __str__(self):
        return f"{self.piece.name} castles from {self.move_from['key']} to {self.move_to['key']}" 
    
    def __repr__(self):
        return f"ChessCastle({self.board}, {self.move_from['key']}, {self.move_to['key']}"
