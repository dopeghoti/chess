from typing import Optional

class ChessPiece:
    """It should be noted that because we're (trying to) use the Unicode
    glyphs for terminal representation of chess pieces, the light
    pieces will appear dark and vice-versa.  However, just flipping
    them to have the visually correct appearance won't work because
    frequently the black pawn Unicode glyph is replaced by the black
    pawn Emoji, which _does_ appear as a dark piece, which looks even
    more incongruous, so for now we'll juse endure the players using
    the "wrong" pieces when they are viewed on a terminal UI."""
    # Define placeholder glyphs for __str()__, meant to be overridded by subclasses
    glyph = {
            'light' : '¡',
            'dark'  : '!' }
    symbol = 'X' # For usage in move notation; should be overridden by subclass
    
    def __init__(self, color: Optional[str] = None ):
        """Meant to be superceded by a subclass for each type of piece."""
        if color is None:
            raise ValueError( "Color must be specified for ChessPiece" )
        elif color not in [ 'light', 'dark' ]:
            raise ValueError( f"Color must be either 'light' or 'dark'.  {color=}." )
        self.color = color
        if type(self) == ChessPiece:
            raise NotImplementedError("ChessPiece should not be instantiated directly")
        self.name = self.__class__.__name__.lower() # e. g. a Knight instance's name will be 'knight'

    def __str__( self ):
        return self.__class__.glyph[self.color]

    def __repr__( self ) -> str:
        """Return e. g. 'Rook ( "light" )'."""
        return f'{self.__class__.__name__.capitalize()}( "{self.color}" )'

    def __eq__( self, other_piece ) -> bool:
        """Allow for such things as `if some_chess_piece in{ Rook('light'), Queen('dark') }:` """
        if isinstance( other_piece, ChessPiece ):
            return all( [ self.color == other_piece.color, self.name == other_piece.name ] )
        else:
            # It's not even a ChessPiece, so it's oviously not equal
            return False

    def __hash__( self ) -> int:
        return hash( ( self.color, self.name ) )
    
    def get_move_pattern( self ) -> list[ tuple[ int, int ] ]:
        """Returns a list of (file_offset, rank_offset) tuples for valid movement pattern.

        Positive file_offset means moving toward 'h'; negative toward 'a'.
        Positive rank_offset means moving toward 8; negative toward 1.

        These are _relative_ movement directions."""
        raise NotImplementedError( 'Must be implemented by ChessPiece subclasses.' )

    def get_capture_pattern( self ) -> list[ tuple[ int, int ] ]:
        """Returns a list of (file_offset, rank_offset) tuples for valid capture / attack locations.

        For most pieces this is identical to the movement pattern; pawns are, shall we say, Special."""
        return self.get_move_pattern()

    def is_sliding_piece( self ) -> bool:
        """Return True if the piece can move an arbitrary number of squares in a direction.

        Used to determine if path-clearing logic is needed.  Only for Rook, Bishop, and Queen."""
        return False
    
    def is_vulnerable( self ) -> bool:
        """Return True if the piece is vulnerable to en passant capture."""
        if hasattr( self, 'vulnerable' ):
            return self.vulnerable
        else:
            raise AttributeError( f"{self} does not have a 'vulnerable' attribute." )

    def raise_moved_flag( self ) -> None:
        """Set the has_moved flag to True.  This is used for castling."""
        if hasattr( self, 'has_moved' ):
            self.has_moved = True
        else:
            raise AttributeError( f"{self} does not have a 'has_moved' attribute." )
    
    def raise_passant_flag( self ) -> None:
        """Set the vulnerable flag to True.  This is used for en passant."""
        if hasattr( self, 'vulnerable' ):
            self.vulnerable = True
        else:
            raise AttributeError( f"{self} does not have a 'vulnerable' attribute." )
        
    def lower_passant_flag( self ) -> None:
        """Set the vulnerable flag to False.  This is used for en passant."""
        if hasattr( self, 'vulnerable' ):
            self.vulnerable = False
        else:
            raise AttributeError( f"{self} does not have a 'vulnerable' attribute." )

class Pawn(ChessPiece):
    """Represents a pawn chess piece."""
    glyph = {
            'light' : '♙',
            'dark'  : '♟' }
    symbol = ''
    def __init__(self, color: str):
        super().__init__(color)
        self.vulnerable = False  # Track if the pawn can be captured en passant
        self.has_moved = False # For tracking first-move option for moving two spaces forward
        self.direction = 1 if self.color == 'light' else -1 # for setting which direction the Pawn can advance based on color

    def get_move_pattern( self ) -> list[ tuple[ int, int ] ]:
        """Pawns move forward only.  "Forward" is defined by piece color."""
        moves = [ ( 0, self.direction ) ]

        # If we have not yet moved, we also have this option:
        if not self.has_moved:
            moves.append( ( 0, 2 * self.direction ) )
        return moves

    def get_capture_pattern( self ) -> list[ tuple[ int, int ] ]:
        """Pawns capture diagonally forward, and can capture a lateral neighbor en-pessant."""
        captures = [
                ( -1, self.direction ),  # Diagonal left
                (  1, self.direction ),  # Diagonal right
                ( -1, 0 ),               # en-pessant left (validation will be in ChessCapture)
                (  1, 0 )                # en-pessant right (validation will be in ChessCapture)t
                ]
        return captures

class Rook(ChessPiece):
    """Represents a rook chess piece."""
    glyph = {
            'light' : '♖',
            'dark'  : '♜' }
    symbol = 'R'
    def __init__(self, color: str):
        super().__init__(color)
        self.has_moved = False  # Track whether the rook has moved for castling purposes

    def is_sliding_piece( self ) -> bool:
        """Rooks can slide."""
        return True

    def get_move_pattern( self ) -> list[ tuple[ int, int ] ]:
        """Rooks move along ranks and files only."""
        moves = [
                (  1,  0 ),
                ( -1,  0 ),
                (  0,  1 ),
                (  0, -1 )
                ]
        return moves

class Knight(ChessPiece):
    """Represents a knight chess piece."""
    glyph = {
            'light' : '♘',
            'dark'  : '♞' }
    symbol = 'N'
    def __init__(self, color: str):
        super().__init__(color)

    def get_move_pattern( self ) -> list[ tuple[ int, int ] ]:
        """Knights move either ±2 ranks and ±1 file or vice verse."""
        moves = [
                (  1,  2 ),
                ( -1,  2 ),
                (  1, -2 ),
                ( -1, -2 ),
                ( -2,  1 ),
                (  2,  1 ),
                ( -2, -1 ),
                (  2, -1 )
                ]
        return moves

class Bishop(ChessPiece):
    """Represents a bishop chess piece."""
    glyph = {
            'light' : '♗',
            'dark'  : '♝' }
    symbol = 'B'
    def __init__(self, color: str):
        super().__init__(color)

    def is_sliding_piece( self ) -> bool:
        """Bishops can slide."""
        return True

    def get_move_pattern( self ) -> list[ tuple[ int, int ] ]:
        """Bishops move along diagonals only."""
        moves = [
                (  1,  1 ),
                ( -1,  1 ),
                ( -1, -1 ),
                (  1, -1 )
                ]
        return moves

class Queen(ChessPiece):
    """Represents a queen chess piece."""
    glyph = {
            'light' : '♕',
            'dark'  : '♛' }
    symbol = 'Q'
    def __init__(self, color: str):
        super().__init__(color)

    def is_sliding_piece( self ) -> bool:
        """Queens can slide."""
        return True

    def get_move_pattern( self ) -> list[ tuple[ int, int ] ]:
        """Queens move in diagonals, ranks, and files."""
        moves = [
                (  1,  0 ),
                ( -1,  0 ),
                (  0,  1 ),
                (  0, -1 ),
                (  1,  1 ),
                ( -1,  1 ),
                ( -1, -1 ),
                (  1, -1 )
                ]
        return moves

class King(ChessPiece):
    """Represents a king chess piece."""
    glyph = {
            'light' : '♔',
            'dark'  : '♚' }
    symbol = 'K'
    def __init__(self, color: str):
        super().__init__(color)
        self.has_moved = False  # Track whether the king has moved for castling purposes
        self.has_been_in_check = False  # Track whether the king has been in check at any point for castling purposes

    def get_move_pattern( self ) -> list[ tuple[ int, int ] ]:
        """Kings move in diagonals, ranks, and files, but only one space."""
        moves = [
                (  1,  0 ),
                ( -1,  0 ),
                (  0,  1 ),
                (  0, -1 ),
                (  1,  1 ),
                ( -1,  1 ),
                ( -1, -1 ),
                (  1, -1 )
                ]
        return moves

def main():
    p = [
            Queen('light'),
            King('dark')
            ]
    for _ in p:
        print( f'{_} is a {repr(_)}.' )

if __name__ == '__main__':
    main()
