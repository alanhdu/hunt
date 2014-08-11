import numpy as np

def numNeighbors(grid):
    m = grid.astype(int)
    m[1:-1, 1:-1] = (m[:-2,  :-2] + m[:-2, 1:-1] + m[:-2,  2:] +
                     m[1:-1, :-2] + m[1:-1,1:-1] + m[1:-1, 2:] +
                     m[2:,   :-2] + m[2:,  1:-1] + m[2:,   2:])
    return m

def rule12345_3(grid):
    n = numNeighbors(grid)
    return (n == 3) + ((0 < n) * (n < 6) * grid)

class Game(object):
    def __init__(self, w=51, h=23, debug=False):
        self.arena = Arena(w, h, debug=debug)
        self.players = {} 
    def addPlayer(self, username):
        if username in self.players:
            raise ValueError('Username already taken')
        self.players[username] = Player(self.arena)

class Arena(object):
    def __init__(self, w=51, h=23, density=0.5, debug=False):
        start = -np.zeros((h+2, w+2), dtype=bool)
        start[1:-1, 1:-1] = np.random.rand(h, w) > density
        self.shape = start.shape

        for i in xrange(100):   # 100 interations of Rule 12345/3
            start = rule12345_3(start)
        self._translate(start)

        if debug:
            self.maze = """\
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
            self.maze = np.array([ list(line) for line in self.maze.split("\n")])
    def __getitem__(self, *args, **kwargs):
        return self.maze.__getitem__(*args, **kwargs)
    def _translate(self, grid):
        self.maze = np.array([["*" if x else " " for x in y]
                              for y in grid ])
    def __str__(self):
        height, width = self.shape
        return  "\n".join("".join(self.getType(x, y) 
                                  for x in xrange(width))
                          for y in xrange(height))
    def getType(self, x, y):
        if not self.isStar(x, y):
            return self[y, x]

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
            c = self.maze[y, x]
        except IndexError:
            return False
        return c == "*"

    def getMask(self, x, y, facing):
        if self.maze[y, x] == '*':
            raise IndexError("Position located at a Wall")
        row = self.maze[y, :]
        col = self.maze[:, x]

        view = np.zeros(self.maze.shape, dtype=bool)

        if facing != "v":
            view[:y, x] = ((col[y - 1::-1] == "*").cumsum() == 0)[::-1]
        if facing != "^":
            view[y+1:, x] = ((col[y + 1:] == "*").cumsum() == 0)
        if facing != ">":
            view[y, :x] = ((row[x - 1::-1] == "*").cumsum() == 0)[::-1]
        if facing != "<":
            view[y, x+1:] = ((row[x + 1:] == "*").cumsum() == 0)

        view[y, x] = True

        # Expand all masks so you can see the walls
        # TODO Make expansion work with edges

        view[1:-1, 1:-1] = (view[:-2,  :-2] + view[:-2, 1:-1] + view[:-2,  2:] +
                            view[1:-1, :-2] + view[1:-1,1:-1] + view[1:-1, 2:] +
                            view[2:,   :-2] + view[2:,  1:-1] + view[2:,   2:])

        # Flip so True -> Masked & Invisible
        return -view

class Player(object):
    def __init__(self, arena):
        h, w = arena.maze.shape
        self.x, self.y = np.random.randint(w), np.random.randint(h)
        while arena.maze[self.y, self.x] == "*":
            self.x, self.y = np.random.randint(w), np.random.randint(h)
        self.facing = "<>v^"[np.random.randint(4)]

        arena.maze[self.y, self.x] = self.facing
        self.arena = arena

        mask = arena.getMask(self.x, self.y, self.facing)
        mask[0, :].fill(False)      # ensure edges are visible
        mask[-1, :].fill(False)
        mask[:, 0].fill(False)
        mask[:, -1].fill(False)
        self.view = np.ma.masked_array(arena.maze, mask)

    def move(self, direction):
        xs = {"<": -1, ">": 1, "^":  0, "v": 0}
        ys = {"<":  0, ">": 0, "^": -1, "v": 1}

        self.arena.maze[self.y, self.x] = ' '

        self.x += xs[direction]
        self.y += ys[direction]

        if self.arena.maze[self.y, self.x] == " ":
            mask = self.arena.getMask(self.x, self.y, self.facing)
            self.view.mask *= mask
        else:   # running into something
            self.x -= xs[direction]
            self.y -= ys[direction]

        self.arena.maze[self.y, self.x] = self.facing

    def turn(self, direction):
        self.facing = direction
        mask = self.arena.getMask(self.x, self.y, self.facing)
        self.view.mask *= mask
        self.arena.maze[self.y, self.x] = self.facing

    def __str__(self):
        h, w = self.view.shape
        s = "\n".join("".join(  self.arena.getType(x, y) 
                                if not self.view.mask[y, x]
                                else " "
                              for x in xrange(w))
                      for y in xrange(h))
        return s
