#!/usr/bin/python3

from itertools import chain, tee
from collections import Counter
import argparse
import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
import common.Tokenize


class DataCollector:
    total           = Counter() # total occurencies of token
    followedDot     = Counter() # occurencies followed by dot
    followedDotCap  = Counter() # occurencies followed by dot followed by Capital letter
    length          = 0         # all tokens

    dot = "."

    @staticmethod
    def normalize(token):
        return token[0] if token[1] != common.Tokenize.TYPE_NUMBER else common.Tokenize.TOKEN_NUMERIC



    def statsForFile(self, fin):
        """Simple ngram stats for file"""
        # Create N copies of iterator shifted in order to window represent current token
        # and N-1 preceding. Current token is last.
        tokens = common.Tokenize.TextFileTokenizer(fin)
        N = 2
        streams = [chain([None] * (N-n-1), it) for n, it in enumerate(tee(tokens, N))]
        lastFollowedDot = None
        for window in zip(*streams):
            current = DataCollector.normalize(window[-1])
            prev = DataCollector.normalize(window[-2]) if window[-2] else None
            if current == self.dot:
                self.followedDot[prev] += 1
                lastFollowedDot = prev
            if current[0].isupper() and lastFollowedDot:
                self.followedDotCap[lastFollowedDot] += 1
            if window[-1][1] != common.Tokenize.TYPE_DELIMITER:
                lastFollowedDot = None
            self.total[current] += 1
            self.length += 1

    def process(self, params):
        """Process collected data and returns list of abbreviations."""
        result = []
        for token in self.followedDot:
            if self.followedDot[token] < int(self.length / params.f) or len(token) > params.l:
                continue
            if (self.followedDot[token] / self.total[token]) >= params.dt:
                result.append(token)
            elif 1 - self.followedDotCap[token] / self.followedDot[token] >= params.ct:
                result.append(token)
                
        return result


def main():
    parser = argparse.ArgumentParser(description="Prints words that are probably abbreviations in given text files.")
    parser.add_argument("-dt", help="frequency of occurencies followed by a dot\t[%(default)s]", type=float, default=0.8)
    parser.add_argument("-ct", help="frequency of occurencies followed by a dot followed by capital letter\t[%(default)s]", type=float, default=0.5)
    parser.add_argument("-l", help="maximal length of an abbreviation\t[%(default)s]", type=int, default=5)
    parser.add_argument("-f", help="frequency of occurencies of an abbreviation, reciprocal value\t[%(default)s]", type=int, default=10000)
    parser.add_argument("file", help="text file", type=argparse.FileType('r'), nargs='+')

    args = parser.parse_args()
    dc = DataCollector()

    for f in args.file:
        dc.statsForFile(f)
        f.close()

    print("Processed {} tokens.".format(dc.length), file=sys.stderr)

    for abbr in dc.process(args):
        print(abbr)
    

if __name__ == '__main__':
    main()


    
    


