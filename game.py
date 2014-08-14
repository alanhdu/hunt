import numpy as np

def numNeighbors(grid):
    m = grid.astype(int)
    m[1:-1, 1:-1] = (m[:-2,  :-2] + m[:-2, 1:-1] + m[:-2,  2:] +
                     m[1:-1, :-2] +                m[1:-1, 2:] +
                     m[2:,   :-2] + m[2:,  1:-1] + m[2:,   2:])
    return m

def rule12345_3(grid):
    n = numNeighbors(grid)
    return (n == 3) + ((0 < n) * (n < 6) * grid)

def debugMaze():
    maze = """\
*****************************************************
*                                                   *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                                                   *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                        *                          *
*                                                   *
*****************************************************"""
    return np.array([list(line) for line in maze.split("\n")])

class Game(object):
    def __init__(self, w=51, h=23, debug=False):
        self.players = {} 
        self.bullets = []

        start = -np.zeros((h+2, w+2), dtype=bool)
        start[1:-1, 1:-1] = np.random.rand(h, w) > 0.5
        for i in xrange(100):   # 100 interations of Rule 12345/3
            start = rule12345_3(start)
        self.arena = np.array([["*" if x else " " for x in y]
                               for y in start])
        if debug:
            self.arena = debugMaze()

    def addPlayer(self, username):
        if username in self.players:
            raise ValueError('Username already taken')
        self.players[username] = Player(self)
    def update(self):
        pass
    def __str__(self):
        height, width = self.shape
        return  "\n".join("".join(self.getType(x, y) 
                                  for x in xrange(width))
                          for y in xrange(height))
    def getType(self, x, y):
        if not self.isStar(x, y):
            return self.arena[y, x]

        top    = self.isStar(x, y - 1)
        bottom = self.isStar(x, y + 1)
        left   = self.isStar(x - 1, y)
        right  = self.isStar(x + 1, y)

        dash = left or right
        pipe = top or bottom

        if dash and pipe:
            return "+"
        elif dash:
            return "-"
        elif pipe:
            return "|"
        else:
            return "+"

    def isStar(self, x, y):
        if (x < 0 or y < 0):
            return False
        try:
            c = self.arena[y, x]
        except IndexError:
            return False
        return c == "*"


class Player(object):
    def __init__(self, game):
        h, w = game.arena.shape
        self.x, self.y = np.random.randint(w), np.random.randint(h)
        while game.arena[self.y, self.x] == "*":
            self.x, self.y = np.random.randint(w), np.random.randint(h)
        self.facing = "<>v^"[np.random.randint(4)]

        self.game = game
        game.arena[self.y, self.x] = self.facing

        mask = -np.zeros((h, w), dtype=bool)
        mask[0, :].fill(False)      # ensure edges are visible
        mask[-1, :].fill(False)
        mask[:, 0].fill(False)
        mask[:, -1].fill(False)

        self.view = np.ma.masked_array(game.arena, mask)
        self.updateMask()

    def move(self, direction):
        xs = {"<": -1, ">": 1, "^":  0, "v": 0}
        ys = {"<":  0, ">": 0, "^": -1, "v": 1}

        self.game.arena[self.y, self.x] = ' '

        self.x += xs[direction]
        self.y += ys[direction]

        if self.game.arena[self.y, self.x] == " ":
            self.updateMask()
        else:   # running into something
            self.x -= xs[direction]
            self.y -= ys[direction]

        self.game.arena[self.y, self.x] = self.facing


    def updateMask(self):
        x, y = self.x, self.y
        if self.game.arena[y, x] == "*":
            raise IndexError("Position located at a Wall")
        row = self.game.arena[y, :]
        col = self.game.arena[:, x]

        mask = np.zeros(self.game.arena.shape, dtype=bool)

        if self.facing != "v":
            mask[:y, x] = ((col[y - 1::-1] == "*").cumsum() == 0)[::-1]
        if self.facing != "^":
            mask[y+1:, x] = ((col[y + 1:] == "*").cumsum() == 0)
        if self.facing != ">":
            mask[y, :x] = ((row[x - 1::-1] == "*").cumsum() == 0)[::-1]
        if self.facing != "<":
            mask[y, x+1:] = ((row[x + 1:] == "*").cumsum() == 0)

        mask[y, x] = True

        # Expand all masks so you can see the walls
        # TODO Make expansion work with edges

        mask[1:-1, 1:-1] = (mask[:-2,  :-2] + mask[:-2, 1:-1] + mask[:-2,  2:] +
                            mask[1:-1, :-2] + mask[1:-1,1:-1] + mask[1:-1, 2:] +
                            mask[2:,   :-2] + mask[2:,  1:-1] + mask[2:,   2:])

        # Flip so True -> Masked & Invisible
        self.view.mask *= -mask

    def turn(self, direction):
        self.facing = direction
        self.updateMask()
        self.game.arena[self.y, self.x] = self.facing

    def __str__(self):
        h, w = self.view.shape
        s = "\n".join("".join(  self.game.getType(x, y) 
                                if not self.view.mask[y, x]
                                else " "
                              for x in xrange(w))
                      for y in xrange(h))
        return s
