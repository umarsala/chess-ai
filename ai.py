import random

pieceScores = {"K": 0,"Q": 9,"R": 5,"B": 3,"N": 3,"P": 1}

pieceSquareTables = {
    "gP": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 5, 5, 5, 5, 5, 5, 5],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0, 0, 0, -2, -2, 0, 0, 0],
        [1,-1,-2, 0, 0,-2,-1, 1],
        [1,2,2,-2,-2,2,2,1],
        [0, 0 ,0 ,0 ,0 ,0 ,0 ,0]
    ],

    "bP": None
}
pieceSquareTables["bP"] = pieceSquareTables["gP"][::-1]  # Reverse for black pawns

def evaluateBoard(game_state):

    # Checkmate / stalemate
    if game_state.checkMate():
        if game_state.whiteToMove:
            return -9999
        else:
            return 9999

    if game_state.staleMate():
        return 0

    score = 0

    for r in range(8):
        for c in range(8):
            piece = game_state.board[r][c]
            if piece != "--":

                value = pieceScores[piece[1]] * 100  # scale up

                # positional bonus for pawns
                if piece in pieceSquareTables:
                    value += pieceSquareTables[piece][r][c]

                if piece[0] == 'g':  #grey (human)
                    score += value
                else:  # blue AI)
                    score -= value

    # small bonus
    mobility = len(game_state.getValidMoves())
    if game_state.whiteToMove:
        score += mobility * 2
    else:
        score -= mobility * 2

    return score


def findBestMove(game_state, difficulty):

    validMoves = game_state.getValidMoves()
    random.shuffle(validMoves)

    if difficulty == "easy":
        return random.choice(validMoves)

    bestMove = None
    bestScore = -9999 if game_state.whiteToMove else 9999

    for move in validMoves:

        game_state.makeMove(move)
        score = evaluateBoard(game_state)

        # Encourage captures heavily
        if move.pieceCaptured != "--":
            score += pieceScores[move.pieceCaptured[1]] * 2

        game_state.undoMove()

        if game_state.whiteToMove:
            if score > bestScore:
                bestScore = score
                bestMove = move
        else:
            if score < bestScore:
                bestScore = score
                bestMove = move

    return bestMove


def minimax(game_state, depth, alpha, beta, maximizingPlayer):

    if depth == 0:
        return evaluateBoard(game_state)

    validMoves = game_state.getValidMoves()
    if len(validMoves) == 0:
        return evaluateBoard(game_state)

    if maximizingPlayer:
        maxEval = -9999
        for move in validMoves[:20]:
            game_state.makeMove(move, realMove=False)  # make move without affecting position history
            eval = minimax(game_state, depth - 1, alpha, beta, False)
            game_state.undoMove()
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval

    else:
        minEval = 9999
        for move in validMoves:
            game_state.makeMove(move, realMove=False)  # make move without affecting position history
            eval = minimax(game_state, depth - 1, alpha, beta, True)
            game_state.undoMove()
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval