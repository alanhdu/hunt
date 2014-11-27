from __future__ import division
from collections import namedtuple, deque
import settings
from decimal import Decimal
from random import shuffle

import numpy as np

import custom_exceptions as excpt

Point = namedtuple("Point", ["y", "x"])
Projectile = namedtuple("Projectile", ["pos", "direction", "source", "type"])

def in_arena(p, arena):
    # don't allow things to hit the edge, so 0 < a < b-1, not 0 <= a < b
    return all(0 < a < b - 1 for a, b in zip(p, arena.shape))

def move(p, direction):
    if direction == "<":
        return Point(x=p.x-1, y=p.y)
    elif direction == ">":
        return Point(x=p.x+1, y=p.y)
    elif direction == "^":
        return Point(x=p.x, y=p.y-1)
    elif direction == "v":
        return Point(x=p.x, y=p.y+1)
    else:
        raise ValueError("Direction must be <>v^. Got " + direction)

def generate_maze(width, height):
    if width % 2 == 0:
        width -= 1
    if height % 2 == 0:
        height -= 1

    maze = -np.zeros((height + 2, width + 2), dtype=bool)
    cell = Point(y=0, x=0)
    visited = {cell}
    stack = deque([cell])

    def odd(p):
        return Point(y=p.y * 2 + 1, x=p.x * 2 + 1)

    dirs = list("<>v^")
    while len(stack) > 0:
        maze[odd(cell)] = False
        shuffle(dirs)

        changed = False
        for d in dirs:
            wall = move(odd(cell), d)
            if in_arena(wall, maze) and move(cell, d) not in visited:
                maze[wall] = False
                cell = move(cell, d)
                visited.add(cell)
                stack.append(cell)
                changed = True
                break

        if not changed:
            cell = stack.pop()

    return np.array([["*" if x else " " for x in y]
                    for y in maze])


def debugMaze():
    maze = """\
*****************************************************
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
    def __init__(self, setting=settings.default, debug=False):
        self.settings = setting
        self.players = {}
        self.projectiles = []

        if not debug:
            self.arena = generate_maze(setting.w, setting.h)
        else:
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
        # clear explosions
        height, width = self.arena.shape
        for x in xrange(width):
            for y in xrange(height):
                if self.arena[y, x] == "#":
                    self.arena[y, x] = " "

        # clear projectiles
        for i in xrange(self.settings.pace):
            for proj in self.projectiles:
                self.arena[proj.pos] = " "

            projectiles = [Projectile(move(proj.pos, proj.direction),
                                      proj.direction, proj.source, proj.type)
                           for proj in self.projectiles]
            self.projectiles = []
            for proj in projectiles:
                self.updateProjectile(proj)

        # Update player movements
        for player in self.players.itervalues():
            player.update()

        # Update scores
        for player in self.players.itervalues():
            player.updateScore()
            player.updateMask()

        # regenerate recharges
        while len(self.players) > (self.arena == 'A').sum():
            h, w = self.arena.shape
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            while self.arena[y, x] != " ":
                y, x = np.random.randint(0, h), np.random.randint(0, w)
            self.arena[y, x] = "A"

    def updateProjectile(self, proj):
        render = {"bullet": ":", "bomb": "o"}
        if self.arena[proj.pos] == " " and self.inArena(proj.pos):
            self.arena[proj.pos] = render[proj.type]
            self.projectiles.append(proj)
        elif proj.type == "bullet":
            if self.arena[proj.pos] == "*" and self.inArena(proj.pos):
                self.arena[proj.pos] = " "
            elif self.arena[proj.pos] in "<>v^":
                player = self.findPlayer(proj.pos)
                player.hit(proj.source, proj.type)
        elif proj.type == "bomb" and self.arena[proj.pos] in "A#<>v^*":
            y, x = proj.pos

            for player in self.players.values():
                py, px = player.pos
                if (y - 1 <= py <= y + 1) and (x - 1 <= px <= x + 1):
                    player.hit(proj.source, proj.type)

            # prevent things from clearing the edges
            h, w = self.arena.shape
            y_low = max(y - 1, 1)
            y_high = min(y + 2, h - 1)

            x_low = max(x - 1, 1)
            x_high = min(x + 2, w - 1)

            cs = self.arena[y_low:y_high, x_low:x_high]
            cs[:] = "#"

    def __str__(self):
        height, width = self.arena.shape
        return "\n".join("".join(self.arena[y, x]
                                 for x in xrange(width))
                         for y in xrange(height))
    def inArena(self, p):
        # don't allow things to hit the edge, so 0 < a < b-1, not 0 <= a < b
        return in_arena(p, self.arena)

class Player(object):
    game, name, deaths, score, cloak = None, None, None, None, None
    view, ammo, kills, pos, facing = None, None, None, None, None
    actions, lastActionTime, msg, health = None, None, None, None
    currentView = None

    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.deaths = self.kills = 0
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

        # ensure visible edges
        mask = np.zeros((h, w), dtype=bool)
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

        def stopper(array):
            b = np.zeros(array.shape, dtype=bool)
            for stop in "*v^<>":
                b += (array == stop)
            return b

        if self.facing != "v":
            mask[:y, x] = (stopper(col[y - 1::-1]).cumsum() == 0)[::-1]
        if self.facing != "^":
            mask[y+1:, x] = stopper(col[y + 1:]).cumsum() == 0
        if self.facing != ">":
            mask[y, :x] = (stopper(row[x - 1::-1]).cumsum() == 0)[::-1]
        if self.facing != "<":
            mask[y, x+1:] = stopper(row[x + 1:]).cumsum() == 0

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
        self.currentView = -mask
        self.view.mask *= -mask

    def queue(self, action, *args, **kwargs):
        if len(self.actions) > 5:       # only queue 5 actions at a time
            self.actions.popleft()
        self.actions.append((action, args, kwargs))

    def update(self):
        self.game.arena[self.pos] = self.facing
        self.msg = None
        if self.actions:
            func, args, kwargs = self.actions.popleft()
            speed = self.game.settings.speed
            if func == "move" and self.lastActionTime >= speed["move"]:
                self.move(*args, **kwargs)
                self.lastActionTime = 1
            else:
                if func == "move":
                    self.queue(func, *args, **kwargs)
                elif func == "turn" and self.lastActionTime >= speed["turn"]:
                    self.turn(*args, **kwargs)
                elif func == "fire" and self.lastActionTime >= speed["fire"]:
                    self.fire(*args, type="bullet", **kwargs)
                elif func == "bomb" and self.lastActionTime >= speed["fire"]:
                    self.fire(*args, type="bomb", **kwargs)

                self.lastActionTime += self.game.settings.pace
        else:
            self.lastActionTime += self.game.settings.pace

        self.updateMask()

    def move(self, direction):
        self.game.arena[self.pos] = ' '
        p = move(self.pos, direction)

        if self.cloak :
            if self.ammo >= self.game.settings.ammo["cloak"]:
                self.ammo -= self.game.settings.ammo["cloak"]
            else:
                self.cloak = False
                self.msg = "No more ammo for cloaking"
        else:
            for player in self.game.players.itervalues():
                if player.scan and player is not self:
                    if player.ammo >= self.game.settings.ammo["scan"]:
                        player.ammo -= self.game.settings.ammo["scan"]
                    else:
                        player.scan = False
                        player.msg = "No more ammo for scanning"

        if self.game.inArena(p):
            if self.game.arena[p] == " ":
                self.pos = p
                self.updateMask()
            if self.game.arena[p] == "A":
                self.ammo += self.game.settings.ammo["recharge"]
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

    def fire(self, type):
        pos = move(self.pos, self.facing)
        if self.game.inArena(pos):
            if self.ammo >= self.game.settings.ammo[type]:
                proj = Projectile(pos, self.facing, self, type)
                self.ammo -= self.game.settings.ammo[type]
                self.game.updateProjectile(proj)
            else:
                self.msg = "You don't have enough ammo for a {}".format(type)

    def hit(self, src, method):
        self.health -= self.game.settings.damage[method]
        if src is self:
            if method == "bullet":
                self.msg = "You hit yourself with a bullet"
            elif method == "bomb":
                self.msg = "You hit yourself with a bomb"
            elif method == "stab":
                self.msg = "You managed to stab yourself. That shouldn't be possible"

            if self.health <= 0:
                self.msg = "You commited suicide!"
                self.kills += 1
                self.deaths += 1
                self.score -= 5
                self.rebirth()
        else:
            if method == "bullet":
                self.msg = "{src} hit you with a bullet".format(src=src.name)
                src.msg = "You hit {target} with a bullet".format(target=self.name)
            elif method == "stab":
                self.msg = "{src} stabbed you".format(src=src.name)
                src.msg = "You stabbed {target}".format(target=self.name)
            elif method == "bomb":
                self.msg = "{src} hit you with a bomb".format(src=src.name)
                src.msg = "You hit {target} with a bomb".format(target=self.name)

            if self.health <= 0:
                self.msg = "{src} killed you".format(src=src.name)
                src.msg = "You killed {target}".format(target=self.name)

                src.health += 2     # generate health
                src.kills += 1
                self.deaths += 1

                self.score -= 1
                src.score += 1

                self.game.arena[self.pos] = " "
                self.rebirth()

    def updateScore(self):
        # use Decimal to avoid annoying scores like 0.000000000001
        self.score = Decimal('0.9998') * self.score

    def getView(self, x, y):
        c = self.game.arena[y, x]
        if not self.currentView[y, x]:
            return c
        elif not self.view.mask[y, x] and c == "*":  # walls of arena
            return c
        else:
            return " "

    def __str__(self):
        h, w = self.view.shape
        s = "\n".join("".join(self.getView(x, y)
                              for x in xrange(w))
                      for y in xrange(h))
        return s

    def to_json(self):
        d = {"arena": str(self), "ammo": self.ammo, "health": self.health,
             "x": self.pos.x, "y": self.pos.y, "cloak": self.cloak, 
             "scan": self.scan,
             "scores": {name: {"kills": player.kills, "deaths": player.deaths,
                               "score": round(player.score, 3)}
                        for name, player in self.game.players.iteritems()}}
        if self.msg:
            d["msg"] = self.msg

        return d
