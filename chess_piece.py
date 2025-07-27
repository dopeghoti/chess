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
    
    def __init__(self, color: str | None = None):
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
        return f'{self.color} {self.name}'

    def __eq__( self, other_piece ) -> bool:
        """Allow for such things as `if some_chess_piece in{ Rook('light'), Queen('dark') }:` """
        return isinstance( other_piece, ChessPiece ) and \
                self.color == other_piece.color and \
                self.name == other_piece.name

    def __hash__( self ):
        return hash( ( self.color, self.name ) )

class Pawn(ChessPiece):
    """Represents a pawn chess piece."""
    glyph = {
            'light' : '♙',
            'dark'  : '♟' }
    symbol = ''
    def __init__(self, color: str):
        super().__init__(color)

class Rook(ChessPiece):
    """Represents a rook chess piece."""
    glyph = {
            'light' : '♖',
            'dark'  : '♜' }
    symbol = 'R'
    def __init__(self, color: str):
        super().__init__(color)

class Knight(ChessPiece):
    """Represents a knight chess piece."""
    glyph = {
            'light' : '♘',
            'dark'  : '♞' }
    symbol = 'N'
    def __init__(self, color: str):
        super().__init__(color)

class Bishop(ChessPiece):
    """Represents a bishop chess piece."""
    glyph = {
            'light' : '♗',
            'dark'  : '♝' }
    symbol = 'B'
    def __init__(self, color: str):
        super().__init__(color)

class Queen(ChessPiece):
    """Represents a queen chess piece."""
    glyph = {
            'light' : '♕',
            'dark'  : '♛' }
    symbol = 'Q'
    def __init__(self, color: str):
        super().__init__(color)

class King(ChessPiece):
    """Represents a king chess piece."""
    glyph = {
            'light' : '♔',
            'dark'  : '♚' }
    symbol = 'K'
    def __init__(self, color: str):
        super().__init__(color)

def main():
    p = [
            Queen('light'),
            King('dark')
            ]
    for _ in p:
        print( f'{_} is a {repr(_)}.' )

if __name__ == '__main__':
    main()
