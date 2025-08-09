from chess_piece import *
from color import Color as C
from copy import copy, deepcopy
from typing import Optional

class Square:
    def __init__(self, color: Optional[str] = None, file: Optional[str] = None, rank: Optional[int] = None ):
        if None in (color, file, rank):
            raise ValueError( f"Color, file, and rank must be specified for Square.  {color=}, {file=}, {rank=}" )
        if color is not None and color.lower() not in [ 'light', 'dark' ]:
            raise ValueError( f"Color must be either 'light' or 'dark'.  {color=}." )
        if rank is not None and int(rank) - 1 not in range( 8 ):
            raise ValueError( f"Rank must be between 1 and 8.  {rank=}" )
        if file is not None and file.lower() not in 'abcdefgh':
            raise ValueError( f"File must be one of 'a' to 'h'.  {file=}" )
        self.color, self.file, self.rank, self.occupant = color.lower(), file.lower(), rank, None
        self.key = f"{self.file}{self.rank}"  # e.g. 'a1', 'h8'

    def __hash__( self ) -> int:
        """Returns a hash of the square."""
        return hash((self.color, self.file, self.rank, self.occupant, self.key))

    def __eq__( self, other ) -> bool:
        """Check if two squares are equal based on color, file, rank, and occupant."""
        if not isinstance(other, Square):
            return False
        return all( (
            self.color == other.color,
            self.file == other.file,
            self.rank == other.rank,
            self.occupant == other.occupant) )

    def __deepcopy__( self, memo ):
        """Create a deep copy of the square."""
        new_square = self.__class__(
            deepcopy( self.color, memo ),
            deepcopy( self.file, memo ),
            deepcopy( self.rank, memo )
        )
        if self.is_occupied():
            new_square.occupant = deepcopy( self.occupant, memo )
        return new_square

    def is_occupied(self) -> bool:
        """Check if the square is occupied by a chess piece."""
        return self.occupant is not None

    def contains(self) -> Optional[ChessPiece]:
            return self.occupant

    def place( self, piece: ChessPiece ) -> None:
        """place a chess piece on the square."""
        if self.occupant is not None:
            raise ValueError( f"Square is already occupied with a {self.occupant}. Cannot place another piece.")
        if not isinstance(piece, ChessPiece):
            raise TypeError( f"Only ChessPiece objects can be placed on a square. Received: {type(piece)}")
        self.occupant = piece

    def remove( self ) -> ChessPiece:
        """Remove the chess piece from the square."""
        if self.occupant is None:
            raise ValueError( "Square is empty. Cannot remove a piece.")
        piece = self.occupant
        self.occupant = None
        return piece

    def __str__( self ) -> str:
        fgc = C.WHITE
        if self.color == 'dark':
            bgc = C.BLACK
        else:
            bgc = C.BLUE
        if self.occupant is not None:
            piece = str(self.occupant)
        else:
            piece = ' '
        return fgc( f' {piece} ', fgc, bgc, True )

class ChessBoard:
    def __init__(self):
        self.squares = {
                f"{file}{rank}": Square(
                    color = 'light' if( ord(file) - ord('a') + rank ) % 2 == 0 else 'dark',
                    file=file,
                    rank=rank)
                for file in 'abcdefgh' for rank in range(1, 9)
                }
        self.turn = 'light'
        self.turns = 0
        self.game_states = {}

    def __eq__( self, other ) -> bool:
        """Check if two chess boards are equal based on their squares."""
        # Naturally, the Other item must be a ChessBoard.
        if not isinstance(other, ChessBoard):
            return False
        # Check if the number of squares and their contents are the same
        if len( self.squares ) != len( other.squares ) or not all( [ self.squares[key] == other.squares[key] for key in self.squares ] ):
            return False
        return all( ( self.turn == other.turn, self.turns == other.turns, self.game_states == other.game_states ) )

    def __hash__( self ) -> int:
        """Returns a hash of the chess board."""
        # First we need to make an immutable representation of the Squares dictionary:
        squares_tuple = tuple(sorted((key, hash(value)) for key, value in self.squares.items()))
        # Now, same for game states:
        game_states_tuple = tuple(sorted((key, value) for key, value in self.game_states.items()))
        # Finally, we can return a hash of the immutables:
        return hash( ( self.turn, self.turns, squares_tuple, game_states_tuple ) )

    def __deepcopy__( self, memo ):
        """Create an exact copy of this chess board.  Primarily used for the following purposes:
         - Saving game states
         - Looking for discovered checks in proposed moves"""
        new_board = ChessBoard()
        for k, v in self.squares.items():
            new_board.squares[k] = deepcopy(v)
        new_board.turn = str( self.turn )
        new_board.turns = int( self.turns )
        new_board.game_states = self.game_states.copy()
        return new_board

    def end_turn( self ) -> None:
        # When ending a side's half-turn, we need to reset the en passant flag for all pawns of that side.
        for _ in self.squares.values():
            piece = _.contains()
            if isinstance(piece, Pawn) and piece.color != self.turn:
                piece.lower_passant_flag()
            if isinstance(piece, King) and piece.color != self.turn:
                if self.is_in_check_from( _, self.turn ):
                    piece.raise_check_flag()
        # DONE: Clear en-passant vulnerable flags
        # DONE: Look for Kings in check
        # TODO: Look for checkmates (!)  Hoo boy, this will be fun.
        # TODO: Look for repetition stalemates once we save board states
        # TODO: Look for stalemate: no legal moves
        # TODO: Look for 50-turn draw
        # TODO: Look for forced draw due to lack of pieces on both sides
        if self.turn == 'light':
            self.turns += 1


        self.game_states[ ( self.turns, self.turn ) ] = deepcopy( self )
        self.turn = 'light' if self.turn == 'dark' else 'dark'

    def place_piece(self, piece: ChessPiece, file: str, rank: int) -> None:
        """place a chess piece on the board at the specified file and rank."""
        square_key = f"{file.lower()}{rank}"
        if square_key not in self.squares:
            raise ValueError(f"Invalid square: {square_key}. Must be in the format 'a1' to 'h8'.")
        self.squares[square_key].place(piece)

    def remove_piece(self, key: str) -> ChessPiece:
        """Remove a chess piece from the board at the specified file and rank."""
        if key not in self.squares:
            raise ValueError(f"Invalid square: {key}. Must be in the format 'a1' to 'h8'.")
        if self.squares[key].is_occupied():
            return self.squares[key].remove()
        else:
            raise ValueError(f"No piece on {key} to remove.")

    def __getitem__( self, square_key: str ) -> Square:
        """Get the square at the specified key."""
        if square_key not in self.squares:
            raise ValueError(f"Invalid square: {square_key}. Must be in the format 'a1' to 'h8'.")
        return self.squares[square_key]

    def get_piece(self, square_key: str) -> Optional[ChessPiece]:
        """Get the chess piece at the specified square."""
        if square_key not in self.squares:
            raise ValueError(f"Invalid square: {square_key}. Must be in the format 'a1' to 'h8'.")
        return self.squares[square_key].contains()

    def is_discovered_check( self, from_square_key: str, to_square_key: str, is_capture: bool = False ) -> bool:
        """Determine whether a proposed move would be a disovered check, so that
        it can be eliminated from a proposed list of moves or captures to return to ChessMove"""
        # Make a copy of the board for starters
        hypothetical = deepcopy( self )
        # We have a from_square_key and a to_square_key.  Let's get keys and squares for both.
        from_square = hypothetical[from_square_key]
        to_square = hypothetical[to_square_key]
        moving_player = self.turn
        passive_player = 'light' if self.turn == 'dark' else 'dark'

        if is_capture:
            # If this is an en passant capture, we need to remove the pawn and then shift the to_square
            # before making the hypothetical move.  So let's determine if this is en-passant:
            if is_capture and from_square.rank == to_square.rank and isinstance( from_square.contains(), Pawn ): # it is!
                to_square.remove()
                new_rank = from_square.rank + from_square.contains().direction # type: ignore as we know origin square contains a Pawn
                to_square = hypothetical[ f'{to_square.file}{str(new_rank)}']
                to_square_key = to_square.key
            else: # It's a capture, but not en passant
                to_square.remove()
        hypothetical.move_piece( from_square_key, to_square_key )
        # Go through the checklist for discovered-check sitiations
        for square_key in hypothetical.squares:
            piece = hypothetical.get_piece(square_key)
            if piece is not None and isinstance( piece, King ) and piece.color == moving_player:
                if hypothetical.is_in_check_from( hypothetical.squares[square_key], passive_player ):
                    # We have a discovered check!
                    return True
        # Well, I guess it's not.
        return False


    def get_legal_moves( self, square_key: str ) -> list[Square]:
        """Get all legal moves for the piece on the specified square.
        Captures are NOT included in the list of legal moves, only moves to empty squares."""
        if square_key not in self.squares:
            raise ValueError(f"Invalid square: {square_key}. Must be in the format 'a1' to 'h8'.")
        piece = self.squares[square_key].contains()
        if piece is None:
            return []  # No piece on the square, no legal moves

        # Get the piece's movement pattern and translate it to squares
        legal_moves = []
        possible_moves = []

        for file_dir, rank_dir in piece.get_move_pattern():
            current_file_ord = ord(square_key[0])
            current_rank = int(square_key[1])

            while True: # I hate infinite loops but we _will_ break out eventually.
                current_file_ord += file_dir
                current_rank += rank_dir

                if not ( 97 <= current_file_ord <= 104 and 1 <= current_rank <= 8 ):
                    # We're off the board, and so we
                    break
                target_square = self.squares[f'{chr(current_file_ord)}{current_rank}']

                if target_square.is_occupied():
                    # The path is blocked by a piece, and so we
                    break

                possible_moves.append( target_square )

                if not piece.is_sliding_piece():
                    # No further squares in this direction to check, and so we
                    break

        # Remove duplicates and return the list of legal moves
        possible_moves = list( set( possible_moves ) )

        # Okay, now we have a list of presumable legal moves.  For each one, we need to
        # see if it would be a discovered check and, if so, remove it from the list.
        for possible_move in possible_moves:
            if not self.is_discovered_check( square_key, possible_move.key, False ):
                legal_moves.append( possible_move )
        return list(set(legal_moves))

    def get_legal_captures( self, square_key: str ) -> list[Square]:
        """Get all legal captures for the piece on the specified square."""
        if square_key not in self.squares:
            raise ValueError(f"Invalid square: {square_key}. Must be in the format 'a1' to 'h8'.")
        piece = self.squares[square_key].contains()
        if piece is None:
            return [] # No piece on the square, no legal captures
        # Get the piece's capture pattern and translate it to squares
        possible_captures = []
        legal_captures = []

        for capture in piece.get_capture_pattern():
            target_file_ord = ord(square_key[0]) + capture[0]
            target_rank = int(square_key[1]) + capture[1]
            if 97 <= target_file_ord <= 104 and 1 <= target_rank <= 8:
                target_square_key = f"{chr(target_file_ord)}{target_rank}"
                target_square = self.squares[target_square_key]
                if target_square is not None:
                    if target_square.is_occupied() and target_square.contains().color != piece.color:
                        captured_piece = self[target_square_key].contains()
                        # If we are capturing with a Pawn, and the capture is en passant,
                        # we need to check if the target square is vulnerable
                        if isinstance( piece, Pawn ) and isinstance ( captured_piece, Pawn ) and capture in [ ( -1, 0 ), ( 1, 0 ) ]:
                            if captured_piece.is_vulnerable():
                                # Check to see if the square behind the target square is empty
                                final_rank = target_rank + piece.direction
                                final_square_key = f"{target_square_key[0]}{final_rank}"
                                if not self.squares[final_square_key].is_occupied():
                                    possible_captures.append(target_square)
                        else:
                            possible_captures.append(target_square)
            if piece.is_sliding_piece():
                # For sliding pieces, we need to check all squares in the direction of capture
                step_file_ord = ord(square_key[0]) + capture[0]
                step_rank = int(square_key[1]) + capture[1]
                while 97 <= step_file_ord <= 104 and 1 <= step_rank <= 8:
                    step_square_key = f"{chr(step_file_ord)}{step_rank}"
                    step_square = self.squares[step_square_key]
                    if step_square.is_occupied() and step_square.contains().color != piece.color:
                        possible_captures.append(step_square)
                        break
                    elif step_square.is_occupied():
                        break
                    step_file_ord += capture[0]
                    step_rank += capture[1]
        possible_captures = list( set( possible_captures ) ) # Strip duplicates

        # Okay, now we have a list of presumable legal captures.  For each one, we need to
        # see if it would be a discovered check and, if so, remove it from the list.
        for possible_capture in possible_captures:
            if not self.is_discovered_check( square_key, possible_capture.key, True ):
                legal_captures.append( possible_capture )
        # Remove duplicates and return the list of legal captures
        return list(set(legal_captures))

    def move_piece( self, from_key: str, to_key: str ) -> None:
        """Move a piece from one Square to another.

        This ls literally just moving the piece, it is not a Chess Move and does not
        validate game logic or rules.  That will be handled by ChessMetaMove.
        """

        if from_key not in self.squares or to_key not in self.squares:
            raise ValueError(f"Invalid square keys: {from_key}, {to_key}. Must both be in the format 'a1' to 'h8'.")
        if from_key == to_key:
            raise ValueError(f"Cannot move piece to the same square: {from_key}.")

        from_square = self.squares[from_key]
        to_square = self.squares[to_key]

        if not all( ( isinstance(from_square, Square), isinstance(to_square, Square) ) ):
            raise TypeError("from_square and to_square must be instances of Square.")
        if not from_square.is_occupied():
            raise ValueError(f"No piece on {from_square} to move.")
        if to_square.is_occupied():
            raise ValueError(f"Cannot move to {to_square}. It is already occupied by {to_square.contains()}.")

        to_square.place( from_square.remove() )

    def clear(self):
        """Reset the chess board by removing all pieces."""
        for square in self.squares.values():
            if square.is_occupied():
                square.remove()

    def setup(self):
        """Set up the chess board with the initial positions of the pieces."""
        self.clear()
        # Light always goes first.
        self.turn = 'light'
        self.turns = 0
        self.game_states = {}

        # place Pawns
        for file in 'abcdefgh':
            self.place_piece(Pawn('light'), file, 2)
            self.place_piece(Pawn('dark'), file, 7)

        # place Rooks
        self.place_piece(Rook('light'), 'a', 1)
        self.place_piece(Rook('light'), 'h', 1)
        self.place_piece(Rook('dark'), 'a', 8)
        self.place_piece(Rook('dark'), 'h', 8)

        # place Knights
        self.place_piece(Knight('light'), 'b', 1)
        self.place_piece(Knight('light'), 'g', 1)
        self.place_piece(Knight('dark'), 'b', 8)
        self.place_piece(Knight('dark'), 'g', 8)

        # place Bishops
        self.place_piece(Bishop('light'), 'c', 1)
        self.place_piece(Bishop('light'), 'f', 1)
        self.place_piece(Bishop('dark'), 'c', 8)
        self.place_piece(Bishop('dark'), 'f', 8)

        # place Queens
        self.place_piece(Queen('light'), 'd', 1)
        self.place_piece(Queen('dark'), 'd', 8)

        # place Kings
        self.place_piece(King('light'), 'e', 1)
        self.place_piece(King('dark'), 'e', 8)

    def is_in_check_from( self, target_square: Square, attacking_color: str) -> bool:
        """Determine whether a specified square is under attack from the specified player's pieces."""
        for square_key, square in self.squares.items():
            piece = square.contains()
            if not piece or piece.color != attacking_color:
                continue

            file_offset = ord(target_square.file) - ord(square.file)
            rank_offset = target_square.rank - square.rank # type: ignore

            # If there's no offset, it's the same square, so no attack
            if file_offset == 0 and rank_offset == 0:
                continue

            # Determine the base direction of the attack (e.g., (0, -7) -> (0, -1))
            file_dir = 0 if file_offset == 0 else (1 if file_offset > 0 else -1)
            rank_dir = 0 if rank_offset == 0 else (1 if rank_offset > 0 else -1)

            # For Pawns, the capture pattern is exact and non-sliding
            if isinstance(piece, Pawn):
                if (file_offset, rank_offset) in piece.get_capture_pattern():
                    return True
                else:
                    continue # Pawns don't slide, so move to the next piece

            # For all other pieces (sliding and non-sliding like King/Knight)
            if (file_dir, rank_dir) in piece.get_capture_pattern():
                if not piece.is_sliding_piece():
                    # For King/Knight, the offset must be exact
                    if (file_offset, rank_offset) in piece.get_capture_pattern():
                        return True
                else:
                    # For sliding pieces, check if the path is clear
                    if self._is_sliding_path_clear(square, target_square, file_offset, rank_offset):
                        return True

        return False

    def _is_sliding_path_clear( self, from_square, to_square, file_offset, rank_offset) -> bool:
        """Check if the path is clear for a sliding piece's attack."""
        file_step = 0 if file_offset == 0 else (1 if file_offset > 0 else -1 )
        rank_step = 0 if rank_offset == 0 else (1 if rank_offset > 0 else -1 )

        # We're not currently handling diagonals properly.  This thinks that Qd1 can see Ke8 for example.  So let's rule out diagonals that
        # don't actually line up.
        if file_offset and rank_offset and abs( file_offset ) != abs( rank_offset ):
            # This is not on the _same_ diagonal, so-
            return False

        # Start from the square after the attacking piece
        current_file_ord = ord( from_square.file ) + file_step
        current_rank = from_square.rank + rank_step

        # Check each square in the path (excluding the target itself)
        while( current_file_ord != ord(to_square.file) or current_rank != to_square.rank ) and ( 0 < current_rank < 9 ) and ( 96 < current_file_ord < 105 ):
              current_square_key = f'{chr(current_file_ord)}{current_rank}'
              if self.squares[current_square_key].is_occupied():
                  return False # Path is blocked
              current_file_ord += file_step
              current_rank += rank_step
        return True # Path is clear

    def __str__(self) -> str:
        game_board = '    A  B  C  D  E  F  G  H \n'
        for rank in range( 8, 0, -1 ):
            game_board += f'{rank}: '
            for file in 'abcdefgh':
                square = self.squares[f'{file}{str(rank)}']
                game_board += f'{square}'
            game_board += '\n'
        game_board += '    A  B  C  D  E  F  G  H \n'
        return game_board

def main():
    b = ChessBoard()
    b.setup()
    print( b )

if __name__ == '__main__':
    main()
