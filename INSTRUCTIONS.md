Instructions (for real)
=========

Hunt is a maze-based multiplayer game. You move around the maze and try to find and kill other players with bullets, bombs, and stabs. The entire maze is not visible: as you move around the maze, you will see 

Controls
----
Movement is with VIM controls:

  - `h` move left 
  - `j` move down
  - `k` move up
  - `l` move right

To turn, press shift and the direction key you want to turn

  - `Shift`-`H` face left 
  - `Shift`-`J` face down
  - `Shift`-`K` face up
  - `Shift`-`L` face right

`f` fires a bullet, and `Shift`-`F` fires a bomb. To stab, face another player's cursor and move in their direction.

There are two special options: scanning and cloaking. When scanning, you can see all other uncloaked players. Cloak means that you're unable to be scanned.

  - `c` toggle cloak on/off
  - `s` toggle scanning on/off

Symbols on Screen
---
  - `+|-` walls
  - `:` bullets
  - `o` bomb
  - `<>v^` player cursor, depending on which direction you're facing: left, right, down, or up respectively. Your cursor will be highlighted.
  - `A` ammo pickup

Bomb explosions are rendered as:

```
\|/
-*-
/|\
```

Damage & Ammo
----
  - **Bullets**: Bullets take 1 ammo to shoot, move the direction you are facing, and deal 5 damage if they hit a player. If they hit a wall, they destroy the wall.
  - **Bombs**: Bombs take 5 ammo to shoot and detonates when it hits a wall or a player. On detonation, bomb hits everything in a 3x3 square centered on the bomb, destroying all walls and dealing 10 damage to players (including yourself)
  - **Stabbing**: Stabbing takes no ammo and deals 2 damage. To stab, face another player's cursor and move in their direction.
  - **Ammo pickup**: Gives you 5 additional ammo
  - **Cloaking**: Cloaking takes 0.05 ammo per move.
  - **Scanning**: Scanning takes 0.05 ammo per other uncloaked player's move.

Misc.
----
  - Scores are based on kills and deaths. Kills give you one point, deaths subtract a point, and suicides subtract 5. Scores exponentially decay through time.
  - Bullets/bombs move 5 times faster than you do
  - There is one ammo pickup per player at all times. As soon as you pick up some ammo, another pickup appears somewhere else.
  - You can't see behind you. Turn around to get maximum vision.
  - You're born with 10 health and 15 ammo. Every time another player enters the arena, you gain 5 ammo.
  - Walls eventually regenerate in the order that they are destroyed.
