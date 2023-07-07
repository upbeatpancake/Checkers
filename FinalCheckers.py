from tkinter import *

class CheckersBoard:
    '''represents a board of Checkers: logic'''
    def __init__(self):
        '''CheckersBoard()
        creates a CheckersBoard in starting position
        a number represents the color and normal/king status of a piece
        0 red
        1 white
        2 red king
        3 white king
        None no piece
        '''
        
        self.turn = 0 # current turn
        self.board = {} # (x,y) : pieceValue
        self.endGame = False
        self.jumpInProgress = False
        self.jumpInterimCoords = None # interim position when jumping, set to None when no more jump
        self.pieceColors = ["red", "white"]
        self.winner = None # set to one of the pieceColors
        
        currentColor = 0
        # create opening positions
        for x in range(8):
            for y in range(8):
                coords = (x,y)
                if currentColor == 1 and y in [0,1,2]:
                    self.board[coords] = 0
                elif currentColor == 1 and y in [7, 6, 5]:
                    self.board[coords] = 1
                else:
                    self.board[coords] = None
                currentColor = 1 - currentColor
            currentColor = 1 - currentColor
        
    def is_jumpinprogress(self):
        return self.jumpInProgress
    
    def get_board(self):
        return self.board
        
    def get_piece(self, cords):
        return self.board[cords]
    
    def get_endgame(self):
        return self.endGame
    
    def get_turn(self):
        return self.turn
    
    def next_turn(self):
        self.turn = 1 - self.turn
        
    def get_diagonal_coords(self, coords, steps=1):
        '''CheckersBoard.get_diagnoal_coords(coords, steps) -> list
        - coords: (x,y) coordinate of the piece
        - steps: 1 or 2
        returns list of diagonal positions the piece can move to in the given number
        of steps, e.g. given a red piece at (3,2), steps 2, it returns [[(2,3), (1,4)], [(4,3), (5,4)]],
        if the steps is 1, it returns [[(2,3)], [(4,3)]]
        '''
        pieceValue = self.board[coords]
        
        x = coords[0]
        y = coords[1]
        
        deltaList = [[(1,1), (-1, 1)], [(1, -1), (-1, -1)], [(1,1), (-1, 1), (1, -1), (-1, -1)], [(1,1), (-1, 1), (1, -1), (-1, -1)]]
        
        returnList = []
        
        if pieceValue is None:
            return returnList
        
        for direcPair in deltaList[pieceValue]:
            dest = (x+direcPair[0]*steps, y+direcPair[1]*steps)
            if 0 <= dest[0] <= 7 and 0 <= dest[1] <= 7:
                returnList.append(dest)
                      
        return returnList  
        
    def possible_moves(self, coords):
        '''CheckersBoard.possible_moves(coords) -> list
        - coords: (x,y) coordinate of the piece
        returns a list of positions the piece at the given coordinates
        can move to or jump to; if it can jump, the 1-step move positions will not be returned.
        '''
        returnList = []
        ownPieceValue = self.board[coords]
        # if square is empty or not the right turn
        if ownPieceValue is None or ownPieceValue%2 != self.turn:
            return returnList
        
        # check jumps
        for possCoords in self.get_diagonal_coords(coords, 2):
            # get the coords of the piece being jumped over
            midSquare = ((possCoords[0]+coords[0])//2, (possCoords[1]+coords[1])//2)
            midValue = self.get_piece(midSquare)
            # if the destination is empty and the home and middle piece have opposite colors
            if self.board[possCoords] is None and midValue is not None and (midValue + self.get_piece(coords))%2 == 1:
                returnList.append(possCoords)
                
        # if it can jump
        if len(returnList) > 0: 
            # don't return 1-step move positions
            return returnList 
        
        # check 1-step move positions
        for possCoords in self.get_diagonal_coords(coords, 1):
            # if the destination is empty
            if self.get_piece(possCoords) is None: 
                returnList.append(possCoords)
                
        return returnList  
            
    def all_possible_moves(self):
        '''CheckersBoard.all_possible_moves() -> dict
        It returns a dictionary of (x,y) : list of positions the piece at
        (x,y) can move or jump to, where (x,y) is a piece with the color of
        the current player
        If any such piece can jump, only jumps are kept in the dict values;
        1-step moves are omitted
        '''
        # stores 1-step dests
        dictOne = {}
        # stores 2-step dests
        dictTwo = {}
        
        for coords in self.board:
            pieceValue = self.get_piece(coords)
            # if the square has piece of the current player
            if pieceValue is not None and pieceValue%2 == self.turn: 
                moves = self.possible_moves(coords)
                # if it's empty
                if len(moves) == 0:
                    # go to the next coordinates
                    continue
                steps = abs(coords[1] - moves[0][1])
                if steps == 1:
                    dictOne[coords] = moves
                # steps is 2
                else: 
                    dictTwo[coords] = moves
                    
        if len(dictTwo.keys()) > 0:
            # only return jump dests
            return dictTwo 
        return dictOne    
    
    def can_move(self, coords):
        '''CheckersBoard.can_move(coords) -> boolean
        returns true if the piece at the given coordinates can move or jump
        checks to make sure the piece is one of the current player's'''
        pieceValue = self.get_piece(coords)
        if pieceValue is not None and self.turn == pieceValue%2:
            if self.jumpInProgress and self.jumpInterimCoords != coords:
                return False
            # if piece can move or jump
            if coords in self.all_possible_moves().keys():
                len(self.all_possible_moves()[coords]) > 0
                return True
        return False
    
    def try_move(self, from_coords, to_coords):
        '''CheckersBoard.try_move(from_coords, to_coords) -> boolean
        - from_coords: starting position
        - to_coords: destination position
        returns True if the piece of the current player at from_coords
        is successfully moved to the coordinates specified by to_coords. This 
        function should update self.jumpInProgress, self.jumpInterimCoords, and
        self.turn accordingly. It also takes care of king promotion.
        '''
        fromValue = self.get_piece(from_coords)
        toValue = self.get_piece(to_coords)
        
        if self.jumpInProgress and from_coords != self.jumpInterimCoords:
            return False
        
        jumpAgain = False
        if to_coords in self.possible_moves(from_coords): # if it's a valid move
            # update the piece values
            self.board[from_coords] = None
            self.board[to_coords] = fromValue
            # if it's a jump
            if abs(from_coords[0] - to_coords[0]) != 1:
                midCoord = ((from_coords[0] + to_coords[0])//2, (from_coords[1] + to_coords[1])//2)
                self.board[midCoord] = None
                
                # can player jump again?
                for possNextJump in self.possible_moves(to_coords):
                    if abs(possNextJump[0] - to_coords[0]) != 1:
                        jumpAgain = True
                if jumpAgain:
                    self.jumpInProgress = True
                    self.jumpInterimCoords = to_coords
                else:
                    self.jumpInterimCoords = None
                    self.jumpInProgress = False
        
            kingPromotion = False
            # king promotion
            if (fromValue == 0 and to_coords[1] == 7) or (fromValue == 1 and to_coords[1] == 0):
                kingPromotion = True
                self.board[to_coords] = fromValue + 2
            
            if kingPromotion or not jumpAgain:
                self.next_turn()    
                
            return True
        return False
                
    def check_loss(self):
        '''CheckersBoard.check_loss() -> boolean
        returns true if the current player has nothing 
        to move. 
        self.winner is set to the other player.'''
        for i in range(2):
            if len(self.all_possible_moves()) == 0:
                self.endGame = True
                self.winner = self.pieceColors[1-self.turn]
                return True
            self.next_turn()

        return False
            
class CheckersSquare(Canvas):
    '''displays a square in the Checkers game'''
    
    def __init__(self, master, x, y, pieceValue=None, color=None):
        '''CheckersSquare()
        - pieceValue: 0 (red), 1(white), 2(red king), 3(white king), or None
        - color: background color. If it it None, set to 'blanched almond' if
        x+y is even, 'dark green' if x+y is odd.
        - creates a Checkers square at coordinates (x,y)'''
        
        self.colors = ["blanched almond", "dark green"]
        self.pieceColors = ["red", "white"]
        
        if color is None:
            self.color = self.colors[(x + y) % 2]
        else:
            self.color = color
        
        # create and place the widget
        Canvas.__init__(self, master, width=70, height=70, bg=self.color, \
          highlightbackground=self.color, highlightthickness=4)
        self.grid(row=y, column=x)
        
        # set the attributes
        self.coord = (x,y)
        self.pieceValue = pieceValue
        
        # bind click to selecting a square (to move the piece from OR to)
        self.bind('<Button-1>', master.mouse_click)
        # make the piece based on the piece value
        self.make_piece(pieceValue)

    def make_piece(self, pieceValue):
        '''CheckersSquare.make_piece(pieceValue) -> None
        Given the piece value (0, 1, 2 ,3 or None), create the piece.
        '''
        itemList = self.find_all()  
        for item in itemList:
            self.delete(item)
        
        if pieceValue is None:
            return
        
        index = pieceValue%2
        self.create_oval(10, 10, 65, 65, fill=self.pieceColors[index]) # add the piece
        if pieceValue == 2 or pieceValue == 3: # if it's a king
            self.create_text(37.4,45, text="*", font=('Arial', 25))
            
    def get_color(self):
        '''CheckersSquare.get_color() -> string
        returns background color of the square'''
        return self.color
    
    def get_pieceValue(self):
        '''CheckersSquare.get_pieceValue() -> int
        returns the piece value of the square if any
        '''
        return self.pieceValue
    
    def get_coord(self):
        '''CheckersSquare.get_coord() -> tuple
        returns (x,y) position of the square'''
        return self.coord
    
    def highlight(self):
        '''CheckersSquare.highlight() -> None
        
        Highlight the square with black border.
        '''
        self['highlightbackground'] = "black"
        
    def unhighlight(self):
        '''CheckersSquare.unhighlight() -> None
        
        Unhighlight the square.
        '''
        self['highlightbackground'] = self.color
        
class CheckersGame(Frame):
    '''represents a game of Checkers (UI)'''
    
    def __init__(self, master):
        '''CheckersGame(master)
        
        played with 8 rows and 8 columns'''
        Frame.__init__(self, master)
        self.grid()
        
        # attributes
        self.squares = {}
        
        # keep track of previously selected coordinates
        self.previous_coords = None

        # CheckersBoard
        self.board = CheckersBoard()
        
        self.counter = 0
        
        # set up squares and pieces
        for coord in self.board.get_board():
            pieceValue = self.board.get_piece(coord)
            square = CheckersSquare(self, coord[0], coord[1], pieceValue)
            self.squares[coord] = square
        
        # turn label
        self.turnLabel = Label(self, text='Turn:', font=('Arial bold', 18))
        self.turnLabel.grid(row=8, column=1)
        
        # piece that shows the current player's color
        self.turnSquare = CheckersSquare(self, 2, 8, pieceValue=0, color='gray')
        self.turnSquare.unbind('<Button-1>')
        
        # message label (for when a player wins)
        self.msgLabel = Label(self, text='', font=('Arial', 18))
        self.msgLabel.grid(row=8, column=5, columnspan=3)
        
        
    def update_display(self):
        '''CheckersGame.update_display() -> None
        Updates the display based on self.board,
        including the pieces, turnSquare and message label'''
        # pieces
        for coord in self.board.get_board():
            pieceValue = self.board.get_piece(coord)
            square = self.squares[coord]
            square.make_piece(pieceValue)
            
        # turn square
        self.turnSquare.make_piece(self.board.turn)
        
        # winner 
        if self.board.winner is not None: 
            self.msgLabel['text'] = self.board.winner.title() + " is the winner!"
            
        # double jump
        if self.board.jumpInProgress:
            self.msgLabel['text'] = "Must continue jump"
        elif self.board.endGame == False:
            self.msgLabel['text'] = ""
        
    def mouse_click(self, event):
        '''CheckersGame.mouse_click(event) -> None
        Mouse click handler.
        '''
        if self.board.endGame:
            return
        
        coords = event.widget.get_coord()
        
        # if it's the first click
        if self.previous_coords == None or (self.board.get_board()[self.previous_coords] != None \
            and self.board.get_board()[self.previous_coords]%2 == 1-self.board.turn):
            if self.board.can_move(coords):
                self.squares[coords].highlight()
                if self.previous_coords != None and self.previous_coords != coords:
                    self.squares[self.previous_coords].unhighlight()
                self.previous_coords = coords
        else: # it's the second click
            # unselecting a selected piece
            if coords == self.previous_coords: 
                if self.counter%2 == 0:
                    self.squares[coords].unhighlight()
                else:
                    self.squares[coords].highlight()
                self.counter +=1
                return
            # choosing a different starting piece
            if self.board.can_move(coords) and self.board.get_piece(coords)%2 == self.board.get_piece(self.previous_coords)%2: 
                self.squares[coords].highlight()
                self.squares[self.previous_coords].unhighlight()
                self.previous_coords = coords
                return
                
            if self.board.try_move(self.previous_coords, coords):
                self.squares[coords].highlight()
                self.squares[self.previous_coords].unhighlight()
                self.previous_coords = coords
                if self.board.jumpInProgress == False:
                    self.board.check_loss()
                self.update_display()  # update the display
        
def play_checkers():
    '''play_checkers()
    starts a new game of Checkers'''
    root = Tk()
    root.title('Checkers')
    cg = CheckersGame(root)
    cg.mainloop()

play_checkers()