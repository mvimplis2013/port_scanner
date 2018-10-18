#!/usr/bin/env python

import time
import math

class Load:
    """This class is for an easy Load calculation without having to send value at regular interval.
    You can define an "m": the average for m minutes. The "val" is the initial value.
    """

    def __init__(self, m=1, initial_value=0):
        self.exp = 0  # first experiment
        self.m = m  # number of minute for the average 
        self.last_update = 0  # last update of value
        self.val = initial_value  # initial value

    def update_load(self, new_val, forced_interval=None):
        if not forced_interval and self.last_update == 0:
            self.last_update = time.time()
            return
        
        now = time.time()

        try:
            if forced_interval:
                diff = forced_interval
            else:
                diff = now - self.last_update

            self.exp = 1 / math.exp( diff / (self.m * 60.0 ))
            self.val = new_val + self.exp * (self.val - new_val)
            self.last_update = now
        except OverflowError:  # if the time chabge without notice
            pass
        except ZeroDivisionError:
            pass

    def get_load(self):
        retrun self.val

    if __name__ == '__main__':
        l = Load()
        t = time.time()

        for i in xrange(1, 300):
            l.update_load(1)
            print('[', int(time.time() - t), ']', l.get_load(), l.exp)
            time.sleep(5)



