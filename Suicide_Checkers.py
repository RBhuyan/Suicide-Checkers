#Author: Rohan Bhuyan
# The game is in a 6x6 matrix with B representing Black pieces, W representing White pieces, - representing empty spaces. The point of the game is to lose as many pieces as possible, this is done by
# making sure that if a move is possible, the player must take it. The game ends when either player loses all their pieces or one player runs out of moves. 

import random  #We use random to randomly choose a move from the decision tree if the heuristic returns multiple valid moves with the same heuristic score.
from copy import deepcopy  #We use deepcopy so we can make a copy of the game state and test further down the tree without actually affecting the current board.

DEPTH_LIMIT = 12
PLAYERS = ["Black", "White"]


class Game:
    def __init__(self, player=0):
        self.board = Board()
        # says the amount of pieces on the board for each side, the first one being for White and the second one being for Black
        self.remaining = [6, 6] #This initial state says that there are 6 pieces remaining out of a total of 6 pieces
        self.player = player
        self.turn = 0

    def run(self):  #function to run the game
        while not (self.gameOver(self.board)):
            self.board.drawBoardState()
            print("Current Player: " + PLAYERS[self.turn])
            if (self.turn == self.player):
                # decides the player's next move
                legal = self.board.calcLegalMoves(self.turn)
                if (len(legal) > 0):
                    move = self.getMove(legal)
                    self.makeMove(move)
                else:
                    print("No legal moves available, skipping turn")
            else:
                legal = self.board.calcLegalMoves(self.turn)
                print("AI:                  Valid Moves: ")
                for i in range(len(legal)):
                    print(str(i + 1) + ": ", end='')
                    print(str(legal[i].start) + " " + str(legal[i].end))
                if (len(legal) > 0):
                    
                    # If there's only one choice left we don't even have to use AI
                    if (len(legal) == 1):
                        choice = legal[0]
                    else:
                        state = AB_State(self.board, self.turn, self.turn)
                        choice = self.alpha_beta(state)

                    self.makeMove(choice)
                    print("Computer chooses (" + str(choice.start) + ", " + str(choice.end) + ")")
            # player to AI or AI to CPU
            self.turn = 1 - self.turn
        print("The game is over!")
        score = self.calcScore(self.board)
        if (score[0] > score[1]):
            print("White wins!")
        elif (score[1] > score[0]):
            print("Black wins!")
        else:
            print("It's a tie!")
        self.board.drawBoardState()

    def makeMove(self, move):

        self.board.boardMove(move, self.turn)
        if move.jump:
            # If there is a jump then represent that change in the array
            self.remaining[1 - self.turn] -= len(move.jumpOver)
            print("Removed " + str(len(move.jumpOver)) + " " + PLAYERS[1 - self.turn] + " pieces")

    def getMove(self, legal):
        move = -1
        # repeats until player picks move on the list
        while move not in range(len(legal)):
            # Lists the valid moves:
            print("Valid Moves: ")
            for i in range(len(legal)):
                print(str(i + 1) + ": ", end='')
                print(str(legal[i].start) + " " + str(legal[i].end))
            usr_input = input("Pick a move: ")
            # returns an error if the user does not input a valid move
            move = -1 if (usr_input == '') else (int(usr_input) - 1)
            if move not in range(len(legal)):
                print("Illegal move")
        print("Legal move")
        return (legal[move])

    # returns True if the game is over, false if otherwise
    def gameOver(self, board):
        # all pieces from one side captured
        if (len(board.currPos[0]) == 0 or len(board.currPos[1]) == 0):
            return True
        # stalemate because there are no moves for anyone to make
        elif (len(board.calcLegalMoves(0)) == 0 or len(board.calcLegalMoves(1)) == 0):
            return True
        else:
            # continue onwards
            return False

    # calculates the final score for the board
    def calcScore(self, board):
        score = [0, 0]
        # black pieces
        for cell in range(len(board.currPos[0])):
            # black pieces at end of board - 2 pts
            if (board.currPos[0][cell][0] == 0):
                score[0] += 1
            # black pieces not at end - 1 pt
            else:
                score[0] += 1
        # white pieces
        for cell in range(len(board.currPos[1])):
            # white pieces at end of board - 2 pts
            if (board.currPos[1][cell][0] == 5):
                score[1] += 1
            # white pieces not at end - 1 pt
            else:
                score[1] += 1
        return score

    # state = board, player
    def alpha_beta(self, state):
        result = self.max_value(state, -999, 999, 0)
        return result.move

    # returns max value and action associated with value
    def max_value(self, state, alpha, beta, node):
        # if terminalTest(state)
        actions = state.board.calcLegalMoves(state.player)
        # v <- -inf
        # self, move_value, move, max_depth, total_nodes, max_cutoff, min_cutoff
        v = AB_Value(-999, None, node, 1, 0, 0)
        # depth cutoff
        if (node == DEPTH_LIMIT):
            v.move_value = self.evaluation_function(state.board, state.origPlayer)
            #      print("Depth Cutoff. Eval value: "+str(v.move_value))
            return v
        if (len(actions) == 0):
            # return Utility(state)
            score = self.calcScore(state.board)
            if (score[state.origPlayer] > score[1 - state.origPlayer]):
                v.move_value = 100 + (2 * score[state.origPlayer] - score[1 - state.origPlayer])
            #         print("(max) Terminal Node Score: "+str(v.move_value))
            else:
                v.move_value = -100 + (2 * score[state.origPlayer] - score[1 - state.origPlayer])
            #         print("(max) Terminal Node Score: "+str(v.move_value))
            return v
        for a in actions:
            newState = AB_State(deepcopy(state.board), 1 - state.player, state.origPlayer)
            newState.board.boardMove(a, state.player)
            new_v = self.min_value(newState, alpha, beta, node + 1)
            if (new_v.max_depth > v.max_depth):
                v.max_depth = new_v.max_depth
            v.nodes += new_v.nodes
            v.max_cutoff += new_v.max_cutoff
            v.min_cutoff += new_v.min_cutoff
            if (new_v.move_value > v.move_value):
                v.move_value = new_v.move_value
                v.move = a
            if (v.move_value >= beta):
                v.max_cutoff += 1
                return v
            if (v.move_value > alpha):
                alpha = v.move_value
        return v

    # returns min value
    def min_value(self, state, alpha, beta, node):
        actions = state.board.calcLegalMoves(state.player)
        v = AB_Value(999, None, node, 1, 0, 0)
        if (node == DEPTH_LIMIT):
            v.move_value = self.evaluation_function(state.board, state.player)
            return v
        if (len(actions) == 0):
            score = self.calcScore(state.board)
            if (score[state.origPlayer] > score[1 - state.origPlayer]):
                v.move_value = 100 + (2 * score[state.origPlayer] - score[1 - state.origPlayer])
            
            else:
                v.move_value = -100 + (2 * score[state.origPlayer] - score[1 - state.origPlayer])
            
            return v
        for a in actions:
            newState = AB_State(deepcopy(state.board), 1 - state.player, state.origPlayer)
            newState.board.boardMove(a, state.player)
            new_v = self.max_value(newState, alpha, beta, node + 1)
            if (new_v.max_depth > v.max_depth):
                v.max_depth = new_v.max_depth
            v.nodes += new_v.nodes
            v.max_cutoff += new_v.max_cutoff
            v.min_cutoff += new_v.min_cutoff
            if (new_v.move_value < v.move_value):
                v.move_value = new_v.move_value
                v.move = a
            if (v.move_value <= alpha):
                v.min_cutoff += 1
                return v
            if (v.move_value < beta):
                beta = v.move_value
        return v

    # returns a utility value for a non-terminal node
    def evaluation_function(self, board, currPlayer):
        black_pieces = 0
        white_pieces = 0
        # black's pieces
        for cell in range(len(board.currPos[0])):
            white_pieces += 100

        # white's pieces
        for test_variable in range(len(board.currPos[1])):
            black_pieces += 100
        if (currPlayer != 0):
            return (white_pieces - black_pieces)
            
        else:
            return (black_pieces - white_pieces)
        



class AB_Value:
    def __init__(self, move_value, move, max_depth, child_nodes, max_cutoff, min_cutoff):
        self.move_value = move_value
        self.move = move
        self.max_depth = max_depth
        self.nodes = child_nodes
        self.max_cutoff = max_cutoff
        self.min_cutoff = min_cutoff



class AB_State:
    def __init__(self, boardState, currPlayer, originalPlayer):
        self.board = boardState
        self.player = currPlayer
        self.origPlayer = originalPlayer


class Move:
    def __init__(self, start, end, jump=False):
        self.start = start
        self.end = end  
        self.jump = jump  
        self.jumpOver = []  


class Board:  #The class for the board representation
    def __init__(self, board=[], currBlack=[], currWhite=[]):  #Initialization function
        if (board != []):
            self.boardState = board
        else:
            self.setDefaultBoard()
        self.currPos = [[], []]
        if (currBlack != []):
            self.currPos[0] = currBlack
        else:
            self.currPos[0] = self.calcPos(0)
        if (currWhite != []):
            self.currPos[1] = currWhite
        else:
            self.currPos[1] = self.calcPos(1)

    def boardMove(self, move_info, currPlayer):
        move = [move_info.start, move_info.end]
        jump = move_info.jump
        self.boardState[move[0][0]][move[0][1]] = -1
        self.boardState[move[1][0]][move[1][1]] = currPlayer
        if jump:
            # remove jumped over enemies
            for enemy in move_info.jumpOver:
                self.boardState[enemy[0]][enemy[1]] = -1
        # update currPos array
        # if its jump, the board could be in many configs, just recalc it
        if jump:
            self.currPos[0] = self.calcPos(0)
            self.currPos[1] = self.calcPos(1)
        # otherwise change is predictable, so faster to just set it
        else:
            self.currPos[currPlayer].remove((move[0][0], move[0][1]))
            self.currPos[currPlayer].append((move[1][0], move[1][1]))

    def calcLegalMoves(self, player):  # int array  -> [0] reg, [1] jump
        legalMoves = []
        hasJumps = False
        # next goes up if black or down if white
        next = -1 if player == 0 else 1
        boardLimit = 0 if player == 0 else 5
        
        for cell in self.currPos[player]:
            if (cell[0] == boardLimit):
                continue
            # diagonal right, only search if not at right edge of board
            if (cell[1] != 5):
                # empty, regular move
                if (self.boardState[cell[0] + next][cell[1] + 1] == -1 and not hasJumps):
                    temp = Move((cell[0], cell[1]), (cell[0] + next, cell[1] + 1))
                    legalMoves.append(temp)
                # has enemy, can jump it?
                elif (self.boardState[cell[0] + next][cell[1] + 1] == 1 - player):
                    jumps = self.checkJump((cell[0], cell[1]), False, player)
                    if (len(jumps) != 0):
                        # if first jump, clear out regular moves
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []
                        legalMoves.extend(jumps)
            # diagonal left, only search if not at left edge of board
            if (cell[1] != 0):
                if (self.boardState[cell[0] + next][cell[1] - 1] == -1 and not hasJumps):
                    temp = Move((cell[0], cell[1]), (cell[0] + next, cell[1] - 1))
                    legalMoves.append(temp)
                elif (self.boardState[cell[0] + next][cell[1] - 1] == 1 - player):
                    jumps = self.checkJump((cell[0], cell[1]), True, player)
                    if (len(jumps) != 0):
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []
                        legalMoves.extend(jumps)

        return legalMoves

    #Checks if there are any jumps to be made
    def checkJump(self, cell, isLeft, player):
        jumps = []
        next = -1 if player == 0 else 1
        # Since a piece cannot jump if the move would involve leaving the boundaries of the board, checks that condition
        if (cell[0] + next == 0 or cell[0] + next == 5):
            return jumps
        # Checks the top left of the piece
        if (isLeft):
            if (cell[1] > 1 and self.boardState[cell[0] + next + next][cell[1] - 2] == -1):
                temp = Move(cell, (cell[0] + next + next, cell[1] - 2), True)
                temp.jumpOver = [(cell[0] + next, cell[1] - 1)]
                if (temp.end[0] + next > 0 and temp.end[0] + next < 5):
                    # Checks if there is an enemy piece in the top left
                    if (temp.end[1] > 1 and self.boardState[temp.end[0] + next][temp.end[1] - 1] == (1 - player)):
                        test = self.checkJump(temp.end, True, player)
                        if (test != []):
                            dbl_temp = deepcopy(temp)  # Creates a deep copy to test if there are jumps to be made
                            dbl_temp.end = test[0].end
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)
                    # Does the same checking as before but now in the top right
                    if (temp.end[1] < 4 and self.boardState[temp.end[0] + next][temp.end[1] + 1] == (
                            1 - player)):
                        test = self.checkJump(temp.end, False, player)
                        if (test != []):
                            dbl_temp = deepcopy(temp)  # deepcopy needed?
                            dbl_temp.end = test[0].end
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)
                jumps.append(temp)
        else:
            # Checks the top right of the piece
            if (cell[1] < 4 and self.boardState[cell[0] + next + next][cell[1] + 2] == -1):
                temp = Move(cell, (cell[0] + next + next, cell[1] + 2), True)
                temp.jumpOver = [(cell[0] + next, cell[1] + 1)]
                if (temp.end[0] + next > 0 and temp.end[0] + next < 5):
                    # Checks if there is an enemy to the left of the jump we are considering
                    if (temp.end[1] > 1 and self.boardState[temp.end[0] + next][temp.end[1] - 1] == (1 - player)):
                        test = self.checkJump(temp.end, True, player)
                        if (test != []):
                            dbl_temp = deepcopy(temp)  # deepcopy needed?
                            dbl_temp.end = test[0].end
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)
                    # Does the same check as before but now to the right of the jump we are considering
                    if (temp.end[1] < 4 and self.boardState[temp.end[0] + next][temp.end[1] + 1] == (
                            1 - player)):
                        test = self.checkJump(temp.end, False, player)
                        if (test != []):
                            dbl_temp = deepcopy(temp)  # deepcopy needed?
                            dbl_temp.end = test[0].end
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)
                jumps.append(temp)
        return jumps

    def calcPos(self, player):
        pos = []
        for row in range(6):
            for col in range(6):
                if (self.boardState[row][col] == player):
                    pos.append((row, col))
        return pos

    def drawBoardState(self): #draws the board
        print("  ", end = '')
        for colnum in range(6):
            print(str(colnum) + " ", end="")
        print("")
        for row in range(6):
            print(str(row) + " ", end = '')
            for column in range(6):
                if (self.boardState[row][column] == -1):
                    print("- ", end='')
                elif (self.boardState[row][column] == 1):
                    print("W ", end='')
                elif (self.boardState[row][column] == 0):
                    print("B ", end='')
            print(' ')
            

    def setDefaultBoard(self):
        # 1 means the board cell has a white token, -1 means the board cell has a black token, 0 means the board cell is empty
        self.boardState = [

            [1, -1, 1, -1, 1, -1],
            [-1, 1, -1, 1, -1, 1],
            [-1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1],
            [0, -1, 0, -1, 0, -1],
            [-1, 0, -1, 0, -1, 0]

        ]


def main():
    print("Select player: ")
    print("Press 0 to play as Black (You go first)")
    print("Press 1 to play as White (You go second)")
    playr = int(input("Enter 0 or 1:"))
    while not (playr == 0 or playr == 1):
        playr = int(input("Invalid Choice, please try again: "))
    test = Game(playr)
    test.run()


main()
