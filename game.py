from collections import namedtuple, deque

import numpy as np

def numNeighbors(grid):
    m = grid.astype(int)
    m[1:-1, 1:-1] = (m[:-2,  :-2] + m[:-2, 1:-1] + m[:-2,  2:] +
                     m[1:-1, :-2] +                m[1:-1, 2:] +
                     m[2:,   :-2] + m[2:,  1:-1] + m[2:,   2:])
    return m

def rule12345_3(grid):
    n = numNeighbors(grid)
    return (n == 3) + ( (0 < n) * (n < 6) * grid)

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

def move(p, direction):
    if direction == "<":
        return Point(x=p.x-1, y=p.y)
    elif direction == ">":
        return Point(x=p.x+1, y=p.y)
    elif direction == "^":
        return Point(x=p.x, y=p.y-1)
    elif direction == "v":
        return Point(x=p.x, y=p.y+1)

Point = namedtuple("Point", ["y", "x"])
Bullet = namedtuple("Bullet", ["pos", "direction", "source"])

speeds = {"bullet": 1, "move": 3}   # movement is 5 times slower than bullets

class Game(object):
    def __init__(self, w=51, h=23, debug=False):
        self.players = {} 
        self.bullets = []

        start = -np.zeros((h+2, w+2), dtype=bool)
        start[1:-1, 1:-1] = np.random.rand(h, w) > 0.5
        for i in xrange(250):
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
        for bullet in self.bullets:
            self.arena[bullet.pos] = " "

        bullets = [Bullet(move(bullet.pos, bullet.direction), 
                          bullet.direction, bullet.source)
                   for bullet in self.bullets
                   if self.inArena(move(bullet.pos, bullet.direction))]
        self.bullets = []
        for bullet in bullets:
            if self.arena[bullet.pos] == " ":
                self.arena[bullet.pos] = ":"
                self.bullets.append(bullet)
            elif self.arena[bullet.pos] == "*":
                self.arena[bullet.pos] = " "

        for player in self.players.itervalues():
            player.update()

    def __str__(self):
        height, width = self.arena.shape
        return  "\n".join("".join(self.getType(x, y) 
                                  for x in xrange(width))
                          for y in xrange(height))
    def inArena(self, p):
        # don't allow things to hit the edge, so 0 < a < b-1, not 0 <= a < b
        return all(0 < a < b - 1 for a, b in zip(p, self.arena.shape))
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
        x, y = np.random.randint(w), np.random.randint(h)
        while game.arena[y, x] == "*":
            x, y = np.random.randint(w), np.random.randint(h)
        self.pos = Point(x=x, y=y)
        self.facing = "<>v^"[np.random.randint(4)]

        self.game = game
        game.arena[self.pos] = self.facing

        mask = -np.zeros((h, w), dtype=bool)
        mask[0, :].fill(False)      # ensure edges are visible
        mask[-1, :].fill(False)
        mask[:, 0].fill(False)
        mask[:, -1].fill(False)

        self.view = np.ma.masked_array(game.arena, mask)
        self.updateMask()

        self.actions = deque()
        self.lastActionTime = 0

    def updateMask(self):
        y, x = self.pos
        if self.game.arena[self.pos] == "*":
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

    def queue(self, action, *args, **kwargs):
        if len(self.actions) > 5:       # only queue 5 actions at a time
            self.actions.popleft()
        self.actions.append((action, args, kwargs))

    def update(self):
        if self.actions:
            func, args, kwargs = self.actions.popleft()
            if func == "move" and self.lastActionTime == speeds["move"]:
                self.move(*args, **kwargs)
                self.lastActionTime = 0
            elif func == "move":
                self.lastActionTime += 1
                self.actions.appendleft( (func, args, kwargs) )
            elif func == "turn":
                self.turn(*args, **kwargs)
                self.lastActionTime = 0
            elif func == "fire":
                self.fire(*args, **kwargs)
                self.lastActionTime = 0
        else:
            self.lastActionTime = 0

        self.updateMask()

    def move(self, direction):
        self.game.arena[self.pos] = ' '
        p = move(self.pos, direction)

        if self.game.inArena(p) and self.game.arena[p] == " ":
            self.pos = p
            self.updateMask()
        self.game.arena[self.pos] = self.facing

    def turn(self, direction):
        self.facing = direction
        self.updateMask()
        self.game.arena[self.pos] = self.facing

    def fire(self):
        pos = move(self.pos, self.facing)
        if self.game.inArena(pos):
            bullet = Bullet(pos, self.facing, self)
            if self.game.arena[bullet.pos] == " ":
                self.game.bullets.append(bullet)
                self.game.arena[bullet.pos] = ":"
            elif self.game.arena[bullet.pos] == "*":
                self.game.arena[bullet.pos] = " "

    def __str__(self):
        h, w = self.view.shape
        s = "\n".join("".join(  self.game.getType(x, y) 
                                if not self.view.mask[y, x]
                                else " "
                              for x in xrange(w))
                      for y in xrange(h))
        return s
