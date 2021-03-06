from __future__ import division
from collections import namedtuple, deque
import settings
from random import shuffle

import numpy as np

import custom_exceptions as excpt

Point = namedtuple("Point", ["y", "x"])
Projectile = namedtuple("Projectile", ["pos", "direction", "source", "type"])


def in_arena(p, arena):
    # don't allow things to hit the edge, so 0 < a < b-1, not 0 <= a < b
    return all(0 < a < b - 1 for a, b in zip(p, arena.shape))


def move(p, direction=None):
    if isinstance(p, Point):
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
    elif isinstance(p, Projectile):
        pos = move(p.pos, p.direction)
        return Projectile(pos, p.direction, p.source, p.type)


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
*     A                  *                          *
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
    players, projectiles, arena = None, None, None
    deleted, thread = None, None

    def __init__(self, setting=settings.default, debug=False):
        self.settings = setting
        self.players = {}
        self.projectiles = []
        self.deleted = deque()

        if not debug:
            self.arena = generate_maze(setting.w, setting.h)
        else:
            self.arena = debugMaze()

    def add_player(self, username):
        if username in self.players:
            raise excpt.UsernameTaken(username)
        self.players[username] = Player(self, username)

    def find_player(self, pos):
        for player in self.players.itervalues():
            if player.pos == pos:
                return player

    def update(self):
        # update projectiles
        arena = self.arena
        for i in xrange(self.settings.pace):
            clear = (arena == "#") + (arena == ":") + (arena == "o")
            arena[clear] = " "
            projectiles, self.projectiles = self.projectiles, []
            for proj in projectiles:
                self.update_projectile(proj)

        # Update player movements
        for player in self.players.itervalues():
            player.update_action()
            player.update_score()

        # regenerate walls
        for i in xrange(len(self.deleted) - 15):
            l = self.deleted.popleft()
            if self.arena[l] not in "<>v^":
                self.arena[l] = "*"
            else:   # don't regenerate wall on top of player
                self.deleted.append(l)

        # regenerate ammo recharges
        while len(self.players) > (self.arena == 'A').sum():
            h, w = self.arena.shape
            pos = np.random.randint(0, h), np.random.randint(0, w)
            while self.arena[pos] != " ":
                pos = np.random.randint(0, h), np.random.randint(0, w)
            self.arena[pos] = "A"

        # Update View
        for player in self.players.itervalues():
            player.update_view()

    def update_projectile(self, old_proj):
        render = {"bullet": ":", "bomb": "o"}
        proj = move(old_proj)

        if self.in_arena(proj.pos):
            if self.arena[proj.pos] == " ":
                self.arena[proj.pos] = render[proj.type]
                self.projectiles.append(proj)
            elif self.arena[proj.pos] == "A":
                self.projectiles.append(proj)   # Let projectile pass by
            elif proj.type == "bullet":
                if self.arena[proj.pos] == "*":
                    self.arena[proj.pos] = render[proj.type]
                    self.deleted.append(proj.pos)
                elif self.arena[proj.pos] in "<>v^":
                    player = self.find_player(proj.pos)
                    player.hit(proj.source, proj.type)

        hit = self.arena[proj.pos] != "o"
        edge = not self.in_arena(proj.pos)

        if proj.type == "bomb" and (hit or edge):
            if hit:
                y, x = proj.pos
            elif edge:
                y, x = old_proj.pos
            for player in self.players.itervalues():
                py, px = player.pos
                if (y - 1 <= py <= y + 1) and (x - 1 <= px <= x + 1):
                    player.hit(proj.source, proj.type)

            h, w = self.arena.shape
            y_low = max(y - 1, 1)
            y_high = min(y + 2, h - 1)

            x_low = max(x - 1, 1)
            x_high = min(x + 2, w - 1)

            for y in xrange(y_low, y_high):
                for x in xrange(x_low, x_high):
                    if self.arena[y, x] == "*":
                        self.deleted.append(Point(y=y, x=x))
            self.arena[y_low:y_high, x_low:x_high] = "#"

    def __str__(self):
        height, width = self.arena.shape
        return "\n".join("".join(self.arena[y, x]
                                 for x in xrange(width))
                         for y in xrange(height))

    def to_json(self):
        return {name: {"kills": player.kills, "deaths": player.deaths,
                       "score": player.score}
                for name, player in self.players.iteritems()}

    def in_arena(self, p):
        # don't allow things to hit the edge, so 0 < a < b-1, not 0 <= a < b
        return in_arena(p, self.arena)


class Player(object):
    game, name, deaths, score, cloak, msg = None, None, None, None, None, None
    view, ammo, kills, pos, facing, health = None, None, None, None, None, None
    actions, lastActionTime = None, None

    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.score = self.deaths = self.kills = 0
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
        self.view = np.repeat("*", h * w).reshape(h, w)
        self.view[1:-1, 1:-1] = " "
        self.update_view()

        self.actions = deque()
        self.lastActionTime = 0

        self.health = health
        self.ammo = ammo

        for player in self.game.players.itervalues():
            player.ammo += 5

    def update_view(self):
        view, arena = self.view, self.game.arena

        if arena[self.pos] == "*":
            raise excpt.HittingAWall()

        for c in "<>v^:o":
            view[view == c] = " "

        h, w = arena.shape
        y, x = self.pos

        stopper = np.zeros(shape=view.shape, dtype=bool)
        for c in "<>v^*":
            stopper += (arena == c)

        def _update_view(y, x):
            stop = stopper[y, x].cumsum(dtype=np.int8) > 0
            # we want the first 1 to be visible, but not all the rest
            # e.g. [0,0,0,1,1,1,...] -> [F,F,F,F,T,T,...]
            stop = stop.cumsum() > 1

            def _update(y, x):
                view[y, x] = np.where(stop, view[y, x], arena[y, x])
            _update(y, x)

            # do one above and one below
            if isinstance(x, slice):
                _update(y + 1, x)
                _update(y - 1, x)
            elif isinstance(y, slice):
                _update(y, x - 1)
                _update(y, x + 1)

        if self.facing != "^":
            _update_view(slice(y + 1, None, None), x)
        if self.facing != "v":
            _update_view(slice(y - 1, None, -1), x)
        if self.facing != "<":
            _update_view(y, slice(x + 1, None, None))
        if self.facing != ">":
            _update_view(y, slice(x - 1, None, -1))

        # See everything immediately around you
        view[y-1: y+2, x-1: x+2] = arena[y-1: y+2, x-1: x+2]

        # Scan for other player's locations
        if self.scan:
            for player in self.game.players.itervalues():
                if not player.cloak:
                    self.view[player.pos] = self.game.arena[player.pos]

    def queue(self, action, *args, **kwargs):
        if len(self.actions) > 5:       # only queue 5 actions at a time
            self.actions.popleft()
        self.actions.append((action, args, kwargs))

    def update_action(self):
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

    def move(self, direction):
        self.game.arena[self.pos] = ' '

        if self.cloak:
            if self.ammo >= self.game.settings.ammo["cloak"]:
                self.ammo -= self.game.settings.ammo["cloak"]
            else:
                self.cloak = False
                self.msg = "Not enough ammo for cloaking"
        else:
            for player in self.game.players.itervalues():
                if player.scan and player is not self:
                    if player.ammo >= self.game.settings.ammo["scan"]:
                        player.ammo -= self.game.settings.ammo["scan"]
                    else:
                        player.scan = False
                        player.msg = "Not enough ammo for scanning"

        p = move(self.pos, direction)
        if self.game.in_arena(p):
            if self.game.arena[p] == " ":
                self.pos = p
            if self.game.arena[p] == "A":
                self.ammo += self.game.settings.ammo["recharge"]
                self.pos = p
            elif self.game.arena[p] in "<>v^" and direction == self.facing:
                # if we're facing someone and move into them, stab
                other = self.game.find_player(p)
                other.hit(self, "stab")

        self.game.arena[self.pos] = self.facing
        self.update_view()

    def turn(self, direction):
        self.facing = direction
        self.update_view()
        self.game.arena[self.pos] = self.facing

    def fire(self, type):
        if self.ammo >= self.game.settings.ammo[type]:
            proj = Projectile(self.pos, self.facing, self, type)
            self.ammo -= self.game.settings.ammo[type]
            self.game.update_projectile(proj)
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

                src.health += 2
                src.kills += 1
                self.deaths += 1

                self.score -= 1
                src.score += 1

                self.game.arena[self.pos] = " "
                self.rebirth()

    def update_score(self):
        self.score = 0.9998 * self.score

    def __str__(self):
        h, w = self.view.shape
        s = "\n".join("".join(self.view[y, x]
                              for x in xrange(w))
                      for y in xrange(h))
        return s

    def to_json(self):
        d = {"arena": str(self), "ammo": self.ammo, "health": self.health,
             "x": self.pos.x, "y": self.pos.y, "cloak": self.cloak,
             "scan": self.scan}
        if self.msg is not None:
            d["msg"] = self.msg

        return d
