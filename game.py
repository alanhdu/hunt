import numpy as np

class Arena(object):
    def __init__(self, w=64, h=48, density=0.5):
        self.maze = np.random.rand(h, w) < density

        for i in xrange(100):   # 100 interations of Rule 12345/3
            n = self._numNeighbors()
            self.maze = (n == 3) + ( (n > 0) * (n < 6) * self.maze)
    def _numNeighbors(self):
        x, y = self.maze.shape
        m = np.zeros( (x+2, y+2) )
        m[1:-1, 1:-1] = self.maze.astype(int)
        return (m[:-2,  :-2] + m[:-2, 1:-1] + m[:-2,  2:] + 
                m[1:-1, :-2] + m[1:-1,1:-1] + m[1:-1, 2:] +
                m[2:,   :-2] + m[2:,  1:-1] + m[2:,  :-2])

    def __str__(self):
        s = "\n".join("".join("*" if x else " "
                              for x in y)
                      for y in self.maze)
        return s

