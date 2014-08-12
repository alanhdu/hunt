import numpy as np

def numNeighbors(grid):
    m = grid.astype(int)
    m[1:-1, 1:-1] = (m[:-2,  :-2] + m[:-2, 1:-1] + m[:-2,  2:] +
                     m[1:-1, :-2] + m[1:-1,1:-1] + m[1:-1, 2:] +
                     m[2:,   :-2] + m[2:,  1:-1] + m[2:,   2:] -
                     m[1:-1, 1:-1]) # stops a cell from counting itself as a neighbor
    return m

def rule12345_3(grid):
    n = numNeighbors(grid)
    return (n == 3) or ( (0 < n) and (n < 6) and grid)

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
        start = -np.zeros( (h, w), dtype=bool)
        start[1:-1, 1:-1] = np.random.rand(h-2, w-2) > density

        for i in xrange(100):   # 100 interations of Rule 12345/3
            n = numNeighbors(start)
            start = (n == 3) + ( (n > 0) * (n < 6) * start)
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
    def _translate(self, grid):
        self.maze = np.array([["*" if x else " " for x in y]
                              for y in grid ])
    def __str__(self):
        s = "\n".join("".join(self.getType(x, y) for x in range(len(self.maze[y])))
                      for y in range(len(self.maze)))
        return s
    def getType(self, x, y):
        if not self.isStar(x, y):
            return self.maze[y, x]
        top   = self.isStar(x  , y-1)
        bot   = self.isStar(x  , y+1)
        left  = self.isStar(x-1, y)
        right = self.isStar(x+1, y)

        dash = False
        pipe = False
        if left or right:
            dash = True
        if top or bot:
            pipe = True

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

    def getMask(self, x, y):
        if self.maze[y, x] == '*':
            raise IndexError("Position located at a Wall")
        row = self.maze[y, :]
        col = self.maze[:, x]

        view = np.zeros(self.maze.shape, dtype=bool)

        view[:y,   x] = ((col[:y][::-1]   == "*").cumsum() == 0)[::-1]
        view[y+1:, x] = ((col[y+1:] == "*").cumsum() == 0)

        view[y, :x]   = ((row[:x][::-1]   == "*").cumsum() == 0)[::-1]
        view[y, x+1:] = ((row[x+1:] == "*").cumsum() == 0)

        view[y, x] = False

        # Expand all easks so you can see the walls
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

        self.view = np.ma.masked_array(arena.maze, arena.getMask(self.x, self.y))

        # Ensure edges are visible
        self.view.mask[0,  :].fill(False)
        self.view.mask[-1, :].fill(False)
        self.view.mask[:,  0].fill(False)
        self.view.mask[:, -1].fill(False)
    def move(self, direction):
        xs = {"<": -1, ">": 1, "^":  0, "v": 0}
        ys = {"<":  0, ">": 0, "^": -1, "v": 1}

        self.arena.maze[self.y, self.x] = ' '

        self.x += xs[direction]
        self.y += ys[direction]

        if self.arena.maze[self.y, self.x] == " ":
            mask = self.arena.getMask(self.x, self.y)
            self.view.mask *= mask
        else:   # running into something
            self.x -= xs[direction]
            self.y -= ys[direction]

        self.arena.maze[self.y, self.x] = self.facing

    def turn(self, direction):
        self.facing = direction
        self.arena.maze[self.y, self.x] = self.facing

    def __str__(self):
        h, w = self.view.shape
        s = "\n".join("".join(  self.arena.getType(x, y) 
                                if not self.view.mask[y, x]
                                else " "
                              for x in xrange(w))
                      for y in xrange(h))
        return s

