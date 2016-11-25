import random
import operator
import time


# The first thing to do is to build a class for game states
class GameState():
    """ Game state class """

    def __init__(self):

        # what move number it is
        self.moveNum = 1

        # whether White (W) or Black (B) is to move
        self.isToMove = 'W'

        self.data = [['k', 'q', 'b', 'n', 'r'], ['p', 'p', 'p', 'p', 'p'], ['.', '.', '.', '.', '.'],
                     ['.', '.', '.', '.', '.'], ['P', 'P', 'P', 'P', 'P'], ['R', 'N', 'B', 'Q', 'K']]

        # dictionary for values of the chess pieces
        self.evalW = {'k': 0, 'q': 0, 'b': 0, 'n': 0, 'r': 0, 'p': 0, '.': 0, 'P': 1, 'R': 5, 'N': 3, 'B': 3, 'Q': 9,
                      'K': 100}  # when white on the move
        self.evalB = {'k': 100, 'q': 9, 'b': 3, 'n': 3, 'r': 5, 'p': 1, '.': 0, 'P': 0, 'R': 0, 'N': 0, 'B': 0, 'Q': 0,
                      'K': 0}  # when black on the move
        self.wScore = 0  # white score
        self.bScore = 0  # black score
        # dictionary for mapping 2D array to alphabet i.e('a4' == column 'a' and row 2)
        self.mapColumn = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
        # does opposite of mapColumn
        self.NmapColumn = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'}
        # list of all the states
        self.stateList = []
        # a dictionary to assign a score to each move
        self.movesDict = {}
        # variable to store start time
        self.startTime = 0


    # methods to print the current board to a stream
    def print_current_board(self):
        strOut = str(self.moveNum) + ' ' + self.isToMove + '\n'
        for row in self.data:
            strOut += ''.join(row) + '\n'
        return strOut

    # methods to set the current board using a giving stream
    def set_board(self, strIn):

        lines = strIn.split('\n')
        data_lines = lines[1:7]  # i get an extra line that has '' so i choose to cut it
        self.data = [[char for char in row] for row in data_lines]
        fields = lines[0].split(' ')
        self.moveNum = int(fields[0])
        self.isToMove = fields[1]

    # return who wins the board at this state , from the lecture for now i only have to look who is missing the king
    def who_wins(self):

        W = False
        B = False
        for row in self.data:
            if 'K' in row:
                W = True
            if 'k' in row:
                B = True

        if W and B and self.moveNum > 40:
            return '='
        elif W and B:
            return '?'
        elif W:
            return 'W'
        elif B:
            return 'B'

    # return whether the provided argument is a piece from the side on move
    def isOwn(self, strPiece):
        if (self.isToMove == 'W' and strPiece.isupper()) or (self.isToMove == 'B' and strPiece.islower()):
            return True
        else:
            return False

    # return whether the provided argument is a piece from the side not on move
    def isEnemy(self, strPiece):
        if (self.isToMove == 'W' and strPiece.islower()) or (self.isToMove == 'B' and strPiece.isupper()):
            return True
        else:
            return False

    # return whether the provided argument is not a piece / is an empty field
    def isNothing(self, strPiece):
        if strPiece == '.':
            return True
        else:
            return False

    # return the the evaluation score of the side on move
    def eval(self):
        wTemp = 0
        bTemp = 0
        for row in self.data:
            for piece in row:
                wTemp += self.evalW[piece]
                bTemp += self.evalB[piece]
        self.wScore = wTemp
        self.bScore = bTemp
        if self.isToMove == 'W':

            return self.wScore - self.bScore
        else:
            return self.bScore - self.wScore

    # perform the supplied move
    def moveIt(self, strIn):

        # push this state to the list after you perform a move
        self.stateList.append(self.print_current_board())

        fro = strIn[0:2]
        to = strIn[3:5]

        if self.isToMove == 'W':
            if fro[1] == '5' and to[1] == '6' and self.data[6 - int(fro[1])][self.mapColumn[fro[0]]] == 'P':
                self.data[6 - int(to[1])][self.mapColumn[to[0]]] = 'Q'
            else:
                self.data[6 - int(to[1])][self.mapColumn[to[0]]] = self.data[6 - int(fro[1])][self.mapColumn[fro[0]]]

            self.data[6 - int(fro[1])][self.mapColumn[fro[0]]] = '.'
            self.isToMove = 'B'
        else:
            if fro[1] == '2' and to[1] == '1' and self.data[6 - int(fro[1])][self.mapColumn[fro[0]]] == 'p':
                self.data[6 - int(to[1])][self.mapColumn[to[0]]] = 'q'
            else:
                self.data[6 - int(to[1])][self.mapColumn[to[0]]] = self.data[6 - int(fro[1])][self.mapColumn[fro[0]]]

            self.data[6 - int(fro[1])][self.mapColumn[fro[0]]] = '.'
            self.isToMove = 'W'
            self.moveNum = self.moveNum + 1

    # with reference to the state of the game and return the possible moves
    def moveGen(self):
        moves = []
        if self.who_wins() == '?' and self.moveNum < 42:
            for y in range(6):
                for x in range(5):
                    if self.isOwn(self.data[y][x]):
                        moves += self.movelist(x, y)
        return moves

    # "scan" moves for a given piece by moving it in some direction until it must stop.
    def movescan(self, x0, y0, dx, dy, capture=True, stopShort=False):

        x = x0
        y = y0
        moves = []

        pieceToMove = self.data[y][x]

        # c = self.isToMove
        while True:

            x = x + dx
            y = y + dy

            # if x or y is not in bounds
            if not self.isValid(x, y):
                break
            # if there is a piece p at x, y
            if not self.isNothing(self.data[y][x]):
                if self.isOwn(self.data[y][x]):
                    break
                if not capture:
                    break
                stopShort = True
            elif capture == 'only':
                break

            valid_move = self.NmapColumn[x0] + str(6 - y0) + '-' + self.NmapColumn[x] + str(6 - y) + '\n'

            moves.append(valid_move)

            # condition to exit the do while loop
            if stopShort:
                break

        return moves

    # tries all four rotational symmetries of a given scan
    def symmscan(self, x, y, dx, dy, capture=True, stopShort=False):
        moves = []
        for i in range(4):
            moves += self.movescan(x, y, dx, dy, capture, stopShort)

            # exchange
            tmp = dx
            dx = dy
            dy = tmp
            # negate dy
            dy = -dy

        return moves

    # try all the directions for each given kind of piece.
    def movelist(self, x, y):
        p = self.data[y][x]
        moves = []

        if p in 'KkQq':
            stopShort = p in 'Kk'
            capture = True
            moves += self.symmscan(x, y, 0, -1, capture, stopShort)
            moves += self.symmscan(x, y, 1, -1, capture, stopShort)
            return moves
        elif p in 'BbRr':
            stopShort = p in 'Bb'
            capture = p in 'Rr'
            moves += self.symmscan(x, y, 0, -1, capture, stopShort)
            if p in 'Bb':
                stopShort = False
                capture = True
                moves += self.symmscan(x, y, 1, -1, capture, stopShort)
            return moves
        elif p in 'Nn':
            moves += self.symmscan(x, y, 1, -2, stopShort=True)
            moves += self.symmscan(x, y, -1, -2, stopShort=True)
            return moves
        elif p in 'Pp':
            direc = -1
            if p.islower():
                direc = 1
            moves += self.movescan(x, y, -1, direc, capture='only', stopShort=True)
            moves += self.movescan(x, y, 1, direc, capture='only', stopShort=True)
            moves += self.movescan(x, y, 0, direc, capture=False, stopShort=True)
            return moves
        else:
            return moves

    def isValid(self, intX, intY):
        if intX < 0:
            return False

        elif intX > 4:
            return False

        if intY < 0:
            return False

        elif intY > 5:
            return False

        return True

    # determine the possible moves and sort them in order of an increasing evaluation score
    def movesEvaluated(self):

        movesList = self.moveGen()

        self.movesDict = {}

        for move in movesList:
            self.moveIt(move)
            self.movesDict.update({move: chess_eval()})
            chess_undo()
        # now list sort using the scores (increasing order)
        sortedMovesDict = sorted(self.movesDict.items(), key=operator.itemgetter(1))

        # extract the sorted list of moves without the score
        sortedMoveslist = [i[0] for i in sortedMovesDict]
        # self.movesDict = movesDict
        return sortedMoveslist

    # undo the last move and update the state of the game
    def undo(self):
        if len(self.stateList) > 0:
            strIn = self.stateList.pop()
            self.set_board(strIn)

    # determine the possible moves and shuffle them before returning them
    def movesShuffled(self):
        moves = chess_moves()
        random.shuffle(moves)

        return moves

    # look at all the possible moves and return the move that has the highest score
    def moveGreedy(self):
        similarGreedyMoves = []  # in case of similar score moves
        greedyMoves = self.movesEvaluated()

        if len(greedyMoves) > 0:
            score = self.movesDict[greedyMoves[0]]
            for move in reversed(greedyMoves):
                if self.movesDict[move] == score:
                    similarGreedyMoves.append(move)
            random.shuffle(similarGreedyMoves)
            self.moveIt(similarGreedyMoves[0])
            return similarGreedyMoves[0]

        else:
            return ''

    # perform a random move and return it
    def moveRandom(self):

        randomMoves = self.movesShuffled()
        if len(randomMoves) > 0:
            m = randomMoves[0]
            # n=m[:5]
            self.moveIt(m)
            return m
        else:
            return ''

    # reset the board to the initial state
    def reset(self):
        self.__init__()


    def negamax(self, intDepth, intDuration):

        if self.who_wins() != '?' or intDepth <= 0:
            return self.eval()
        score = -5000
        for move in self.moveGen():
            self.moveIt(move)
            score = max(score, -self.negamax(intDepth - 1, intDuration))
            self.undo()

        return score

    def moveNegamax(self, intDepth, intDuration):
        best = ''
        score = -5000
        temp = 0
        for move in self.moveGen():
            self.moveIt(move)
            temp = -self.negamax(intDepth - 1, intDuration)
            self.undo()

            if (temp > score):
                best = move
                score = temp
        return best

    # alphabeta search
    def alphabeta(self, intDepth, alpha, beta, intDuration):
        if self.who_wins() != '?' or intDepth <= 0:
            return self.eval()
        score = -5000
        for move in self.movesEvaluated():
            self.moveIt(move)
            score = max(score, -self.alphabeta(intDepth - 1, -beta, -alpha, intDuration))
            self.undo()
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return score

    # perform an alphabeta move
    def moveAlphabeta(self, intDepth, intDuration):

        best = ''
        alpha = -5000
        beta = 5000
        temp = 0
        for move in self.movesEvaluated():
            self.moveIt(move)
            temp = -self.alphabeta(intDepth - 1, -beta, -alpha, intDuration)
            self.undo()
            if (temp > alpha):
                best = move
                alpha = temp
        return best



########################################################

# My global Board
MedBoard = GameState()


##########################################################

def chess_reset():
    # reset the state of the game / your internal variables - note that this function is highly dependent on your implementation

    MedBoard.reset()
    #MedBoard.set_board("18 B\nk..qr\n..p.p\n.....\nR.nP.\n.p.QP\n....K\n")


def chess_boardGet():
    # return the state of the game - one example is given below - note that the state has exactly 40 or 41 characters

    return MedBoard.print_current_board()


def chess_boardSet(strIn):
    # read the state of the game from the provided argument and set your internal variables accordingly - note that the state has exactly 40 or 41 characters

    MedBoard.set_board(strIn)


def chess_winner():
    # determine the winner of the current state of the game and return '?' or '=' or 'W' or 'B' - note that we are returning a character and not a string

    return MedBoard.who_wins()


def chess_isValid(intX, intY):
    return MedBoard.isValid(intX, intY)  # move this inside the class to reuse it


def chess_isEnemy(strPiece):
    # with reference to the state of the game, return whether the provided argument is a piece from the side not on move - note that we could but should not use the other is() functions in here but probably

    return MedBoard.isEnemy(strPiece)


def chess_isOwn(strPiece):
    # with reference to the state of the game, return whether the provided argument is a piece from the side on move - note that we could but should not use the other is() functions in here but probably
    return MedBoard.isOwn(strPiece)


def chess_isNothing(strPiece):
    # return whether the provided argument is not a piece / is an empty field - note that we could but should not use the other is() functions in here but probably

    return MedBoard.isNothing(strPiece)


def chess_eval():
    # with reference to the state of the game, return the the evaluation score of the side on move - note that positive means an advantage while negative means a disadvantage

    return MedBoard.eval()


def chess_moves():
    # with reference to the state of the game and return the possible moves - one example is given below - note that a move has exactly 6 characters

    return MedBoard.moveGen()


def chess_movesShuffled():
    # with reference to the state of the game, determine the possible moves and shuffle them before returning them- note that you can call the chess_moves() function in here

    return MedBoard.movesShuffled()


def chess_movesEvaluated():
    # with reference to the state of the game, determine the possible moves and sort them in order of an increasing evaluation score before returning them - note that you can call the chess_moves() function in here

    return MedBoard.movesEvaluated()


def chess_move(strIn):
    # perform the supplied move (for example 'a5-a4\n') and update the state of the game / your internal variables accordingly - note that it advised to do a sanity check of the supplied move

    MedBoard.moveIt(strIn)


def chess_moveRandom():
    # perform a random move and return it - one example output is given below - note that you can call the chess_movesShuffled() function as well as the chess_move() function in here

    return MedBoard.moveRandom()


def chess_moveGreedy():
    # perform a greedy move and return it - one example output is given below - note that you can call the chess_movesEvaluated() function as well as the chess_move() function in here

    return MedBoard.moveGreedy()


def chess_moveNegamax(intDepth, intDuration):
    # perform a negamax move and return it - one example output is given below - note that you can call the the other functions in here
    MedBoard.startTime = time.time()
    move = MedBoard.moveNegamax(intDepth, intDuration)
    if move != '':
        chess_move(move)
    return move


def chess_moveAlphabeta(intDepth, intDuration):
    # perform a alphabeta move and return it - one example output is given below - note that you can call the the other functions in here

    MedBoard.startTime = time.time()
    move = MedBoard.moveAlphabeta(intDepth, intDuration)
    if move != '':
        chess_move(move)
    return move


def chess_undo():
    # undo the last move and update the state of the game / your internal variables accordingly - note that you need to maintain an internal variable that keeps track of the previous history for this

    MedBoard.undo()
