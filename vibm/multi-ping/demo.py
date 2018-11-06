#!/usr/bin/env python

import os
from elevate import elevate

from multiping import MultiPing
from multiping import multi_ping

if __name__ == "__main__":
    elevate() 
    
    # A list of addresses and names, which should be pinged.
    addrs = ["8.8.8.8", "cnn.com", "127.0.0.1", "youtube.com", "2001:4860:4860::8888"]

    print("Sending one round of pings and checking twice for responses")

    mp = MultiPing(addrs)

    mp.send()

    # First attempt: We probably will only have received responses from
    # localhost so far. Note: 0.01 seconds is usually a very unrealistic 
    # timeout value.
    # 1 second may be more useful in a real world example.
    responses, no_responses = mp.receive(0.01)