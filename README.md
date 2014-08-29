Hunt
==========
Trying to implement the hunt terminal game online.

Plan to use Python backend and coffee/javascript frontend.
Flask and Socket-IO to connect them (maybe we should
use Node.js?)

# Usage
On a system with only python2.7 just run:

```python server.py```

Otherwise you need to deliberately use python2.7, so run:

```python2 server.py```

# Prereqs:
### Python 2.7
- - -
  Install the python dependencies with [pip](http://pip.readthedocs.org/en/latest/installing.html), or your preferred method.

  - **numpy**          -- Arrays for fast & easy arena implementation
  - **flask**          -- Lightweight web framework
  - **flask-socketio** -- Bridge between flask and Socket-IO
    - gevent           -- Lightweight asyncs and greenlets 
    - gevent-socketio
    

### Coffeescript
- - -
### Javascript
- - -
  - **Bootstrap** --  Easy site layout. Work on frontend later
  - **JQuery**    --  Required by bootstrap
  - **Socket-IO** --  Continued communication w/ server
    
# Description - from terminal man page
The object of the game Hunt is to kill off the other players.  There are
no rooms, no treasures, and no monsters.  Instead, you wander around a
maze, find grenades, trip mines, and shoot down walls and players. The
more players you kill before you die, the better your score is.

# Instructions - from terminal man page
Hunt uses the same keys to move as vi(1) does, i.e., h, j, k, and l for
left, down, up, right respectively.  To change which direction you're
facing in the maze, use the upper case version of the movement key (i.e.,
HJKL).  You can only fire or throw things in the direction you're facing.
Other commands are:

- [ ] f or 1   Fire a bullet (Takes 1 charge)

- [ ] g or 2   Throw grenade (Takes 9 charges)

- [ ] F or 3   Throw satchel charge (Takes 25 charges)

- [ ] G or 4   Throw bomb (Takes 49 charges)

- [ ] 5        Throw big bomb (Takes 81 charges)

- [ ] 6        Throw even bigger bomb (Takes 121 charges)

- [ ] 7        Throw even more big bomb (Takes 169 charges)

- [ ] 8        Throw even more bigger bomb (Takes 225 charges)

- [ ] 9        Throw very big bomb (Takes 289 charges)

- [ ] 0        Throw very, very big bomb (Takes 361 charges)

- [ ] @        Throw biggest bomb (Takes 441 charges)

- [ ] o        Throw small slime (Takes 5 charges)

- [ ] O        Throw big slime (Takes 10 charges)

- [ ] p        Throw bigger slime (Takes 15 charges)

- [ ] P        Throw biggest slime (Takes 20 charges)

- [ ] s        Scan (show where other players are) (Takes 1 charge)

- [ ] c        Cloak (hide from scanners) (Takes 1 charge)

- [ ] The symbols on the screen are:
```
      -|+    walls
      /\     diagonal (deflecting) walls
      #      doors (dispersion walls)
      ;      small mine
      g      large mine
      :      bullet
      o      grenade
      O      satchel charge
      @      bomb
      s      small slime
      $      big slime
      ><^v   you facing right, left, up, or down
      }{i!   other players facing right, left, up, or down
      *      explosion
      \|/
      -*-    grenade and large mine explosion
      /|\
```
## Other helpful hints:
  - [ ] You can only fire in the direction you are facing.

  - [ ] You can only fire three shots in a row, then the gun must cool off.

  - [ ] Shots move 5 times faster than you do.

  - [ ] To stab someone, you face that player and move at them.

  - [ ] Stabbing does 2 points worth of damage and shooting does 5 points.

  - [ ] Slime does 5 points of damage each time it hits.

  - [ ] You start with 15 charges and get 5 more every time a player enters
    or re-enters.

  - [ ] Grenade explosions cover a 3 by 3 area, each larger bomb cover a cor‐
    respondingly larger area (ranging from 5 by 5 to 21 by 21).  All
    explosions are centered around the square the shot hits and do the
    most damage in the center.

  - [ ] Slime affects all squares it oozes over.  The number of squares is
    equal to the number of charges used.

  - [ ] One small mine and one large mine is placed in the maze for every new
    player.  A mine has a 2% probability of tripping when you walk for‐
    ward on to it; 50% when going sideways; 95% when backing up.  Trip‐
    ping a mine costs you 5 points or 10 points respectively.  Defusing a
    mine is worth 1 charge or 9 charges respectively.

  - [ ] You cannot see behind you.

  - [ ] Cloaking consumes 1 ammo charge per 20 of your moves.

  - [ ] Scanning consumes 1 ammo charge per (20 × the number of players) of
    other player moves.

  - [ ] Turning on cloaking turns off scanning — turning on scanning turns
    off cloaking.

  - [ ] When you kill someone, you get 2 more damage capacity points and 2
    damage points get taken away.

  - [ ] Maximum typeahead is 5 characters.

  - [ ] A shot destroys normal (i.e., non-diagonal, non-door) walls.

  - [ ] Diagonal walls deflect shots and change orientation.

  - [ ] Doors disperse shots in random directions (up, down, left, right).

  - [ ] Diagonal walls and doors cannot be destroyed by direct shots but may
    be destroyed by an adjacent grenade explosion.

  - [ ] Slime goes around walls, not through them.

  - [ ] Walls regenerate, reappearing in the order they were destroyed.  One
    percent of the regenerated walls will be diagonal walls or doors.
    When a wall is generated directly beneath a player, he is thrown in a
    random direction for a random period of time.  When he lands, he sus‐
    tains damage (up to 20 percent of the amount of damage already sus‐
    tained); i.e., the less damage he had, the more nimble he is and
    therefore less likely to hurt himself on landing.

  - [ ] Every 30 deaths or so, a “?” will appear.  It is a wandering bomb
    which will explode when it hits someone, or when it is slimed.

  - [ ] If no one moves, everything stands still.

  - [ ] It's a boring game if you're the only one playing.

Your score is the decayed average of the ratio of number of kills to num‐
ber of times you entered the game and is only kept for the duration of a
single session of Hunt.

Hunt normally drives up the load average to be approximately (# of players + 0.5) greater than it would be without a Hunt game executing.
