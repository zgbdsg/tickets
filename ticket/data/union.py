import sys
import os

td = []
for line in sys.stdin:
    items = line.strip().split(',')
    if not items[1] in td:
        print line,
        td.append(items[1])
