from chess_piece import *
from color import Color as C

class Square:
    def __init__(self, color: str | None = None, file: str | None = None, rank: int | None = None ):
        if not all( [ color, file, rank ] ):
            raise ValueError( f"Color, file, and rank must be specified for Square.  {color=}, {file=}, {rank=}" )
        if color.lower() not in [ 'light', 'dark' ]: # type: ignore (suppress Pylance warning for str we know by now is not None)
            raise ValueError( f"Color must be either 'light' or 'dark'.  {color=}." )
        if int(rank) - 1 not in range( 8 ): # type: ignore (suppress Pylance warning for int we know by now is not None)
            raise ValueError( f"Rank must be between 1 and 8.  {rank=}" )
        if file.lower() not in 'abcdefgh': # type: ignore (suppress Pylance warning for str we know by now is not None)
            raise ValueError( f"File must be one of 'a' to 'h'.  {file=}" )
        self.color, self.file, self.rank, self.occupant = color.lower(), file.lower(), rank, None # type: ignore (suppress Pylance warnings for types we know by now are not None)
        self.key = f"{self.file.lower()}{self.rank}"

    def is_occupied(self) -> bool:
        """Check if the square is occupied by a chess piece."""
        return self.occupant is not None

    def contains(self) -> ChessPiece | None:
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

    def promote( self, new_piece_class: type[ChessPiece] = Queen ) -> None:
        """If there is a Pawn on square, promote it to a higher piece."""
        if self.occupant is None:
            raise ValueError( "Square is empty. Cannot promote a piece.")
        if not isinstance(self.occupant, Pawn):
            raise TypeError( "Only Pawns can be promoted." )
        if not issubclass(new_piece_class, ChessPiece):
            raise TypeError( f"New piece must be a subclass of ChessPiece. Received: {new_piece_class}" )
        if not new_piece_class in [ Queen, Rook, Bishop, Knight ]:
            raise ValueError( f"New piece must be one of Queen, Rook, Bishop, or Knight. Received: {new_piece_class}" )
        self.occupant = new_piece_class(self.occupant.color)

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

    def end_turn( self ) -> None:
        self.turn = 'light' if self.turn == 'dark' else 'dark'

    def place_piece(self, piece: ChessPiece, file: str, rank: int) -> None:
        """place a chess piece on the board at the specified file and rank."""
        square_key = f"{file.lower()}{rank}"
        if square_key not in self.squares:
            raise ValueError(f"Invalid square: {square_key}. Must be in the format 'a1' to 'h8'.")
        self.squares[square_key].place(piece)

    def __getitem__( self, square_key: str ) -> Square:
        """Get the square at the specified key."""
        if square_key not in self.squares:
            raise ValueError(f"Invalid square: {square_key}. Must be in the format 'a1' to 'h8'.")
        return self.squares[square_key]

    def get_piece(self, square_key: str) -> ChessPiece | None:
        """Get the chess piece at the specified square."""
        if square_key not in self.squares:
            raise ValueError(f"Invalid square: {square_key}. Must be in the format 'a1' to 'h8'.")
        return self.squares[square_key].contains()

    def move_piece( self, from_square: Square, to_square: Square ) -> None:
        """Move a piece from one Square to another.
        
        This ls literally just moving the piece, it is not a Chess Move and does not
        validate game logic or rules.  That will be handled by ChessMove.
        """
        if not isinstance(from_square, Square) or not isinstance(to_square, Square):
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
