from chess_piece import *
from color import Color as C
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

    # def promote( self, new_piece_class: type[ChessPiece] = Queen ) -> None:
    #     """If there is a Pawn on square, promote it to a higher piece."""
    #     # TODO: Move this to the Pawn ChessPiece, and a companion piece into ChessMove
    #     if self.occupant is None:
    #         raise ValueError( "Square is empty. Cannot promote a piece.")
    #     if not isinstance(self.occupant, Pawn):
    #         raise TypeError( "Only Pawns can be promoted." )
    #     if not issubclass(new_piece_class, ChessPiece):
    #         raise TypeError( f"New piece must be a subclass of ChessPiece. Received: {new_piece_class}" )
    #     if not new_piece_class in [ Queen, Rook, Bishop, Knight ]:
    #         raise ValueError( f"New piece must be one of Queen, Rook, Bishop, or Knight. Received: {new_piece_class}" )
    #     self.occupant = new_piece_class(self.occupant.color)

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
        if not isinstance(other, ChessBoard):
            return False
        return all( self.squares[key] == other.squares[key] for key in self.squares )
    
    def __hash__( self ) -> int:
        """Returns a hash of the chess board."""
        # TODO: This hash won't work because its members are mutable. Make it instead calculate from immutable copies?
        return hash( [ self.squares, self.turn, self.turns, self.game_states ] )

    def end_turn( self ) -> None:
        # When ending a side's half-turn, we need to reset the en passant flag for all pawns of that side.
        for _ in self.squares.values():
            piece = _.contains()
            if isinstance(piece, Pawn) and piece.color != self.turn:
                piece.lower_passant_flag()
        # TODO: Look for Kings in check
        # TODO: Look for checkmates (!)  Hoo boy, this will be fun.
        # TODO: Look for repetition stalemates once we save board states
        # TODO: Look for stalemate: no legal moves
        # TODO: Look for 50-turn draw
        # TODO: Look for forced draw due to lack of pieces on both sides
        if self.turn == 'light':
            self.turns += 1
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
        for move in piece.get_move_pattern():
            target_file_ord = ord(square_key[0]) + move[0]
            target_rank = int(square_key[1]) + move[1]
            if 97 <= target_file_ord <= 104 and 1 <= target_rank <= 8:
                target_square_key = f"{chr(target_file_ord)}{target_rank}"
                target_square = self.squares[target_square_key]
                if not target_square.is_occupied(): # Occupied squares are not legal moves
                    legal_moves.append(target_square)
            if piece.is_sliding_piece():
                # For sliding pieces, we need to check all squares in the direction of movement
                step_file_ord = ord(square_key[0]) + move[0]
                step_rank = int(square_key[1]) + move[1]
                while 97 <= step_file_ord <= 104 and 1 <= step_rank <= 8:
                    step_square_key = f"{chr(step_file_ord)}{step_rank}"
                    step_square = self.squares[step_square_key]
                    if not step_square.is_occupied():
                        legal_moves.append(step_square)
                    else:
                        break
                    step_file_ord += move[0]
                    step_rank += move[1]
        # Remove duplicates and return the list of legal moves
        return list(set(legal_moves))
    
    def get_legal_captures( self, square_key: str ) -> list[Square]:
        """Get all legal captures for the piece on the specified square."""
        if square_key not in self.squares:
            raise ValueError(f"Invalid square: {square_key}. Must be in the format 'a1' to 'h8'.")
        piece = self.squares[square_key].contains()
        if piece is None:
            return [] # No piece on the square, no legal captures
        # Get the piece's capture pattern and translate it to squares
        legal_captures = []
        for capture in piece.get_capture_pattern():
            target_file_ord = ord(square_key[0]) + capture[0]
            target_rank = int(square_key[1]) + capture[1]
            if 97 <= target_file_ord <= 104 and 1 <= target_rank <= 8:
                target_square_key = f"{chr(target_file_ord)}{target_rank}"
                target_square = self.squares[target_square_key]
                if target_square is not None:
                    if target_square.is_occupied() and target_square.contains().color != piece.color:
                        # If we are capturing with a Pawn, and the capture is en passant,
                        # we need to check if the target square is vulnerable
                        if isinstance(piece, Pawn) and capture in [(-1, 0), (1, 0)]:
                            if target_square.contains().is_vulnerable(): 
                                # Check to see if the square behind the target square is empty
                                final_rank = target_rank + piece.direction
                                final_square_key = f"{target_square_key[0]}{final_rank}"
                                if not self.squares[final_square_key].is_occupied():
                                    legal_captures.append(target_square_key)
                        else:
                            legal_captures.append(target_square_key)
            if piece.is_sliding_piece():
                # For sliding pieces, we need to check all squares in the direction of capture
                step_file_ord = ord(square_key[0]) + capture[0]
                step_rank = int(square_key[1]) + capture[1]
                while 97 <= step_file_ord <= 104 and 1 <= step_rank <= 8:
                    step_square_key = f"{chr(step_file_ord)}{step_rank}"
                    step_square = self.squares[step_square_key]
                    if step_square.is_occupied() and step_square.contains().color != piece.color:
                        legal_captures.append(step_square_key)
                        break
                    elif step_square.is_occupied():
                        break
                    step_file_ord += capture[0]
                    step_rank += capture[1]
        # Remove duplicates and return the list of legal captures
        return list(set(legal_captures))

    def move_piece( self, from_key: str, to_key: str ) -> None:
        """Move a piece from one Square to another.
        
        This ls literally just moving the piece, it is not a Chess Move and does not
        validate game logic or rules.  That will be handled by ChessMove.
        """

        if from_key not in self.squares or to_key not in self.squares:
            raise ValueError(f"Invalid square keys: {from_key}, {to_key}. Must be in the format 'a1' to 'h8'.")
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
        
        # Start from the square after the attacking piece
        current_file_ord = ord( from_square.file ) + file_step
        current_rank = from_square.rank + rank_step

        # Check each square in the path (excluding the target itself)
        while( current_file_ord != ord(to_square.file) or current_rank != to_square.rank ):
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
