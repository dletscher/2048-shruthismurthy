from Game2048 import *
import math
import random

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0
        self._depthCount = 0
        self._count = 0
        self.fixedDepth = 3

    def findMove(self, state):
        self._count += 1
        actions = self.moveOrder(state)
        depth = self.fixedDepth
        self._depthCount += 1
        self._parentCount += 1
        self._nodeCount += 1
        print('Search depth', depth)
        best = -math.inf
        bestMove = None

        for a in actions:
            result = state.move(a)
            if not self.timeRemaining():
                break
            v = self.expectiPlayer(result, depth - 1)
            if v is None:
                break
            if v > best:
                best = v
                bestMove = a

        if bestMove is None:
            bestMove = random.choice(actions)

        self.setMove(bestMove)
        print('\tBest value', best, bestMove)

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
            if not self.timeRemaining():
                return None
            result = state.move(a)
            v = self.expectiPlayer(result, depth - 1)
            if v is None:
                return None
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
        empty_indices = [i for i in range(16) if state._board[i] == 0]
        num_empty = len(empty_indices)
        if num_empty == 0:
            return self.heuristic(state)

        for index in empty_indices:
            for value, prob in [(1, 0.9), (2, 0.1)]:
                result = state.addTile(index, value)
                v = self.maxPlayer(result, depth - 1)
                if v is None:
                    return None
                expected_value += (prob / num_empty) * v

        return expected_value

    def heuristic(self, state):
        board = state._board
        size = 4
        grid = [[board[4 * i + j] for j in range(size)] for i in range(size)]

        empty_tiles = sum(1 for val in board if val == 0)
        max_tile = max(board)
        corner_score = 0
        consistency = 0
        smoothness = 0

        corners = [grid[0][0], grid[0][-1], grid[-1][0], grid[-1][-1]]
        if max_tile in corners:
            corner_score += (2 ** max_tile) * 2.0

        empty_score = empty_tiles * 270

        for row in grid:
            for i in range(size - 1):
                if row[i] >= row[i + 1]:
                    consistency += 1

        for col in range(size):
            for i in range(size - 1):
                if grid[i][col] >= grid[i + 1][col]:
                    consistency += 1

        consistency_score = consistency * 47

        for i in range(size):
            for j in range(size - 1):
                smoothness -= abs((2 ** grid[i][j] if grid[i][j] else 0) - (2 ** grid[i][j + 1] if grid[i][j + 1] else 0))
                smoothness -= abs((2 ** grid[j][i] if grid[j][i] else 0) - (2 ** grid[j + 1][i] if grid[j + 1][i] else 0))

        return (
            state.getScore()
            + empty_score
            + corner_score
            + consistency_score
            + smoothness * 0.2
        )

    def moveOrder(self, state):
        return [a for a in 'LURD' if a in state.actions()]

    def stats(self):
        print(f'Average depth: {self._depthCount/self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
