#!/usr/bin/env python3
from platform import architecture
from core import tld
import threading
import argparse

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--domain", help="Enter Doamin Target (target.com)", required=True)
        parser.add_argument("-t", "--thread", help="Enter Thread number", default=10, type=int)
        args = parser.parse_args()
        for i in range(args.thread):
            t1 = threading.Thread(target=tld.scanner, args=(args.domain,))
            t1.start()
            t1.join()
    except KeyboardInterrupt:
        exit()
if __name__ == '__main__':
    main()