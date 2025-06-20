from Game2048 import *
import math
import copy

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0
        self._depthCount = 0
        self._count = 0

    def findMove(self, state):
        self._count += 1
        actions = self.moveOrder(state)
        depth = 1
        while self.timeRemaining():
            self._depthCount += 1
            self._parentCount += 1
            self._nodeCount += 1
            print('Search depth', depth)
            best = -math.inf
            bestMove = None

            for a in actions:
                result = state.move(a)
                if not self.timeRemaining(): return
                v = self.expectiPlayer(result, depth - 1)
                if v is None: return
                if v > best:
                    best = v
                    bestMove = a

            if bestMove is not None:
                self.setMove(bestMove)
                print('\tBest value', best, bestMove)

            depth += 1

    def maxPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1
        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)
        self._parentCount += 1
        best = -math.inf
        for a in self.moveOrder(state):
            if not self.timeRemaining(): return None
            result = state.move(a)
            v = self.expectiPlayer(result, depth - 1)
            if v is None: return None
            best = max(best, v)
        return best

    def expectiPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1
        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)
        self._parentCount += 1
        expected_value = 0
        tiles = state.possibleTiles()
        for (index, value) in tiles:
            prob = 0.9 if value == 1 else 0.1
            result = state.addTile(index, value)
            v = self.maxPlayer(result, depth - 1)
            if v is None: return None
            expected_value += prob * v
        return expected_value

    def heuristic(self, state):
        board = state._board
        size = 4
        grid = [[board[4 * i + j] for j in range(size)] for i in range(size)]

        empty_tiles = sum(1 for val in board if val == 0)
        max_tile = max(board)
        corner_score = 0
        monotonicity = 0
        smoothness = 0

        corners = [grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1]]
        if max_tile in corners:
            corner_score += (2 ** max_tile) * 1.5

        empty_score = empty_tiles * 100

        for row in grid:
            for i in range(size - 1):
                if row[i] >= row[i + 1]:
                    monotonicity += 1

        for col in range(size):
            for i in range(size - 1):
                if grid[i][col] >= grid[i + 1][col]:
                    monotonicity += 1

        monotonicity_score = monotonicity * 10

        for i in range(size):
            for j in range(size - 1):
                smoothness -= abs((2 ** grid[i][j] if grid[i][j] else 0) - (2 ** grid[i][j + 1] if grid[i][j + 1] else 0))
                smoothness -= abs((2 ** grid[j][i] if grid[j][i] else 0) - (2 ** grid[j + 1][i] if grid[j + 1][i] else 0))

        return (
            state.getScore()
            + empty_score
            + corner_score
            + monotonicity_score
            + smoothness * 0.1
        )

    def moveOrder(self, state):
        return state.actions()

    def stats(self):
        print(f'Average depth: {self._depthCount/self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
