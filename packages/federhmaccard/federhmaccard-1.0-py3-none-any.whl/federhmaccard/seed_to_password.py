#!/usr/bin/env python3

import hashlib
import base64


def seed2password(seed, length, AZ=True, az=True, num=True, special=True):
    if not seed: return None

    def randomness():
        x = seed
        while True:
            yield base64.b85encode(x).decode("ascii")
            x = hashlib.sha256(x).digest()

    assert length > 0
    result = ""

    if not (az or AZ or num or special):
        return ""

    rng = randomness()
    while len(result) < length:
        feed = next(rng)
        while feed != "":
            c = feed[0]
            feed = feed[1:]
            if az and c in "abcdefghijklmnopqrstuvwxyz":
                result += c
            if AZ and c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                result += c
            if num and c in "0123456789":
                result += c
            if special and c.lower() not in "0123456789abcdefghijklmnopqrstuvwxyz":
                result += c
           
    return result[:length]
