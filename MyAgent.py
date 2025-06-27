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
        self.move = None  

    def findMove(self, state):
        self._count += 1
        empty = sum(1 for val in state._board if val == 0)
        depth = 3 if empty >= 6 else 2 if empty >= 3 else 1

        self._depthCount += 1
        self._parentCount += 1
        self._nodeCount += 1
        print('Search depth', depth)

        best = -math.inf
        bestMove = None

        for a in self.moveOrder(state):
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
            actions = state.actions()
            bestMove = random.choice(actions) if actions else None

        self.setMove(bestMove)
        self.move = bestMove
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
        grid = [[board[4 * i + j] for j in range(4)] for i in range(4)]

        empty_tiles = sum(1 for val in board if val == 0)
        max_tile = max(board)
        corner_bonus = 3000 if max_tile in [grid[0][0], grid[0][3], grid[3][0], grid[3][3]] else 0
        empty_score = empty_tiles * 500
        smoothness_score = -self._smoothness(grid) * 2
        monotonicity_score = -self._monotonicity(grid) * 100
        position_score = self._positionScore(grid) * 5

        return (
            state.getScore() +
            empty_score +
            corner_bonus +
            smoothness_score +
            monotonicity_score +
            position_score
        )

    def _smoothness(self, grid):
        score = 0
        for i in range(4):
            for j in range(3):
                a, b = grid[i][j], grid[i][j + 1]
                if a and b:
                    score += abs(math.log2(a) - math.log2(b))
        for j in range(4):
            for i in range(3):
                a, b = grid[i][j], grid[i + 1][j]
                if a and b:
                    score += abs(math.log2(a) - math.log2(b))
        return score

    def _monotonicity(self, grid):
        row_score = 0
        col_score = 0
        for row in grid:
            for i in range(3):
                row_score += abs(row[i] - row[i + 1])
        for col in zip(*grid):
            for i in range(3):
                col_score += abs(col[i] - col[i + 1])
        return row_score + col_score

    def _positionScore(self, grid):
        weights = [
            [16, 15, 14, 13],
            [5, 6, 7, 8],
            [4, 3, 2, 1],
            [0, 0, 0, 0]
        ]
        score = 0
        for i in range(4):
            for j in range(4):
                score += grid[i][j] * weights[i][j]
        return score

    def moveOrder(self, state):
        board = state._board
        max_tile = max(board)
        max_index = board.index(max_tile)
        preferred = ['U', 'L', 'D', 'R'] if max_index in [0, 3, 12, 15] else ['L', 'U', 'R', 'D']
        return [a for a in preferred if a in state.actions()]

    def stats(self):
        print(f'Average depth: {self._depthCount / self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
