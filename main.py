"""
This is our main driver file. It will be responsible for handling user input and displaying ta current gamestate object
"""
import pygame as p
from game import GameState, Move
from ai_search_move import findBestMove, findRandomMove

BOARD_WIDTH = BOARD_HEIGHT = 512  # 400 is another
MOVELOG_PANEL_WIDTH = 300
MOVELOG_PANEL_HEIGHT = BOARD_HEIGHT
BLOCK = 8  # dimensions of a chess board are 8x8
SQ_SIZE = BOARD_HEIGHT // BLOCK
MAX_FPS = 80  # for animations
IMAGES = {}
"""
Initialize a global dictionary of images. This will be called exacty once in the main
"""


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: we can acess an image by saying "IMAGES['wp']


"""
The main driver for our coe. This will hanlde user input and updating the graphics
"""


def drawWhenPressEsc(screen, gameStarted=False, gameMode='', depth=3):
    bgImage = p.transform.scale(p.image.load("images/chessboard.jpg"), (812, 520))
    font = p.font.SysFont("Arial", 24, True, False)
    screen.blit(bgImage, (0, 0))
    # screen.fill('black')
    if not gameStarted:
        sWrapper = p.Surface((512, 300))
        sWrapper.fill('grey')
        screen.blit(sWrapper, (150, 100))
        sWrapper = p.Surface((500, 290))
        sWrapper.fill('black')
        screen.blit(sWrapper, (156, 105))
        s = p.Surface((120, 80))
        if gameMode == '':
            textObj = font.render('Select Mode', True, 'green')
            col = (812 - textObj.get_width()) / 2
            screen.blit(textObj, (col, 136))

            s.fill('green')
            textObj = font.render('PvP Mode', True, 'white')
            s.blit(textObj, (20, 20))
            screen.blit(s, (256, 200))

            s.fill('green')
            textObj = font.render('PvAI Mode', True, 'white')
            s.blit(textObj, (20, 20))
            screen.blit(s, (436, 200))
        elif gameMode == '1p':
            textObj = font.render('Select AI Mode', True, 'white')
            col = (812 - textObj.get_width()) / 2
            screen.blit(textObj, (col, 136))

            s.fill('green')
            textObj = font.render('Easy', True, 'white')
            s.blit(textObj, (20, 20))
            screen.blit(s, (256, 200))

            s.fill('green')
            textObj = font.render('Hard', True, 'white')
            s.blit(textObj, (20, 20))
            screen.blit(s, (436, 200))

    else:
        if gameMode == '1p':
            mode = 'Hard mode' if depth == 3 else 'Easy mode'
            text = 'Current: AI ' + mode
            textObj = font.render(text, True, 'white')
            screen.blit(textObj, ((812 - textObj.get_width()) / 2, 12))
        elif gameMode == '2p':
            text = 'Current: PvP mode'
            textObj = font.render(text, True, 'white')
            screen.blit(textObj, ((812 - textObj.get_width()) / 2, 12))
        s = p.Surface((120, 80))
        s.fill('green')
        textObj = font.render('Restart', True, 'white')
        s.blit(textObj, (20, 20))
        screen.blit(s, (346, 200))


"""
Highlight square selected and moves for piece selected
"""


def highlightState(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # square selected that is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transperancy value -> 0 transparent: 255 opaque
            s.fill(p.Color('red'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('red'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def getPositionFromMoveString(lastMove):
    col = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    row = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    return row[lastMove[1]], col[lastMove[0]], row[lastMove[3]], col[lastMove[2]]


def highlightLastMove(screen, gs):
    if len(gs.moveLog) > 0:
        lastMove = gs.moveLog[-1]
        startRow, startCol, endRow, endCol = getPositionFromMoveString(lastMove.getMoveString())
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)  # transperancy value -> 0 transparent: 255 opaque
        s.fill(p.Color('yellow'))
        screen.blit(s, (startCol * SQ_SIZE, startRow * SQ_SIZE))
        screen.blit(s, (endCol * SQ_SIZE, endRow * SQ_SIZE))


"""
Draw the square on the board. The top left square is always light
"""


def drawBoard(screen):
    global colors
    colors = ['#769656', '#EEEED2']
    for r in range(BLOCK):
        for c in range(BLOCK):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board using the current GameState.board
"""


def drawPieces(screen, board):
    for r in range(BLOCK):
        for c in range(BLOCK):
            piece = board[r][c]
            if piece != '--':  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''draw move log'''


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVELOG_PANEL_WIDTH, MOVELOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)

    textObject = font.render('Move Log', True, p.Color('white'))
    screen.blit(textObject, (512+(300 - textObject.get_width()) / 2, 10))

    moveLog = gs.moveLog
    moveTexts = []  # modify this later
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + moveLog[i].getChessNotation() + " - "
        # moveString += "White:" + moveLog[i].getChessNotation() + " - "
        if i + 1 < len(moveLog):  # make sure black made a move
            # moveString += "Black:"
            moveString += moveLog[i + 1].getChessNotation() + "; "
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    textY = 30
    lineSpacing = 2
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


"""
Animation move
"""


def animationMove(move, screen, board, clock):
    global colors
    coords = []  # list of coords that the animation will movw through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        (r, c) = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnPassantMove:
                if move.pieceCaptured[0] == 'b':
                    enPassantRow = move.endRow + 1
                elif move.pieceCaptured[0] == 'w':
                    enPassantRow = move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        clock.tick(MAX_FPS)
        p.display.flip()


def drawText(screen, text):
    font = p.font.SysFont('Melvitca', 36, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Red'))
    screen.blit(textObject, textLocation.move(2, 2))


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)  # draw the squares on the board
    # add in piece hightlightning or move suggestion (later)
    highlightState(screen, gs, validMoves, sqSelected)
    highlightLastMove(screen, gs)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVELOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    moveLogFont = p.font.SysFont("Arial", 18, False, False)
    gs = GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable when a move is made
    animate = False  # flag variable when we should animate a move
    loadImages()
    running = True
    sqSelected = ()  # no square is selected, keep track of the last click of the user (tuple:= (row, col))
    playerClicks = []  # track of player clicks ( two tuples: [(6,4), (4,4)]
    gameOver = False
    playerOne = True  # If a Human is playing white, then this will be True. If an AI is playing then
    playerTwo = False  # Same as above but for black
    pressEscape = True
    gameStarted = False
    DEPTH = 3  # default game mode - Hard
    gameMode = ''
    while running:

        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if pressEscape:
                    location = p.mouse.get_pos()
                    row = location[1]
                    col = location[0]
                    print(row, col)
                    # start game: choose game mode
                    if not gameStarted:
                        # easy mode
                        if 200 <= row <= 280 and 256 <= col <= 376:
                            if gameMode == '1p':
                                gameStarted = True
                                DEPTH = 2
                                pressEscape = False
                            elif gameMode == '':
                                gameMode = '2p'
                                gameStarted = True
                                playerTwo = True
                                pressEscape = False
                        # hard mode
                        elif 200 <= row <= 280 and 436 <= col <= 556:
                            if gameMode == '1p':
                                gameStarted = True
                                DEPTH = 3
                                pressEscape = False
                            elif gameMode == '':
                                gameMode = '1p'
                                playerTwo = False
                    # when press Restart
                    else:

                        if 200 <= row <= 280 and 346 <= col <= 466:
                            gs = GameState()
                            validMoves = gs.getValidMoves()
                            sqSelected = ()
                            playerClicks = []
                            moveMade = False
                            animate = False
                            gameOver = False
                            gameStarted = False
                            gameMode = ''

                elif not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (
                            row, col) or col >= 8:  # the user clicked the same square twice or user clicked mouse log
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear the player clicks
                    else:
                        sqSelected = (row, col)
                        # phong TH click o trong
                        if (gs.board[row][col] != '--' or len(playerClicks) != 0):
                            playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    if len(playerClicks) == 2:  # after 2nd click

                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if gs.whiteToMove:
                                    print('White: ', end='')
                                else:
                                    print('Black: ', end='')
                                print(move.getChessNotation())
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset the clicks
                                playerClicks = []
                            if not moveMade:  # Click vao con khac cung mau thi thanh click thu nhat cua con khac luon
                                playerClicks = [sqSelected]

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when press 'z
                    # undo in AI mode:
                    if not playerTwo and humanTurn:
                        gs.undoMove()
                        gs.undoMove()
                        moveMade = True
                        animate = False
                        gameOver = False
                    # undo in pvp mode
                    elif playerTwo:
                        gs.undoMove()
                        moveMade = True
                        animate = False
                        gameOver = False
                if e.key == p.K_r:  # reset the board when 'r' is pressed
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                if e.key == p.K_ESCAPE and gameStarted:
                    pressEscape = not pressEscape

        # AI move finder
        if not gameOver and not humanTurn and gameStarted:
            AIMove = findBestMove(gs, validMoves, DEPTH)
            if AIMove is None:
                AIMove = findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animationMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()  # Di chuyen den o moi => thay doi
            moveMade = False
            animate = False
        if not pressEscape:
            drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)
        else:
            drawWhenPressEsc(screen, gameStarted, gameMode, DEPTH)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by Checkmate')
            else:
                drawText(screen, 'White wins by Checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()
