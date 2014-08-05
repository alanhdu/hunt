import numpy as np

def numNeighbors(grid):
    x, y = grid.shape
    m = np.zeros( (x+2, y+2) )  # add edges
    m[1:-1, 1:-1] = grid.astype(int)
    return (m[:-2,  :-2] + m[:-2, 1:-1] + m[:-2,  2:] + 
            m[1:-1, :-2] + m[1:-1,1:-1] + m[1:-1, 2:] +
            m[2:,   :-2] + m[2:,  1:-1] + m[2:,   2:])

def rule12345_3(grid):
    n = numNeighbors(grid)
    return (n == 3) + ( (0 < n) * (n < 6) * grid)

class Game(object):
    def __init__(self, w=64, h=48):
        self.arena = Arena(w, h)
        self.players = {} 
    def addPlayer(self, username):
        if username in self.players:
            raise ValueError('Username already taken')
        self.players[username] = Player(self.arena)

class Arena(object):
    def __init__(self, w=64, h=48, density=0.5):
        start = np.random.rand(h, w) > density

        for i in xrange(100):   # 100 interations of Rule 12345/3
            n = numNeighbors(start)
            start = (n == 3) + ( (n > 0) * (n < 6) * start)
        self._translate(start)
    def _translate(self, grid):
        self.maze = np.array([["*" if x else " " for x in y]
                              for y in grid ])
    def __str__(self):
        s = "\n".join("".join(x for x in y)
                      for y in self.maze)
        return s
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
        self.arena = arena

        self.facing = "<>v^"[np.random.randint(4)]
        self.view = np.ma.masked_array(arena.maze, arena.getMask(self.x, self.y))
    def move(self, direction):
        xs = {"<": -1, ">": 1, "^":  0, "v": 0}
        ys = {"<":  0, ">": 0, "^": -1, "v": 1}
        self.x += xs[direction]
        self.y += ys[direction]

        try:
            mask = self.arena.getMask(self.x, self.y)
            self.view.mask *= mask
        except IndexError:  # TODO Use custom errors
            print "Moving into a wall"
            print self.x, self.y, xs[direction], ys[direction]
            self.x -= xs[direction]
            self.y -= ys[direction]
    def __str__(self):
        arena = self.view.filled(" ")
        arena[self.y, self.x] = self.facing
        s = "\n".join("".join(x for x in y)
                      for y in arena)
        return s
