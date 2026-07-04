# This file contains all the classes and functions for the core logic of the chess game.


class GameState():

    def __init__(self): 
        #8x8 Board representation
        #b/w = black/white, RNBQKP = piece type
        #"--" = no piece.
        
        self.board = [
        ["bR","bN","bB","bQ","bK","bB","bN","bR"],
        ["bP","bP","bP","bP","bP","bP","bP","bP"],
        ["--","--","--","--","--","--","--","--"],
        ["--","--","--","--","--","--","--","--"],
        ["--","--","--","--","--","--","--","--"],
        ["--","--","--","--","--","--","--","--"],
        ["gP","gP","gP","gP","gP","gP","gP","gP"],
        ["gR","gN","gB","gQ","gK","gB","gN","gR"]
        ]
        
        self.whiteToMove = True # White always starts (maybe change later)
        self.moveLog = []  # stores each move made in the game
        # castling rights
        self.gCastleKingside = True
        self.gCastleQueenside = True
        self.bCastleKingside = True
        self.bCastleQueenside = True

        # en passant square
        self.enPassantSquare = None

        self.fiftyMoveCounter = 0  # for fifty-move rule

        self.positionHistory = {}  # for threefold repetition

        initial = self.getBoardSignature()
        self.positionHistory[initial] = 1  # initial position occurs once

        self.capturedPieces = []
        self.checkCountGrey = 0
        self.checkCountBlue = 0

# make move 
    def makeMove(self, move, realMove=True):

        move.enPassantSquare = self.enPassantSquare  # store current en passant square in move object
        move.CastleRights = (self.gCastleKingside,self.gCastleQueenside,self.bCastleKingside,self.bCastleQueenside)
        
        move.fiftyMoveCounter = self.fiftyMoveCounter  # store current fifty-move counter in move object

        if move.pieceMoved[1] == 'P' or move.pieceCaptured != "--":
            if move.pieceCaptured != "--":
                self.capturedPieces.append(move.pieceCaptured)
            self.fiftyMoveCounter = 0  # reset counter
        else:
            self.fiftyMoveCounter = self.fiftyMoveCounter + 1  # increment counter


        self.board[move.startRow][move.startCol] = "--" # leaves the starting square empty when move is made

        # handle pawn promotion
        if move.isPromotion:
        # GUI will handle promotion choice later
            self.board[move.endRow][move.endCol] = move.pieceMoved
        else:
            self.board[move.endRow][move.endCol] = move.pieceMoved  # normal move

        # update castling rights
        if move.pieceMoved == 'gK':
            self.gCastleKingside = False
            self.gCastleQueenside = False
        elif move.pieceMoved == 'bK':
            self.bCastleKingside = False
            self.bCastleQueenside = False
        if move.pieceMoved == 'gR':
            if move.startCol == 0:  # left rook
                self.gCastleQueenside = False
            elif move.startCol == 7:  # right rook
                self.gCastleKingside = False
        if move.pieceMoved == 'bR':
            if move.startCol == 0:
                self.bCastleQueenside = False
            elif move.startCol == 7:
                self.bCastleKingside = False

        # handle castling move
        if move.isCastleMove:

            # kingside 
            if move.endCol == 6:
                self.board[move.endRow][5] = self.board[move.endRow][7]  # move rook
                self.board[move.endRow][7] = "--"  # empty rook square

            # queenside
            else:
                self.board[move.endRow][3] = self.board[move.endRow][0]  # move rook
                self.board[move.endRow][0] = "--"  # empty rook square

        # handle en passant move
        if move.isEnPassantMove:
            if move.pieceMoved[0] =='g':
                 self.board[move.endRow +1][move.endCol] = "--"  # capture black pawn
            else:
                 self.board[move.endRow -1][move.endCol] = "--"  # capture white pawn

        # update en passant square
        self.enPassantSquare = None # reset en passant square
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enPassantSquare = ((move.startRow + move.endRow)//2, move.startCol) # square behind pawn

        self.moveLog.append(move)  # log the move

        if realMove:
            board_fen = self.getBoardSignature()
            self.positionHistory[board_fen] = self.positionHistory.get(board_fen, 0) + 1
            move.boardSignature = board_fen
        self.whiteToMove = not self.whiteToMove
        if self.inCheck():
            if self.whiteToMove:
                self.checkCountGrey = self.checkCountGrey + 1
            else:
                self.checkCountBlue = self.checkCountBlue + 1
  
    # undo the last move 
    def undoMove(self):
        if len(self.moveLog) > 0:
            last = self.moveLog.pop()

            # swap turn back
            self.whiteToMove = not self.whiteToMove
            self.enPassantSquare = last.enPassantSquare  # restore en passant square

            (self.gCastleKingside, self.gCastleQueenside,
             self.bCastleKingside, self.bCastleQueenside) = last.CastleRights

            #Undo en passant
            if last.isEnPassantMove:
                # restore pawn that moved
                self.board[last.startRow][last.startCol] = last.pieceMoved
                self.board[last.endRow][last.endCol] = "--"  #target square becomes empty

                # restore the captured pawn
                if last.pieceMoved[0] == 'g':      # white pawn moved 
                    self.board[last.endRow + 1][last.endCol] = "bP"
                else:                              # black pawn moved 
                    self.board[last.endRow - 1][last.endCol] = "gP"
                return
            
            #Undo pawn promotion
            if last.pieceMoved[1] == 'P' and (last.endRow == 0 or last.endRow == 7):
                    # undo pawn promotion
                    self.board[last.endRow][last.endCol] = "--"  
                    self.board[last.startRow][last.startCol] = last.pieceMoved
                    return 
            # normal undo
            self.board[last.startRow][last.startCol] = last.pieceMoved
            self.board[last.endRow][last.endCol] = last.pieceCaptured

            #Undo castling
            if last.isCastleMove:
                if last.endCol == 6:  # kingside
                    self.board[last.endRow][7] = self.board[last.endRow][5]
                    self.board[last.endRow][5] = "--"
                else:  # queenside
                    self.board[last.endRow][0] = self.board[last.endRow][3]
                    self.board[last.endRow][3] = "--"

            # Undo fifty-move counter
            self.fiftyMoveCounter = last.fiftyMoveCounter

        if hasattr(last, 'boardSignature'):
            if last.boardSignature in self.positionHistory:
                self.positionHistory[last.boardSignature] -= 1
                if self.positionHistory[last.boardSignature] <= 0:
                    del self.positionHistory[last.boardSignature]
            
# for GUI later
    def applyPromotion(self, move, newPieceType):
        colour = move.pieceMoved[0] # 'g' or 'b'
        self.board[move.endRow][move.endCol] = colour + newPieceType

# find valid move
    # find valid move
    def getValidMoves(self):
        legalMoves = []
        
        for move in self.getAllPossibleMoves():
            self.makeMove(move)
            self.whiteToMove = not self.whiteToMove  # swap turn back to check for checks

            kingRow, kingCol = self.findKingPosition(self.whiteToMove)

            if not self.squareUnderAttack(kingRow, kingCol):
                legalMoves.append(move)
            self.whiteToMove = not self.whiteToMove  # swap turn back
            self.undoMove()

        return legalMoves

    def findKingPosition(self, white): # find the king's position on the board
        target = "gK" if white else "bK"
        for i in range(8):  # row
            for j in range(8):   # col
                if self.board[i][j] == target:
                    return (i, j)  # row and col
        return (-1, -1)  # just to avoid errors
    

    def squareUnderAttack(self, r, c): # check if square is under attack by opponent
        self.whiteToMove = not self.whiteToMove
        opponentMoves = self.getAllPossibleMoves(checkCastling=False) # get opponent moves
        self.whiteToMove = not self.whiteToMove 

        for m in opponentMoves:
            if m.endRow == r and m.endCol == c:
                return True
        return False
    

    def getAllPossibleMoves(self, checkCastling=True):  # get all possible moves without considering checks
        moves = []
        for i in range (8):  # row 
            for j in range (8):  # col
                piece = self.board[i][j]
                if piece == "--":
                        continue
                
                colour = piece[0] # g or b
                pieceType = piece[1] # P, R, N...

                # generate moves based on piece type
                if (colour == 'g' and self.whiteToMove) or (colour == 'b' and not self.whiteToMove):
                        if pieceType == 'P':
                            self.getPawnMoves(i, j, moves)
                        elif pieceType == 'R':
                            self.getRookMoves(i, j, moves)
                        elif pieceType == 'N':
                            self.getKnightMoves(i, j, moves)
                        elif pieceType == 'B':
                            self.getBishopMoves(i, j, moves)
                        elif pieceType == 'Q':
                            self.getQueenMoves(i, j, moves)
                        elif pieceType == 'K':
                            self.getKingMoves(i, j, moves, checkCastling)
        return moves
    

    def getPawnMoves(self, r, c, moves):
        piece = self.board[r][c]
        colour = piece[0]

        if colour == 'g':  # white pawn moves


            if self.enPassantSquare is not None:
                epR, epC = self.enPassantSquare
                if r == 3:
                    # capture left
                    if c - 1 == epC and epR == r - 1:
                        m = Move ((r,c), (r-1, c-1), self.board)
                        m.isEnPassantMove = True
                        moves.append(m)
                    
                    # capture right
                    if c + 1 == epC and epR == r - 1:
                        m = Move ((r,c), (r-1, c+1), self.board)
                        m.isEnPassantMove = True
                        moves.append(m)
                    
                

            # move one square forward
            if r - 1 >= 0 and self.board[r-1][c] == "--":
                moves.append(Move((r,c), (r-1,c), self.board))


                # move two squares forward 
                if r == 6 and self.board[r-2][c] == "--":   
                    moves.append(Move((r,c), (r-2,c), self.board))

            if r - 1 >= 0 and c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':  # capture to the left
                    moves.append(Move((r,c), (r-1,c-1), self.board))

            if r - 1 >= 0 and c + 1 < 8:
                if self.board[r-1][c+1][0] == 'b':  # capture to the right
                    moves.append(Move((r,c), (r-1,c+1), self.board))

        else: # black pawn moves

            if self.enPassantSquare is not None:
                epR, epC = self.enPassantSquare
                if r == 4:
                    # capture left
                    if c - 1 == epC and epR == r + 1:
                        m = Move ((r,c), (r+1, c-1), self.board)
                        m.isEnPassantMove = True
                        moves.append(m)
                    
                    # capture right
                    if c + 1 == epC and epR == r + 1:
                        m = Move ((r,c), (r+1, c+1), self.board)
                        m.isEnPassantMove = True
                        moves.append(m)

            # move one square forward
            if r + 1 < 8 and self.board[r+1][c] == "--":
                moves.append(Move((r,c), (r+1,c), self.board))

                # move two squares forward
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c), (r+2,c), self.board))
            
            if r + 1 < 8 and c - 1 >= 0:
                if self.board[r+1][c-1][0] == 'g':  # capture to the left
                    moves.append(Move((r,c), (r+1,c-1), self.board))
            
            if r + 1 < 8 and c + 1 < 8:
                if self.board[r+1][c+1][0] == 'g':  # capture to the right
                    moves.append(Move((r,c), (r+1,c+1), self.board))
    

    def getKnightMoves(self,r,c, moves):
        colour = self.board[r][c][0]

        # all 8 possible knight moves
        jumps = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]

        for step in jumps :
            endR = r + step[0]
            endC = c + step[1]

            # check if move is on board
            if 0 <= endR < 8 and 0 <= endC < 8:
                endPiece = self.board[endR][endC]
                if endPiece == "--" or endPiece[0] != colour: # move if empty square or capturing opponent piece
                    moves.append(Move((r,c), (endR,endC), self.board))


    def getBishopMoves(self, r,c, moves):
        colour = self.board[r][c][0]
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]  # 4 diagonal directions

        for d in directions:
            for i in range(1, 8):  # bishop can move up to 7 squares
                endR = r + d[0] * i
                endC = c + d[1] * i

                if 0 <= endR < 8 and 0 <= endC < 8:  # still on board
                    endPiece = self.board[endR][endC]

                    if endPiece == "--":  # if empty square then move
                        moves.append(Move((r, c), (endR, endC), self.board))

                    elif endPiece[0] != colour:  # if enemy piece then capture
                        moves.append(Move((r, c), (endR, endC), self.board))
                        break

                    else:  
                        break
                else:
                    break


    def getRookMoves(self, r, c,moves):
        colour = self.board[r][c][0]
        directions = [(-1,0), (1,0), (0,-1), (0,1)]  # up, down, left, right

        for d in directions:
            step = 1
            while True:  # rook can move up to 7 squares
                endR = r + d[0] * step
                endC = c + d[1] * step

                if 0 <= endR < 8 and 0 <= endC < 8:  # if still on board
                    endPiece = self.board[endR][endC]

                    if endPiece == "--":  # if empty square then move
                        moves.append(Move((r, c), (endR, endC), self.board))

                    elif endPiece[0] != colour:  # if enemy piece then capture
                        moves.append(Move((r, c), (endR, endC), self.board))
                        break

                    else:  
                        break
                else:
                    break
                step = step + 1


    def getQueenMoves(self, r, c, moves): # queen is a combination of rook and bishop so call both functions
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)


    def getKingMoves(self, r, c, moves, checkCastling=True):
        colour = self.board[r][c][0]
        kingSteps = [ (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1) ]

        for step in kingSteps:
            endR = r + step[0]
            endC = c + step[1]

            if 0 <= endR < 8 and 0 <= endC < 8:  # if still on board
                endPiece = self.board[endR][endC]
                if endPiece == "--" or endPiece[0] != colour: # move if empty square or capturing opponent piece
                    moves.append(Move((r,c), (endR,endC), self.board))

        # CASTLING MOVES
        if checkCastling:
            if colour == 'g' and r == 7 and c == 4:  # white king at starting position
                self.getCastleMovesWhite(r, c, moves)
            elif colour == 'b' and r == 0 and c == 4:  # black king at starting position
                self.getCastleMovesBlack(r, c, moves)


    def getCastleMovesWhite(self, r, c, moves):

        # white castling moves
        if self.gCastleKingside:  
            sq1 = self.board[7][5] # f1
            sq2 = self.board[7][6] # g1

            # kingside castle
            if sq1 == "--" and sq2 == "--":
                # king cannot be in check or pass through attacked squares
                if not self.squareUnderAttack(7,4):
                    if not self.squareUnderAttack(7,5):
                        if not self.squareUnderAttack(7,6):
                            moves.append(Move((7,4), (7,6), self.board))
        # queenside castle
        if self.gCastleQueenside:
            sqA = self.board[7][1] #b1
            sqB = self.board[7][2] # c1
            sqC = self.board[7][3] #d1

            if sqA == "--" and sqB == "--" and sqC == "--":
                if not self.squareUnderAttack(7,4):     # e1
                    if not self.squareUnderAttack(7,3):    # d1
                        if not self.squareUnderAttack(7,2):    # c1
                            moves.append(Move((7,4), (7,2), self.board))


    def getCastleMovesBlack(self, r, c, moves):

        # black castling moves
        if self.bCastleKingside:  
            sq1 = self.board[0][5] # f8
            sq2 = self.board[0][6] # g8

            # kingside castle
            if sq1 == "--" and sq2 == "--":
                # king cannot be in check or pass through attacked squares
                if not self.squareUnderAttack(0,4):
                    if not self.squareUnderAttack(0,5):
                        if not self.squareUnderAttack(0,6):
                            moves.append(Move((0,4), (0,6), self.board))
        # queenside castle
        if self.bCastleQueenside:
            sqA = self.board[0][1] #b8
            sqB = self.board[0][2] # c8
            sqC = self.board[0][3] #d8

            if sqA == "--" and sqB == "--" and sqC == "--":
                if not self.squareUnderAttack(0,4):     # e8
                    if not self.squareUnderAttack(0,3):    # d8
                        if not self.squareUnderAttack(0,2):    # c8
                            moves.append(Move((0,4), (0,2), self.board))


    def inCheck(self):
        kingR, kingC = self.findKingPosition(self.whiteToMove)
        return self.squareUnderAttack(kingR, kingC)
    

    def checkMate(self):
        return self.inCheck() and len(self.getValidMoves()) == 0
    

    def staleMate(self):
        return not self.inCheck() and len(self.getValidMoves()) == 0


    def fiftyMoveRuleReached(self):
        return self.fiftyMoveCounter >= 100  # 50 full moves = 100 half-moves


    def getBoardSignature(self):
        rows = []
        for r in self.board:
            rows.append(",".join(r))

        boardString = "/".join(rows)
        turn = "g" if self.whiteToMove else "b"   
        return boardString + " " + turn
    
    
    def threefoldRepetition(self):
        board_signature = self.getBoardSignature()
        return self.positionHistory.get(board_signature, 0) >= 3
    


class Move():
    # stores info about a move on the chessboard (might add more later e,g. promotion)
    def __init__(self, startSq, endSq, board):
        # startling/ending squares
        self.startPos = startSq
        self.endPos = endSq
        self.startRow = startSq[0]  # row
        self.startCol = startSq[1]  #col
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        
        #what piece is moved or on target square
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # castling flag
        self.isCastleMove = False
        if self.pieceMoved[1] == 'K' and abs(self.startCol - self.endCol) == 2:
            self.isCastleMove = True

        # en passant flag
        self.isEnPassantMove = False
        self.enPassantSquare = None

        #promotion flag
        self.isPromotion = False
        if self.pieceMoved[1] == 'P' and (self.endRow == 0 or self.endRow == 7):
            self.isPromotion = True

        self.CastleRights = None 
        self.promotionChoice = "Q"

        self.fiftyMoveCounter = None  # to be set when move is made


    def __eq__(self, other):
        if isinstance(other, Move):
            return (self.startRow == other.startRow and self.startCol == other.startCol and
                    self.endRow == other.endRow and self.endCol == other.endCol)
        return False
    
    def __str__(self):
        return self.getChessNotation()
    
    def getChessNotation(self):
        cols_to_files = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
        rows_to_ranks = {7: '1', 6: '2', 5: '3', 4: '4', 3: '5', 2: '6', 1: '7', 0: '8'}

        start = cols_to_files[self.startCol] + rows_to_ranks[self.startRow]
        end = cols_to_files[self.endCol] + rows_to_ranks[self.endRow]
        return start + end