#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import heapq
import math
import sys
import time
from Tkinter import *
from optparse import OptionParser

class State():

    def __init__(self, board, cost, parent, h, size):
        self._matrix = board
        self.cost = cost
        self.size = size
        self.heuristic = 0
        heur_arr = map(lambda heur: calcHeuristic(heur, self._matrix, self.size), h)
        for hval in heur_arr:
            self.heuristic += hval
        self.fval = self.cost + self.heuristic
        self.parent = parent
        self.hashvalue = hash(tuple(self._matrix))


    def __str__(self):
        ret = ""
        for var in range(len(self._matrix)):
            if var % self.size==0 and var != 0:
                ret += "\n"
            ret += " "
            ret += str(self._matrix[var])
            ret += " "
        return ret

    def get_matrix(self):
        return (self._matrix)

    def __hash__(self):
        return self.hashvalue

    def __eq__(self, other):
        return self._matrix == other

def solver(board, h):
    print "Puzzle is solving, wait a few seconds...", "\n"
    print "Number of heuristic use :", len(h)
    stateSelected = 0
    pq = []
    cost = {}
    visited = {}
    puzzleSize = int(math.sqrt(len(board)))
    success = False
    start = State(board, 0, None, h, puzzleSize)
    end = State(fBoard, 42, None, h, puzzleSize)
    heapq.heappush(pq,(start.fval,start))
    tmp_board = start
    while pq:
        stateSelected += 1
        tmp_tuple = heapq.heappop(pq)
        tmp_board = tmp_tuple[1]
        if tmp_board.heuristic == 0:
            end = tmp_board
            success = True
            break

        index = tmp_board._matrix.index(0)
        x = index / puzzleSize
        y = index % puzzleSize
        listOfMoves = checkMove(x,y,end.size)

        for move in listOfMoves:
            moveBoard = tmp_board._matrix[:]
            moveIndex = move[0] * puzzleSize + move[1]
            moveBoard[index], moveBoard[moveIndex] = moveBoard[moveIndex], moveBoard[index]
            newBoard = State(moveBoard, tmp_board.cost + 1, tmp_board, h, tmp_board.size)
            new_cost = newBoard.fval
            if newBoard not in visited or new_cost < cost[newBoard]:
                cost[newBoard] = new_cost
                visited[newBoard] = 1
                newBoard.parent = tmp_board
                heapq.heappush(pq,(newBoard.fval,newBoard))

    print "\n","Total number of states ever selected in the opened set :", stateSelected, "\n"
    print "Maximum number of states ever represented in memory at the same time during the search :", len(visited), "\n"

    if success == True:
        res = []
        var = end
        while var != start:
            res.append(var)
            var = var.parent
        res.append(var)
        # print len(res), "state to resolve"
        return list(reversed(res))
    else:
        return []

def checkMove(x, y, size):
    listOfMoves = [[x,y]]
    if(x + 1 < size):
        listOfMoves.append([x + 1, y])
    if(x - 1 >= 0):
        listOfMoves.append([x - 1, y])
    if(y - 1 >= 0):
        listOfMoves.append([x, y - 1])
    if(y + 1 < size):
        listOfMoves.append([x, y + 1])

    return listOfMoves

def h_manhattan(s, goal, size):
    tot = 0

    for element in s:
        i = goal.index(element)
        index = s.index(element)
        fBoard_x = i / size
        fBoard_y = i % size
        x = index / size
        y = index % size
        tot += math.fabs(x - fBoard_x)
        tot += math.fabs(y - fBoard_y)
    return tot

def h_linear_conflict(s, goal, size):

    heuristic = h_manhattan(s, goal, size)
    def linear_vertical_conflict():
        linearConflict = 0
        for row in range(size - 1):
            maxVal = -1
            for col in range(size - 1):
                cellValue = s[(size * col) + row]
                if cellValue != 0 and (cellValue - 1) / size == row:
                    if cellValue > maxVal:
                        maxVal = cellValue
                    else:
                        linearConflict += 2
        return linearConflict

    def linear_horizontal_conflict():
        linearConflict = 0
        for row in range(size - 1):
            maxVal = -1
            for col in range(size - 1):
                cellValue = s[(size * col) + row]
                if cellValue != 0 and cellValue % size == col + 1:
                    if cellValue > maxVal:
                        maxVal = cellValue
                    else:
                        linearConflict += 2
        return linearConflict

    heuristic += linear_vertical_conflict()
    heuristic += linear_horizontal_conflict()

    return heuristic


def h_hamming_distance(s,t, size):
    assert len(s) == len(t)
    return sum([ch1 != ch2 for ch1, ch2 in zip(s,t)])

def calcHeuristic(h, matrix, size):
    heuristic = h(matrix, fBoard, size)
    return heuristic

def create_goal(size):
    arr = []
    count = 0
    a = 0
    for i in range(size):
        line = []
        for j in range(size):
            line.append(0)
        arr.append(line)
    k = 1
    while k < size:
        i = a
        j = a
        while j < (size - k):
            count += 1
            arr[i][j] = count
            j += 1
        i = a
        j = size - k
        while i < (size - k):
            count += 1
            arr[i][j] = count
            i += 1
        i = size - k
        j = size - k
        while j >= a:
            count += 1
            arr[i][j] = count
            j -= 1
        i = size - (k + 1)
        j = a
        while i >= k:
            count += 1
            arr[i][j] = count
            i -= 1
        a += 1
        k += 1
    ret = []
    for line in arr:
        for num in line:
            if num == size * size:
                ret.append(0)
            else:
                ret.append(num)
    return ret

def parseFile(filename):
    if not os.path.isfile(filename):
        print "Puzzle must be a file"
        sys.exit()
    file = open(filename, 'r')
    content = file.readlines()
    content.pop(0)
    puzzleSize = content[0]
    content.pop(0)
    startState = [];
    for line in content:
        line = line.replace("\n", "").split('#')[0]
        arrayLine = ' '.join(line.split()).split(" ")
        for num in arrayLine:
            try:
                startState.append(int(num))
            except ValueError:
                print "Puzzle is not sovable or Wrong Format"
                sys.exit()
    return int(puzzleSize), startState

def init_UI(size, board, resolverList, speed):
    def getdiff(last, current):
        i = 0
        for val in last:
            if current[i] != val and val != 0:
                return last.index(val), current.index(val), val
            i += 1


    def startAnim():
        solveButton.config(state=DISABLED)
        def moveTiles(direction, el, stopAt):
            if direction == 0:
                pos = Canevas.coords(el)
                Canevas.coords(el, pos[0] - speed if pos[0] - speed >= stopAt else pos[0] - (pos[0] - stopAt), pos[1])
                if pos[0] > stopAt:
                    fenetre.after(1, moveTiles,0, el, stopAt)
            elif direction == 1:
                pos = Canevas.coords(el)
                Canevas.coords(el, pos[0] + speed if pos[0] + speed <= stopAt else pos[0] + (stopAt - pos[0]), pos[1])
                if pos[0] < stopAt:
                    fenetre.after(1, moveTiles,1, el, stopAt)
            elif direction == 2:
                pos = Canevas.coords(el)
                Canevas.coords(el, pos[0], pos[1] - speed if pos[1] - speed >= stopAt else pos[1] - (pos[1] - stopAt))
                if pos[1] > stopAt:
                    fenetre.after(1, moveTiles,2, el, stopAt)
            elif direction == 3:
                pos = Canevas.coords(el)
                Canevas.coords(el, pos[0], pos[1] + speed if pos[1] + speed <= stopAt else pos[1] + (stopAt - pos[1]))
                if pos[1] < stopAt:
                    fenetre.after(1, moveTiles,3, el, stopAt)



        global lastState
        currentState = resolverList.pop(0)
        try:
            lastState
        except NameError:
            lastState = currentState
            currentState = resolverList.pop(0)
            orig, dest, val = getdiff(lastState.get_matrix(), currentState.get_matrix())
            el = [item for item in frameArray if item[0] == val][0][1]
            if orig / size == dest / size:
                if orig == dest + 1:
                    moveTiles(0, el, Canevas.coords(el)[0] - win_size)
                elif orig == dest - 1:
                    moveTiles(1, el, Canevas.coords(el)[0] + win_size)
            elif orig % size == dest % size:
                if orig == dest + size:
                    moveTiles(2, el, Canevas.coords(el)[1] - win_size)
                elif orig == dest - size:
                    moveTiles(3, el, Canevas.coords(el)[1] + win_size)

        else:
            orig, dest, val = getdiff(lastState.get_matrix(), currentState.get_matrix())
            el = [item for item in frameArray if item[0] == val][0][1]
            if orig / size == dest / size:
                if orig == dest + 1:
                    moveTiles(0, el, Canevas.coords(el)[0] - win_size)
                elif orig == dest - 1:
                    moveTiles(1, el, Canevas.coords(el)[0] + win_size)
            elif orig % size == dest % size:
                if orig == dest + size:
                    moveTiles(2, el, Canevas.coords(el)[1] - win_size)
                elif orig == dest - size:
                    moveTiles(3, el, Canevas.coords(el)[1] + win_size)
        if len(resolverList) != 0:
            lastState = currentState
            fenetre.after(speed * (win_size / speed), startAnim)
            # fenetre.after(1000, startAnim)

    fenetre = Tk()

    fenetre.resizable(width=False, height=False)
    Canevas = Canvas(fenetre,width=700,height=700,bg ='white', bd=-4)


    win_size = 700 / size
    if speed > win_size / 3:
        speed = win_size / 3
    row = 0
    col = 0
    frameArray = []
    Canevas.create_rectangle(0, 0, 700, 700, fill="black")
    for var in range(len(board)):
        if var % size==0 and var != 0:
            col = 0
            row += 1
        if board[var] == 0:
            Canevas.create_rectangle(win_size * col + 5, win_size * row + 5,((win_size * col) + win_size) - 5, ((win_size * row) + win_size) - 5, fill="white")
            col += 1
        else:
            t = Label(Canevas, text=str(board[var]), bg="red", font=("Helvetica", 40), justify=CENTER, borderwidth=0)
            Canevas.create_rectangle(win_size * col + 5, win_size * row + 5,((win_size * col) + win_size) - 5, ((win_size * row) + win_size) - 5, fill="white")
            frameArray.append((board[var], Canevas.create_window(win_size * col + 5, win_size * row + 5, width=win_size - 10, height=win_size - 10, window=t, anchor='nw')))
            col += 1

    Canevas.pack()
    frame = Frame(fenetre, relief=RAISED, borderwidth=1)
    frame.pack(fill=BOTH, expand=True)
    closeButton = Button(fenetre, text="Close", command = fenetre.destroy)
    closeButton.pack(side=RIGHT)
    solveButton = Button(fenetre, text="Solve", command = startAnim)
    solveButton.pack(side=RIGHT)
    Canevas.focus_set()
    def close(event):
        fenetre.withdraw()
        sys.exit()
    Canevas.bind('<Escape>', close)
    fenetre.mainloop()

def inversions(puzzle):
    ret = 0
    for i in range(0, len(puzzle) - 1):
        if puzzle[i] == 0:
            continue
        for j in range(i + 1, len(puzzle)):
            if puzzle[j] == 0:
                continue
            ret += (puzzle[j] < puzzle[i])
    return ret

def check_if_solvable(puzzle, goal, size):
    puzzle_invert = inversions(puzzle)
    goal_invert = inversions(goal)

    if size % 2 == 0:
        puzzle_invert += puzzle.index(0) / size;
        goal_invert += goal.index(0) / size;
    return puzzle_invert % 2 == goal_invert % 2

def main():

    parser = OptionParser()
    parser.add_option("-f", "--file", help="Use file to import resolve puzzle");
    parser.add_option("-g", "--graph", help="Set to 1 to enable the UI");
    parser.add_option("-n", "--heuristic", help="Number of heuristic");
    (options, args) = parser.parse_args()
    if options.file == None:
        sys.exit()

    size, board = parseFile(options.file)

    global fBoard
    fBoard = create_goal(int(math.sqrt(len(board))))
    if not check_if_solvable(board, fBoard, size):
        print "Puzzle is not sovable or Wrong Format"
        sys.exit()
    if options.heuristic == None:
        sys.exit()
    elif options.heuristic == "1":
        resolverList = solver(board, [h_manhattan])
    elif options.heuristic == "2":
        resolverList = solver(board, [h_manhattan, h_linear_conflict])
    elif options.heuristic == "3":
        resolverList = solver(board, [h_manhattan, h_linear_conflict, h_hamming_distance])

    print "Number of moves required to transition from the initial state to the final state, according to the search :", len(resolverList), "\n"
    if options.graph == "1":
        init_UI(size, board, resolverList, 10000)
    else:
        for state in resolverList:
            print state, "\n"

if __name__ == "__main__":
    main()
