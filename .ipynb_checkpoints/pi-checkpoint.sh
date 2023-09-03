#!/usr/bin/env python3

"""
Pi spigot algorithm, source: https://gist.github.com/deeplook/4947835
Slightly modified by AA
:author: "Deeplook" (https://github.com/deeplook) and AA
:date: 2023-03-14
"""

import sys

def pi_digits(n):
    """
    Generates `n` digits of `pi`.
    :param n: The number of digits
    :return: an iterator with the digits of Pi.
    """
    
    k, a, b, a1, b1 = 2, 4, 1, 12, 4
    while n > 0:
        p, q, k = k * k, 2 * k + 1, k + 1
        a, b, a1, b1 = a1, b1, p * a + q * a1, p * b + q * b1
        d, d1 = a / b, a1 / b1
        while d == d1 and n > 0:
            yield int(d)
            n -= 1
            a, a1 = 10 * (a % b), 10 * (a1 % b1)
            d, d1 = a / b, a1 / b1

# == MAIN ==

if len(sys.argv) < 2:
    print("Usage: pi_digits.py <n> , where <n> is the number of digits of Pi")
    sys.exit(0)

dstr = "".join([ str(digit) for digit in pi_digits(int(sys.argv[1])) ])
dstr = dstr[0] + "." + dstr[1:]
print(dstr)
