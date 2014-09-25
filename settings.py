from collections import namedtuple

Settings = namedtuple("Settings", ["w", "h", "pace", "speed", "damage"])

default = Settings(w=51, h=23, pace=2,
                   speed={"move": 5, "fire": 1, "turn": 1},
                   damage={"bullet": 5, "stab": 2})
