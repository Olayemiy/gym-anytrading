import sys
from collections import deque

class Running_Z_Score():
    def __init__(self, mode = "min-max", period = 96):
        self.mode = mode
        self.period = period
        self.buffer = deque(maxlen = self.period)
        self.min = sys.maxsize
        self.max = -sys.maxsize

    def norm(self, val):
        return self.min_max(val) if(self.mode == "min-max") else self.z_score(val)

    def min_max(self, val): #not  optimized runtime
        self.buffer.append(val)
        self.min = sys.maxsize
        self.max = -sys.maxsize
        for x in self.buffer:
            self.min = min(self.min, x)
            self.max = max(self.max, x)

        return (val-self.min)/(self.max-self.min) if ((self.max - self.min) != 0) else 0

    #z-score formula = (val- mean)/(std deviation)
    def z_score(self, val):
        raise NotImplementedError
        
import multiprocessing as mp

num_workers = mp.cpu_count()  
print(num_workers)