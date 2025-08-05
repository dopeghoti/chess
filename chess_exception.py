class ChessException( Exception ):
    """This is an abatract Exception meant to be instantiated by way of inheritors."""
    pass

class ChessMoveException( ChessException ):
    """This is an abatract Exception meant to be instantiated by way of inheritors."""
    pass

class ChessCaptureException( ChessException ):
    """This is an abatract Exception meant to be instantiated by way of inheritors."""
    pass

class ChessCastleException( ChessException ):
    """This is an abatract Exception meant to be instantiated by way of inheritors."""
    pass

class ChessCheckException( ChessException ):
    """This is an abatract Exception meant to be instantiated by way of inheritors."""
    pass

class ChessCannotMoveToOriginSquareException( ChessMoveException ):
    pass

class ChessCannotMoveFromEmptySquareException( ChessMoveException ):
    pass

class ChessCannotMoveOutOfTurnException( ChessMoveException ):
    pass

class ChessCannotMoveIntoCheckException( ChessCheckException ):
    pass

class ChessCannotMoveIntoOccupiedSquareException( ChessMoveException ):
    pass

class ChessCannotMoveOutsideMovementPatternException( ChessMoveException ):
    pass

class ChessCannotCaptureIntoEmptySquareException( ChessCaptureException ):
    pass

class ChessCannotCaptureFriendlyPieceException( ChessCaptureException ):
    pass

class ChessCannotCaptureNonPawnEnPassantException( ChessCaptureException ):
    pass

class ChessCannotCaptureEnPassantRemotelyException( ChessCaptureException ):
    """En passant captures can only occur in adjacent files"""
    pass

class ChessCannotCaptureEnPassantWhenNotVulnerableException( ChessCaptureException ):
    pass

class ChessCannotCaptureEnPassantWhenFinalSquareNotEmptyException( ChessCaptureException ):
    """I don't know how this might actually happen because a Pawn cannot move
    _through_ a piece, but the square the capturing Pawn would land on was
    not empty."""
    pass

class ChessCannotCaptureOutsideCapturePatternException( ChessCaptureException ):
    pass

class ChessCannotCastleWithNonKingException( ChessCastleException ):
    pass

class ChessCannotCastleIfKingHasMovedException( ChessCastleException ):
    pass

class ChessCannotCastleIfKingHasBeenInCheckException( ChessCastleException ):
    pass

class ChessCannotCastleOutOfCheckException( ChessCastleException ):
    pass

class ChessCannotCastleIntoInvalidDestinationException( ChessCastleException ):
    pass

class ChessCannotCastleFromInvalidOriginException( ChessCastleException ):
    pass

class ChessCannotCastleThroughOccupiedSquaresException( ChessCastleException ):
    pass

class ChessCannotCastleWithoutRookException( ChessCastleException ):
    pass

class ChessCannotCastleIfRookHasMovedException( ChessCastleException ):
    pass

class ChessCannotCastleIntoCheckException( ChessCheckException ):
    pass

