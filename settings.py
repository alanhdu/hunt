from collections import namedtuple

Settings = namedtuple("Settings", ["w", "h", "pace", "speed", "damage", "ammo"])

default = Settings(w=50, h=25, pace=2,
                   speed={"move": 5, "fire": 1, "turn": 1},
                   damage={"bullet": 5, "stab": 2, "bomb": 10},
                   ammo={"bomb" : 5, "bullet":1})
