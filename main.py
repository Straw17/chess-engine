import chess

#Simplified Evaluation Function
pieceVals = {"P": 100,
             "N": 320,
             "B": 330,
             "R": 500,
             "Q": 900,
             "K": 20000}
pawnSquares = [[0, 0, 0, 0, 0, 0, 0, 0],
               [50, 50, 50, 50, 50, 50, 50, 50],
               [10, 10, 20, 30, 30, 20, 10, 10],
               [5, 5, 10, 25, 25, 10, 5, 5],
               [0, 0, 0, 20, 20, 0, 0, 0],
               [5, -5, -10, 0, 0, -10, -5, 5],
               [5, 10, 10, -20, -20, 10, 10, 5],
               [0, 0, 0, 0, 0, 0, 0, 0]]
knightSquares = [[-50, -40, -30, -30, -30, -30, -40, -50],
                 [-40, -20, 0, 0, 0, 0, -20, -40],
                 [-30, 0, 10, 15, 15, 10, 0, -30],
                 [-30, 5, 15, 20, 20, 15, 5, -30],
                 [-30, 0, 15, 20, 20, 15, 0, -30],
                 [-30, 5, 10, 15, 15, 10, 5, -30],
                 [-40, -20, 0, 5, 5, 0, -20, -40],
                 [-50, -40, -30, -30, -30, -30, -40, -50]]
bishopSquares = [[-20, -10, -10, -10, -10, -10, -10, -20],
                 [-10, 0, 0, 0, 0, 0, 0, -10],
                 [-10, 0, 5, 10, 10, 5, 0, -10],
                 [-10, 5, 5, 10, 10, 5, 5, -10],
                 [-10, 0, 10, 10, 10, 10, 0, -10],
                 [-10, 10, 10, 10, 10, 10, 10, -10],
                 [-10, 5, 0, 0, 0, 0, 5, -10],
                 [-20, -10, -10, -10, -10, -10, -10, -20]]
rookSquares = [[0, 0, 0, 0, 0, 0, 0, 0],
               [5, 10, 10, 10, 10, 10, 10, 5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [0, 0, 0, 5, 5, 0, 0, 0]]
queenSquares = [[-20, -10, -10, -5, -5, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 5, 5, 5, 5, 0, -10],
                [-5, 0, 5, 5, 5, 5, 0, -5],
                [0, 0, 5, 5, 5, 5, 0, -5],
                [-10, 5, 5, 5, 5, 5, 0, -10],
                [-10, 0, 5, 0, 0, 0, 0, -10],
                [-20, -10, -10, -5, -5, -10, -10, -20]]
kingSquares = [[-30, -40, -40, -50, -50, -40, -40, -30],
               [-30, -40, -40, -50, -50, -40, -40, -30],
               [-30, -40, -40, -50, -50, -40, -40, -30],
               [-30, -40, -40, -50, -50, -40, -40, -30],
               [-20, -30, -30, -40, -40, -30, -30, -20],
               [-10, -20, -20, -20, -20, -20, -20, -10],
               [20, 20, 0, 0, 0, 0, 20, 20],
               [20, 30, 10, 0, 0, 10, 30, 20]]
squareAccess = {"P": pawnSquares,
                "N": knightSquares,
                "B": bishopSquares,
                "R": rookSquares,
                "Q": queenSquares,
                "K": kingSquares}

def evalBoard(board):
    if board.is_check():
        checkBonus = 50
    else:
        checkBonus = 0
    
    board = str(board)
    board = board.replace("\n", " ")
    board = board.split(" ")
    whiteVal = 0
    for a in range(8):
        for b in range(8):
            piece = board[a*8 + b]
            if piece == ".":
                continue
            if piece.isupper():
                swap = 1
                aNew = a
            else:
                swap = -1
                aNew = 7-a
                piece = piece.upper()
            whiteVal += swap * (pieceVals[piece] + squareAccess[piece][aNew][b] + checkBonus)
    return whiteVal

def getNextMove(board, isWhite):
    moves = list(board.legal_moves)
    moveVals = []
    if isWhite:
        swap = 1
    else:
        swap = -1
    for move in moves:
        board.push_san(move.uci())
        moveVals.append(swap * evalBoard(board))
        board.pop()
    return moves[max(range(len(moveVals)), key=moveVals.__getitem__)].uci()

def getAIMove(board, AIWhite):
    board.push_san(getNextMove(board, AIWhite))
    return board

def getPlayerMove(board, AIWhite):
    print()
    print(board.unicode())
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
            board.push_san(input("Enter move: "))
            break
        except:
            continue
    return board

def isOver(board):
    outcome = board.outcome()
    if outcome == None:
        return False
    else:
        print()
        print(board.unicode())
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
        print(board.unicode())
        board = players["White"](board, True)
        if isOver(board):
            break
        
        print()
        print(board.unicode())
        board = players["Black"](board, False)
        if isOver(board):
            break

def runGame(AIWhite):
    board = chess.Board()
    if AIWhite:
        players = {"White": getAIMove,
                   "Black": getPlayerMove}
    else:
        players = {"White": getPlayerMove,
                   "Black": getAIMove}
    while True:
        board = players["White"](board, AIWhite)
        if isOver(board):
            break
        board = players["Black"](board, AIWhite)
        if isOver(board):
            break

runGame(False)
