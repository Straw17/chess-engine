#ideas: improve eval speed, passed pawns, null move pruning

import chess
import time
import sys
import random

pieceIDs = {"P": 0,
            "N": 1,
            "B": 2,
            "R": 3,
            "Q": 4,
            "K": 5}

def initZobrist(seed, bits):
    random.seed(seed)
    zobrist = [[[0]*64 for i in range(12)], [0, 0]]
    for piece in range(12):
        for square in range(64):
            zobrist[0][piece][square] = random.getrandbits(bits)
    for turn in range(2):
        zobrist[1][turn] = random.getrandbits(bits)
    return zobrist

zobrist = initZobrist(82737838281137781, 64)

def getZobHash(board):
    currentZob = 0
    for a in range(8):
        for b in range(8):
            piece = board.piece_at(a*8 + b)
            if piece is None:
                continue
            piece = piece.symbol()
            if piece.isupper():
                toAdd = 0
            else:
                toAdd = 6
            zobNext = zobrist[0][pieceIDs[piece.upper()] + toAdd][a*8 + b]
            currentZob = currentZob ^ zobNext
    if board.turn:
        currentZob = currentZob ^ zobrist[1][0]
    else:
        currentZob = currentZob ^ zobrist[1][1]
    return currentZob

#each hash has the following entries: [depth, score, toCut]
zobHashes = {}

def pruneZobHashes(zobHashes):
    for key in list(zobHashes.keys()):
        if zobHashes[key][2]:
            del zobHashes[key]
        else:
            zobHashes[key][2] = False
    return zobHashes

#PeSTO's Evaluation Function
pieceValsStart = {"P": 82,
                  "N": 337,
                  "B": 365,
                  "R": 477,
                  "Q": 1025,
                  "K": 0}
pieceValsEnd = {"P": 94,
                "N": 281,
                "B": 297,
                "R": 512,
                "Q": 936,
                "K": 0}

pawnStart = [
   0,   0,   0,   0,   0,   0,   0,   0,
  98, 134,  61,  95,  68, 126,  34, -11,
  -6,   7,  26,  31,  65,  56,  25, -20,
 -14,  13,   6,  21,  23,  12,  17, -23,
 -27,  -2,  -5,  12,  17,   6,  10, -25,
 -26,  -4,  -4, -10,   3,   3,  33, -12,
 -35,  -1, -20, -23, -15,  24,  38, -22,
   0,   0,   0,   0,   0,   0,   0,   0
]
pawnEnd = [
   0,   0,   0,   0,   0,   0,   0,   0,
 178, 173, 158, 134, 147, 132, 165, 187,
  94, 100,  85,  67,  56,  53,  82,  84,
  32,  24,  13,   5,  -2,   4,  17,  17,
  13,   9,  -3,  -7,  -7,  -8,   3,  -1,
   4,   7,  -6,   1,   0,  -5,  -1,  -8,
  13,   8,   8,  10,  13,   0,   2,  -7,
   0,   0,   0,   0,   0,   0,   0,   0
]
##pawnMate = [
##   0,   0,   0,   0,   0,   0,   0,   0,
## 600, 600, 600, 600, 600, 600, 600, 600,
## 500, 500, 500, 500, 500, 500, 500, 500,
## 400, 400, 400, 400, 400, 400, 400, 400,
## 300, 300, 300, 300, 300, 300, 300, 300,
## 200, 200, 200, 200, 200, 200, 200, 200,
## 100, 100, 100, 100, 100, 100, 100, 100,
##   0,   0,   0,   0,   0,   0,   0,   0
##]

knightStart = [
-167, -89, -34, -49,  61, -97, -15,-107,
 -73, -41,  72,  36,  23,  62,   7, -17,
 -47,  60,  37,  65,  84, 129,  73,  44,
  -9,  17,  19,  53,  37,  69,  18,  22,
 -13,   4,  16,  13,  28,  19,  21,  -8,
 -23,  -9,  12,  10,  19,  17,  25, -16,
 -29, -53, -12,  -3,  -1,  18, -14, -19,
-105, -21, -58, -33, -17, -28, -19, -23
]
knightEnd = [
 -58, -38, -13, -28, -31, -27, -63, -99,
 -25,  -8, -25,  -2,  -9, -25, -24, -52,
 -24, -20,  10,   9,  -1,  -9, -19, -41,
 -17,   3,  22,  22,  22,  11,   8, -18,
 -18,  -6,  16,  25,  16,  17,   4, -18,
 -23,  -3,  -1,  15,  10,  -3, -20, -22,
 -42, -20, -10,  -5,  -2, -20, -23, -44,
 -29, -51, -23, -15, -22, -18, -50, -64
]

bishopStart = [
 -29,   4, -82, -37, -25, -42,   7,  -8,
 -26,  16, -18, -13,  30,  59,  18, -47,
 -16,  37,  43,  40,  35,  50,  37,  -2,
  -4,   5,  19,  50,  37,  37,   7,  -2,
  -6,  13,  13,  26,  34,  12,  10,   4,
   0,  15,  15,  15,  14,  27,  18,  10,
   4,  15,  16,   0,   7,  21,  33,   1,
 -33,  -3, -14, -21, -13, -12, -39, -21
]
bishopEnd = [
 -14, -21, -11,  -8,  -7,  -9, -17, -24,
  -8,  -4,   7, -12,  -3, -13,  -4, -14,
   2,  -8,   0,  -1,  -2,   6,   0,   4,
  -3,   9,  12,   9,  14,  10,   3,   2,
  -6,   3,  13,  19,   7,  10,  -3,  -9,
 -12,  -3,   8,  10,  13,   3,  -7, -15,
 -14, -18,  -7,  -1,   4,  -9, -15, -27,
 -23,  -9, -23,  -5,  -9, -16,  -5, -17
]

rookStart = [
  32,  42,  32,  51,  63,   9,  31,  43,
  27,  32,  58,  62,  80,  67,  26,  44,
  -5,  19,  26,  36,  17,  45,  61,  16,
 -24, -11,   7,  26,  24,  35,  -8, -20,
 -36, -26, -12,  -1,   9,  -7,   6, -23,
 -45, -25, -16, -17,   3,   0,  -5, -33,
 -44, -16, -20,  -9,  -1,  11,  -6, -71,
 -19, -13,   1,  17,  16,   7, -37, -26
]
rookEnd = [
  13,  10,  18,  15,  12,  12,   8,   5,
  11,  13,  13,  11,  -3,   3,   8,   3,
   7,   7,   7,   5,   4,  -3,  -5,  -3,
   4,   3,  13,   1,   2,   1,  -1,   2,
   3,   5,   8,   4,  -5,  -6,  -8, -11,
  -4,   0,  -5,  -1,  -7, -12,  -8, -16,
  -6,  -6,   0,   2,  -9,  -9, -11,  -3,
  -9,   2,   3,  -1,  -5, -13,   4, -20
]

queenStart = [
 -28,   0,  29,  12,  59,  44,  43,  45,
 -24, -39,  -5,   1, -16,  57,  28,  54,
 -13, -17,   7,   8,  29,  56,  47,  57,
 -27, -27, -16, -16,  -1,  17,  -2,   1,
  -9, -26,  -9, -10,  -2,  -4,   3,  -3,
 -14,   2, -11,  -2,  -5,   2,  14,   5,
 -35,  -8,  11,   2,   8,  15,  -3,   1,
  -1, -18,  -9,  10, -15, -25, -31, -50
]
queenEnd = [
  -9,  22,  22,  27,  27,  19,  10,  20,
 -17,  20,  32,  41,  58,  25,  30,   0,
 -20,   6,   9,  49,  47,  35,  19,   9,
   3,  22,  24,  45,  57,  40,  57,  36,
 -18,  28,  19,  47,  31,  34,  39,  23,
 -16, -27,  15,   6,   9,  17,  10,   5,
 -22, -23, -30, -16, -16, -23, -36, -32,
 -33, -28, -22, -43,  -5, -32, -20, -41
]


kingStart = [
 -65,  23,  16, -15, -56, -34,   2,  13,
  29,  -1, -20,  -7,  -8,  -4, -38, -29,
  -9,  24,   2, -16, -20,   6,  22, -22,
 -17, -20, -12, -27, -30, -25, -14, -36,
 -49,  -1, -27, -39, -46, -44, -33, -51,
 -14, -14, -22, -46, -44, -30, -15, -27,
   1,   7,  -8, -64, -43, -16,   9,   8,
 -15,  36,  12, -54,   8, -28,  24,  14
]
kingEnd = [
 -74, -35, -18, -18, -11,  15,   4, -17,
 -12,  17,  14,  17,  17,  38,  23,  11,
  10,  17,  23,  15,  20,  45,  44,  13,
  -8,  22,  24,  27,  26,  33,  26,   3,
 -18,  -4,  21,  24,  27,  23,   9, -11,
 -19,  -3,  11,  21,  23,  16,   7,  -9,
 -27, -11,   4,  13,  14,   4,  -5, -17,
 -53, -34, -21, -11, -28, -14, -24, -43
]

squareStarts = {"P": pawnStart,
                "N": knightStart,
                "B": bishopStart,
                "R": rookStart,
                "Q": queenStart,
                "K": kingStart}
squareEnds = {"P": pawnEnd,
              "N": knightEnd,
              "B": bishopEnd,
              "R": rookEnd,
              "Q": queenEnd,
              "K": kingEnd}

def inEndPhase(board):
    whitePieces = 0
    blackPieces = 0
    for a in range(8):
        for b in range(8):
            piece = board.piece_at(a*8 + b)
            if piece is None:
                continue
            piece = piece.symbol()
            if piece.isupper():
                whitePieces += 1
            else:
                blackPieces += 1
    return (whitePieces < 5) or (blackPieces < 5)

def inMatePhase(board):
    whitePieces = 0
    blackPieces = 0
    for a in range(8):
        for b in range(8):
            piece = board.piece_at(a*8 + b)
            if piece is None:
                continue
            piece = piece.symbol()
            if piece.isupper():
                whitePieces += 1
            else:
                blackPieces += 1
    return (whitePieces < 3) or (blackPieces < 3)

evals = 0
def evalBoard(board, isWhite, isEnd, isMate, isWinning, depth):
    global evals
    evals += 1
    
    if board.is_check() and (isMate or isEnd):
        checkBonus = 30
    else:
        checkBonus = 0

    outcome = board.outcome()
    if outcome != None:
        if outcome.termination == chess.Termination.CHECKMATE:
            checkBonus = 10000 + 1000*depth
        else:
            if isWinning or not isMate:
                checkBonus = -5000
            else:
                checkBonus = 5000
    
    whiteVal = 0
    for a in range(8):
        for b in range(8):
            piece = board.piece_at(a*8 + b)
            if piece is None:
                continue
            piece = piece.symbol()
            if piece.isupper():
                swap = 1
                aNew = a
            else:
                swap = -1
                aNew = 7-a
                piece = piece.upper()
            if isMate:
                if piece == "P":
                    whiteVal += swap * (pieceValsEnd[piece] + pawnEnd[aNew*8 + b])
                else:
                    whiteVal += swap * (pieceValsEnd[piece])
            elif isEnd:
                whiteVal += swap * (pieceValsEnd[piece] + squareEnds[piece][aNew*8 + b])
            else:
                whiteVal += swap * (pieceValsStart[piece] + squareStarts[piece][aNew*8 + b])
                #print(piece + " " + str(pieceValsEnd[piece]) + " " + str(squareEnds[piece][aNew*8 + b]))
    if isWhite:
        whiteVal += checkBonus
    else:
        whiteVal -= checkBonus
    return whiteVal

def alphaBeta(depth, alpha, beta, board, isWhite, isEnd, isMate, isWinning, oldMoveUCI):
    if isWhite:
        swap = -1
    else:
        swap = 1

    hashVal = getZobHash(board)
    global zobHashes
    if (hashVal in zobHashes) and (zobHashes[hashVal][0] >= depth):
        if not zobHashes[hashVal][2]:
            zobHashes[hashVal][2] = True
        if zobHashes[hashVal][1] < beta:
            if zobHashes[hashVal][1] > alpha:
                return zobHashes[hashVal][1]
            else:
                return alpha
    
    if depth == 0:
        if board.is_check() or ("x" in oldMoveUCI):
            depth = 1
        else:
            toReturn = swap * evalBoard(board, isWhite, isEnd, isMate, isWinning, depth)
            zobHashes[hashVal] = [depth, toReturn, False]
            return toReturn
    if board.outcome() != None:
        toReturn = swap * evalBoard(board, isWhite, isEnd, isMate, isWinning, depth)
        zobHashes[hashVal] = [depth, toReturn, False]
        return toReturn

    moves = list(board.legal_moves)
    if depth > 1:
        moveVals = []
        for move in moves:
            board.push_san(move.uci())
            moveVals.append(swap * evalBoard(board, isWhite, isEnd, isMate, isWinning, depth))
            board.pop()
        moves = [x for _, x in sorted(zip(moveVals, moves), key=lambda pair: pair[0])]
        moves.reverse()

    moveCount = 0
    exact = False
    for move in moves:
        moveUCI = move.uci()
        board.push_san(moveUCI)
        if (moveCount > 3) and (depth > 2) and ("x" not in moveUCI) and (not board.is_check()):
            moveScore = -alphaBeta(depth-2, -beta, -alpha, board, not isWhite, isEnd, isMate, not isWinning, moveUCI)
            if moveScore <= alpha:
                board.pop()
                continue
        moveScore = -alphaBeta(depth-1, -beta, -alpha, board, not isWhite, isEnd, isMate, not isWinning, moveUCI)
        board.pop()
        if moveScore >= beta:
            return moveScore
        if moveScore > alpha:
            alpha = moveScore
            exact = True
        moveCount += 1

    if exact and depth > 0:
        zobHashes[hashVal] = [depth, alpha, False]
    
    return alpha

def getNextMove(board, isWhite):
    end = inEndPhase(board)
    mate = inMatePhase(board)

    if isWhite:
        swap = 1
    else:
        swap = -1
    boardNow = swap * evalBoard(board, isWhite, end, mate, False, 0)
    #print("Board: " + str(boardNow))
    
    moves = list(board.legal_moves)
    moveVals = []
    alpha = -30000
    beta = 30000
    for move in moves:
        moveUCI = move.uci()
        board.push_san(moveUCI)
        returnedVal = -alphaBeta(2, -beta, -alpha, board, isWhite, end, mate, boardNow > 0, moveUCI)
        moveVals.append(returnedVal)
        board.pop()
    #print([board.san(move) for move in moves])
    #print(moveVals)
    moves = [x for _, x in sorted(zip(moveVals, moves), key=lambda pair: pair[0])]
    moves.reverse()

    depth = 4
    moveVals = []
    for move in moves:
        moveUCI = move.uci()
        board.push_san(moveUCI)
        returnedVal = -alphaBeta(depth, -beta, -alpha, board, isWhite, end, mate, boardNow > 0, moveUCI)
        if returnedVal > alpha:
            alpha = returnedVal
        moveVals.append(returnedVal)
        board.pop()
    while evals < 20000:
        depth += 1
        moves = [x for _, x in sorted(zip(moveVals, moves), key=lambda pair: pair[0])]
        moveVals = []

        alpha = -30000
        beta = 30000
        for move in moves:
            moveUCI = move.uci()
            board.push_san(moveUCI)
            returnedVal = -alphaBeta(depth, -beta, -alpha, board, isWhite, end, mate, boardNow > 0, moveUCI)
            if returnedVal > alpha:
                alpha = returnedVal
            moveVals.append(returnedVal)
            board.pop()
    global zobHashes
    zobHashes = pruneZobHashes(zobHashes)
    print([board.san(move) for move in moves])
    print(moveVals)
    print("Depth: " + str(depth))
    return moves[max(range(len(moveVals)), key=moveVals.__getitem__)].uci()

total = 0
ply = 0
def getAIMove(board, AIWhite):
    global total, ply, evals
    evals = 0
    startTime = time.time()
    board.push_san(getNextMove(board, AIWhite))
    endTime = time.time()
    diff = endTime-startTime
    print("Evals: " + str(evals))
    print("Time: " + str(diff))
    total += diff
    ply += 1
    print("Running average: " + str(total/ply))
    print("FEN: " + board.fen())
    return board

def getPlayerMove(board, AIWhite):
    print()
    print(board)
    moves = [board.san(move) for move in list(board.legal_moves)]
    print("Moves: ", end="")
    lastPiece = ""
    for move in list(board.legal_moves):
        move = board.san(move)
        if lastPiece != evalPiece(move):
            lastPiece = evalPiece(move)
            print()
        print(move, end=" ")
    print()
    
    while True:
        try:
            move = input("Enter move: ")
            if move == "quit":
                sys.exit(1)
            board.push_san(move)
            break
        except Exception:
            continue
    return board

def isOver(board):
    outcome = board.outcome()
    if outcome == None:
        return False
    else:
        print()
        print(board)
        print("Game over!")
        print(str(outcome.termination).split(".")[1])
        return True

def evalPiece(uci):
    first = uci[0]
    if first.islower():
        return "P"
    else:
        return first

def runAIGame():
    board = chess.Board()
    players = {"White": getAIMove,
               "Black": getAIMove}
    while True:
        print()
        print(board)
        if board.turn is chess.WHITE:
            board = players["White"](board, True)
        elif board.turn is chess.BLACK:
            board = players["Black"](board, False)
        if isOver(board):
            break
    print(total/ply)
    return board.outcome().termination

def runGame(AIWhite):
    board = chess.Board()
    if AIWhite:
        players = {"White": getAIMove,
                   "Black": getPlayerMove}
    else:
        players = {"White": getPlayerMove,
                   "Black": getAIMove}
    while True:
        if board.turn is chess.WHITE:
            board = players["White"](board, AIWhite)
        elif board.turn is chess.BLACK:
            board = players["Black"](board, AIWhite)
        if isOver(board):
            break

#runGame(False)
runAIGame()
