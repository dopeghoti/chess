from chess_piece import *
from chess_board import ChessBoard
from chess_move import ChessMove, ChessCapture, ChessCastle, ChessMetaMove as CM
from typing import Optional, Union
from chess_exception import *
import re

class ChessNotationConverter:
    """Converts between long algebraic notation and standard algebraic notation"""

    def __init__(self, board: ChessBoard):
        self.board = board

    def long_to_algebraic(self, long_notation: str) -> str:
        """Convert long notation (e.g., 'e2e4', 'b1c3') to algebraic notation (e.g., 'e4', 'Nc3')
        
        Also handles extended long notation like 'f4xg5' by parsing it appropriately.
        """
        # Clean and parse the input
        clean_notation = long_notation.replace(' ', '').lower()
        
        # Handle extended long notation (e.g., 'f4xg5')
        if 'x' in clean_notation:
            parts = clean_notation.split('x')
            if len(parts) == 2:
                from_square = parts[0]
                to_square = parts[1]
                is_capture_notation = True
            else:
                raise ValueError(f"Invalid capture notation: {long_notation}")
        else:
            # Standard long notation (e.g., 'e2e4')
            if len(clean_notation) != 4:
                raise ValueError(f"Invalid long notation: {long_notation}. Expected format like 'e2e4'")
            from_square = clean_notation[:2]
            to_square = clean_notation[2:]
            is_capture_notation = False

        # Validate squares exist
        if from_square not in self.board.squares or to_square not in self.board.squares:
            raise ValueError(f"Invalid squares in notation: {long_notation}")

        piece = self.board.get_piece(from_square)
        if piece is None:
            raise ValueError(f"No piece on square {from_square}")

        # Check for castling first (special case)
        if isinstance(piece, King):
            castle_notation = self._check_castling(from_square, to_square)
            if castle_notation:
                return castle_notation

        # Determine if this is actually a capture
        target_piece = self.board.get_piece(to_square)
        is_actual_capture = target_piece is not None

        # Check for en passant (pawn capturing to empty square diagonally)
        if isinstance(piece, Pawn) and not is_actual_capture:
            file_diff = abs(ord(from_square[0]) - ord(to_square[0]))
            if file_diff == 1:  # Diagonal move to empty square = en passant
                is_actual_capture = True

        # Build the notation
        notation_parts = []

        # Add piece symbol (empty for pawns)
        notation_parts.append(piece.symbol)

        # Add disambiguation if needed
        disambiguation = self._get_disambiguation(piece, from_square, to_square, is_actual_capture)
        notation_parts.append(disambiguation)

        # Add capture marker
        if is_actual_capture:
            notation_parts.append('x')

        # Add destination square
        notation_parts.append(to_square)

        # TODO: Add promotion notation (=Q, =R, etc.) when promotion is implemented
        # TODO: Add check (+) and checkmate (#) indicators

        return ''.join(notation_parts)

    def _check_castling(self, from_square: str, to_square: str) -> Optional[str]:
        """Check if this move represents castling and return appropriate notation"""
        # Only check castling for king moves from starting positions
        if from_square not in ['e1', 'e8']:
            return None

        castling_moves = {
            ('e1', 'g1'): 'O-O',    # White kingside
            ('e1', 'c1'): 'O-O-O',  # White queenside
            ('e8', 'g8'): 'O-O',    # Black kingside
            ('e8', 'c8'): 'O-O-O'   # Black queenside
        }

        return castling_moves.get((from_square, to_square))

    def _get_disambiguation(self, piece: ChessPiece, from_square: str, to_square: str, is_capture: bool) -> str:
        """Determine if disambiguation is needed and return appropriate notation"""
        # For pawns capturing, always include the file
        if isinstance(piece, Pawn) and is_capture:
            return from_square[0]  # Return the file letter

        # For non-pawns, check if other pieces of same type can reach the destination
        if not isinstance(piece, Pawn):
            ambiguous_pieces = self._find_ambiguous_pieces(piece, from_square, to_square)

            if ambiguous_pieces:
                return self._resolve_ambiguity(from_square, ambiguous_pieces)

        return ''

    def _find_ambiguous_pieces(self, piece: ChessPiece, from_square: str, to_square: str) -> list[str]:
        """Find other pieces of the same type that can also reach the destination"""
        ambiguous_squares = []

        for square_key, square in self.board.squares.items():
            if square_key == from_square:
                continue

            other_piece = square.contains()
            if (other_piece and
                type(other_piece) == type(piece) and
                other_piece.color == piece.color):

                # Check if this piece can legally move to the destination
                legal_moves = self.board.get_legal_moves(square_key)
                legal_captures = self.board.get_legal_captures(square_key)

                target_square = self.board.squares[to_square]
                if target_square in legal_moves or target_square in legal_captures:
                    ambiguous_squares.append(square_key)

        return ambiguous_squares

    def _resolve_ambiguity(self, from_square: str, ambiguous_squares: list[str]) -> str:
        """Determine the minimum disambiguation needed"""
        from_file = from_square[0]
        from_rank = from_square[1]

        # Check if file disambiguation is sufficient
        files_in_conflict = {square[0] for square in ambiguous_squares}
        if from_file not in files_in_conflict:
            return from_file

        # Check if rank disambiguation is sufficient
        ranks_in_conflict = {square[1] for square in ambiguous_squares}
        if from_rank not in ranks_in_conflict:
            return from_rank

        # If both file and rank are needed, return both
        return from_square

    def algebraic_to_long(self, algebraic_notation: str) -> str:
        """Convert algebraic notation back to long notation"""
        # Handle castling
        if algebraic_notation in ['O-O', '0-0']:
            return 'e1g1' if self.board.turn == 'light' else 'e8g8'
        elif algebraic_notation in ['O-O-O', '0-0-0']:
            return 'e1c1' if self.board.turn == 'light' else 'e8c8'

        # Parse the algebraic notation
        notation = algebraic_notation.replace('+', '').replace('#', '')  # Remove check/mate indicators

        # Extract components
        is_capture = 'x' in notation
        if is_capture:
            parts = notation.split('x')
            piece_part = parts[0]
            destination = parts[1]
        else:
            # Find where the destination square starts (last 2 characters)
            destination = notation[-2:]
            piece_part = notation[:-2]

        # Determine piece type
        if not piece_part or piece_part[0].islower():
            # Pawn move
            piece_type = Pawn
        else:
            piece_symbol = piece_part[0].upper()
            piece_type = {
                'K': King, 'Q': Queen, 'R': Rook,
                'B': Bishop, 'N': Knight
            }[piece_symbol]

        # Find the source square
        source_square = self._find_source_square(piece_type, piece_part, destination, is_capture)

        return f"{source_square}{destination}"

    def _find_source_square(self, piece_type: type, piece_part: str, destination: str, is_capture: bool) -> str:
        """Find the source square for a piece given the algebraic notation"""
        candidates = []

        # Find all pieces of the correct type that can reach the destination
        for square_key, square in self.board.squares.items():
            piece = square.contains()
            if (piece and
                type(piece) == piece_type and
                piece.color == self.board.turn):

                # Check if this piece can legally reach the destination
                legal_moves = self.board.get_legal_moves(square_key)
                legal_captures = self.board.get_legal_captures(square_key)

                target_square = self.board.squares[destination]
                can_reach = target_square in legal_moves or target_square in legal_captures

                if can_reach:
                    candidates.append(square_key)

        if not candidates:
            raise ValueError(f"No {piece_type.__name__} can reach {destination}")

        if len(candidates) == 1:
            return candidates[0]

        # Use disambiguation info to narrow down
        disambiguation = piece_part[1:] if piece_part and piece_part[0].isupper() else piece_part

        for candidate in candidates:
            if disambiguation in candidate:
                return candidate

        raise ValueError(f"Cannot resolve ambiguous move: {piece_part} to {destination}")

    def create_move_from_long_notation(self, long_notation: str) -> Union[ChessMove, ChessCapture, ChessCastle]:
        """Create the appropriate ChessMove object from long algebraic notation"""
        # Clean and parse the input
        clean_notation = long_notation.replace(' ', '').lower()
        
        # Handle extended long notation (e.g., 'f4xg5')
        if 'x' in clean_notation:
            parts = clean_notation.split('x')
            if len(parts) == 2:
                from_square = parts[0]
                to_square = parts[1]
            else:
                raise ValueError(f"Invalid capture notation: {long_notation}")
        else:
            # Standard long notation (e.g., 'e2e4')
            if len(clean_notation) != 4:
                raise ValueError(f"Invalid long notation: {long_notation}. Expected format like 'e2e4'")
            from_square = clean_notation[:2]
            to_square = clean_notation[2:]

        # Validate squares exist
        if from_square not in self.board.squares or to_square not in self.board.squares:
            raise ValueError(f"Invalid squares in notation: {long_notation}")

        piece = self.board.get_piece(from_square)
        if piece is None:
            raise ValueError(f"No piece on square {from_square}")

        # Check for castling
        if isinstance(piece, King) and self._check_castling(from_square, to_square):
            return ChessCastle(self.board, from_square, to_square)

        # Check if this is a capture
        target_piece = self.board.get_piece(to_square)
        is_capture = target_piece is not None

        # Check for en passant (pawn capturing to empty square diagonally)
        if isinstance(piece, Pawn) and not is_capture:
            file_diff = abs(ord(from_square[0]) - ord(to_square[0]))
            if file_diff == 1:  # Diagonal move to empty square = en passant
                is_capture = True

        if is_capture:
            return ChessCapture(self.board, from_square, to_square)
        else:
            return ChessMove(self.board, from_square, to_square)

# # Extension to ChessMetaMove for algebraic notation support
# class ChessMetaMoveExtensions:
#     """Mixin or extension methods that could be added to ChessMetaMove"""
#     
#     @staticmethod
#     def from_long_notation(board: ChessBoard, long_notation: str) -> Union[ChessMove, ChessCapture, ChessCastle]:
#         """Factory method to create appropriate move from long notation"""
#         converter = ChessNotationConverter(board)
#         return converter.create_move_from_long_notation(long_notation)
#     
#     def to_algebraic_notation(self) -> str:
#         """Convert this move to algebraic notation"""
#         converter = ChessNotationConverter(self.board)
#         long_notation = f"{self.move_from['key']}{self.move_to['key']}"
#         return converter.long_to_algebraic(long_notation)

# Example usage and testing
def demo_enhanced_converter():
    """Demonstrate the enhanced notation converter"""
    board = ChessBoard()
    board.setup()
    converter = ChessNotationConverter(board)

    print("=== Long to Algebraic Conversion ===")
    test_moves = [
        'e2e4',      # Should become 'e4'
        'b1c3',      # Should become 'Nc3'
        'g1f3',      # Should become 'Nf3'
        'f1c4',      # Should become 'Bc4'
    ]
    
    for move in test_moves:
        try:
            algebraic = converter.long_to_algebraic(move)
            print(f"{move} -> {algebraic}")
            
            # Test round trip
            long_back = converter.algebraic_to_long(algebraic)
            print(f"  Round trip: {algebraic} -> {long_back}")
        except Exception as e:
            print(f"{move} -> Error: {e}")
    
    print("\n=== Extended Long Notation ===")
    # Set up a capture scenario
    board.clear()
    board.place_piece(Pawn('light'), 'f', 4)
    board.place_piece(Pawn('dark'), 'g', 5)
    board.turn = 'light'
    
    try:
        # Test extended notation: f4xg5
        algebraic = converter.long_to_algebraic('f4xg5')
        print(f"f4xg5 -> {algebraic}")
    except Exception as e:
        print(f"f4xg5 -> Error: {e}")
    
    print("\n=== Move Object Creation ===")
    board.setup()
    
    test_notations = ['e2e4', 'b1c3', 'e1g1']  # Move, capture, castle
    for notation in test_notations:
        try:
            move_obj = converter.create_move_from_long_notation(notation)
            print(f"{notation} -> {type(move_obj).__name__}")
        except Exception as e:
            print(f"{notation} -> Error: {e}")

    print("\n=== Move Validation Demo ===")
    test_notations = [ 'e2e4', 'b8c6', 'a2a3', 'b7b5' ]
    for notation in test_notations:
        print( board )
        print ( f'Attempting move {notation}.' )
        chess_move = CM.from_long_notation( board, notation )
        chess_move.validate()
        try:
            chess_move.execute()
        except ChessException as e:
            print( f'Chess move validation exception thrown: {e}' )
    print( f'Final board state:\n{board}' )
        

if __name__ == "__main__":
    demo_enhanced_converter()
