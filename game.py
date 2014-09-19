from __future__ import division
from collections import namedtuple, deque, defaultdict
from decimal import *

import numpy as np

import custom_exceptions as excpt

def numNeighbors(grid):
    m = grid.astype(int)
    m[1:-1, 1:-1] = (m[:-2,  :-2] + m[:-2, 1:-1] + m[:-2,  2:] +
                     m[1:-1, :-2] +                m[1:-1, 2:] +
                     m[2:,   :-2] + m[2:,  1:-1] + m[2:,   2:])
    return m

def rule12345_3(grid):
    n = numNeighbors(grid)
    return (n == 3) + ( (0 < n) * (n < 6) * grid)

def rule1234_3(grid):
    n = numNeighbors(grid)
    return (n == 3) + ( (0 < n) * (n < 5) * grid)

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

speed = defaultdict(int, {"move": 4})
damage = {"bullet": 5, "stab": 2}

class Game(object):
    def __init__(self, w=51, h=23, debug=False):
        self.players = {} 
        self.bullets = []

        start = -np.zeros((h+2, w+2), dtype=bool)
        start[1:-1, 1:-1] = np.random.rand(h, w) > 0.8
        for i in xrange(200):
            start = rule1234_3(start)
        self.arena = np.array([["*" if x else " " for x in y]
                               for y in start])
        if debug:
            self.arena = debugMaze()

    def addPlayer(self, username):
        if username in self.players:
            raise excpt.UsernameTaken(username)
        self.players[username] = Player(self, username)

    def findPlayer(self, pos):
        for player in self.players.itervalues():
            if player.pos == pos:
                return player

    def update(self):
        # Update player movements
        for player in self.players.itervalues():
            player.update()

        # Update bullet movements
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
            elif self.arena[bullet.pos] in "<>v^":
                player = self.findPlayer(bullet.pos)
                player.hit(bullet.source, "bullet")
        # Update scores
        for player in self.players.itervalues():
            player.updateScore()

    def __str__(self):
        height, width = self.arena.shape
        return  "\n".join("".join(self.getType(x, y) 
                                  for x in xrange(width))
                          for y in xrange(height))
    def inArena(self, p):
        # don't allow things to hit the edge, so 0 < a < b-1, not 0 <= a < b
        return all(0 < a < b - 1 for a, b in zip(p, self.arena.shape))
    def getType(self, x, y):
        if self.arena[y, x] != "*":
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
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.deaths = self.kills = self.currentScore = 0
        self.score = Decimal(0)
        self.cloak = self.scan = False
        self.rebirth()

    def rebirth(self, health=10, ammo=15):
        h, w = self.game.arena.shape
        self.pos = Point(np.random.randint(h), np.random.randint(w))
        while self.game.arena[self.pos] == "*":
            self.pos = Point(np.random.randint(h), np.random.randint(w))
        self.facing = "<>v^"[np.random.randint(4)]
        self.game.arena[self.pos] = self.facing

        mask = np.zeros((h, w), dtype=bool)
        # ensure visible edges
        mask[1:-1, 1:-1] = -np.zeros((h-2, w-2), dtype=bool) 

        self.view = np.ma.masked_array(self.game.arena, mask)
        self.updateMask()

        self.actions = deque()
        self.lastActionTime = 0

        self.health = health
        self.ammo = ammo

        for player in self.game.players.itervalues():
            player.ammo += 5

    def updateMask(self):
        y, x = self.pos
        if self.game.arena[self.pos] == "*":
            raise excpt.HittingAWall()
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

        # Scan for other player's locations
        if self.scan:
            for player in self.game.players.itervalues():
                if not player.cloak:
                    mask[player.pos] = True

        # Expand all masks so you can see the walls
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
        self.msg = None
        if self.actions:
            func, args, kwargs = self.actions.popleft()
            if func == "move" and self.lastActionTime >= speed["move"]:
                self.move(*args, **kwargs)
                self.lastActionTime = 0
            elif func == "move":
                self.lastActionTime += 1
                self.actions.appendleft( (func, args, kwargs) )
            elif func == "turn" and self.lastActionTime >= speed["turn"]:
                self.lastActionTime += 1
                self.turn(*args, **kwargs)
            elif func == "fire" and self.lastActionTime >= speed["fire"]:
                self.lastActionTime += 1
                self.fire(*args, **kwargs)
        else:
            self.lastActionTime += 1

        self.updateMask()

    def move(self, direction):
        self.game.arena[self.pos] = ' '
        p = move(self.pos, direction)

        if self.cloak:
            self.ammo -= 0.05
        else:
            for player in self.game.players.itervalues():
                if player.scan and player is not self:
                    player.ammo -= 0.05

        if self.game.inArena(p):
            if self.game.arena[p] == " ":
                self.pos = p
                self.updateMask()
            elif self.game.arena[p] in "<>v^" and direction == self.facing:
                # if we're facing someone and move into them, stab
                other = self.game.findPlayer(p)
                other.hit(self, "stab")

        self.game.arena[self.pos] = self.facing

    def turn(self, direction):
        self.facing = direction
        self.updateMask()
        self.game.arena[self.pos] = self.facing

    def fire(self):
        pos = move(self.pos, self.facing)
        if self.game.inArena(pos):
            if self.ammo > 0:
                bullet = Bullet(pos, self.facing, self)
                self.ammo -= 1
                if self.game.arena[bullet.pos] == " ":
                    self.game.bullets.append(bullet)
                    self.game.arena[bullet.pos] = ":"
                elif self.game.arena[bullet.pos] == "*":
                    self.game.arena[bullet.pos] = " "
                elif self.game.arena[bullet.pos] in "v^<>": # Direct hit
                    other = self.game.findPlayer(bullet.pos)
                    other.hit(self, "bullet")
            else:
                self.msg = "You are out of ammo"


    def hit(self, src, method):
        if method == "bullet":
            self.msg = "{src} hit you with a bullet".format(src=src.name)
            src.msg = "You hit {target} with a bullet".format(target=self.name)
        elif method == "stab":
            self.msg = "{src} stabbed you".format(src=src.name)
            src.msg = "You stabbed {target}".format(target=self.name)

        self.health -= damage[method]
        if self.health <= 0:
            self.msg = "{src} killed you".format(src=src.name)
            src.msg = "You killed {target}".format(target=self.name)

            src.health += 2     #generate health
            src.kills += 1
            self.deaths += 1

            self.currentScore -= 1
            src.currentScore += 1

            self.game.arena[self.pos] = " "
            self.rebirth()

    def updateScore(self):
        # use Decimal to avoid annoying scores like 0.000000000001
        self.score = Decimal('0.998') * self.score + self.currentScore
        self.currentScore = 0

    def __str__(self):
        h, w = self.view.shape
        s = "\n".join("".join(  self.game.getType(x, y) 
                                if not self.view.mask[y, x]
                                else " "
                              for x in xrange(w))
                      for y in xrange(h))
        return s

    def to_json(self):
        d = {"arena": str(self), "ammo": self.ammo, "health": self.health,
             "scores": {name: {"kills":player.kills, "deaths":player.deaths,
                               "score":round(player.score, 3)}      # 3 decimal points of score
                        for name, player in self.game.players.iteritems()}}
        if self.msg:
            d["msg"] = self.msg

        return d
