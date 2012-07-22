#!/usr/bin/env python3
import math
import sys

import argparse
import os

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import common.tokenize
import learning.backoff
import lm.probability



def main():
    parser = argparse.ArgumentParser(description="Train backoff models from text.")
    parser.add_argument("-a", help="abbreviations file, one per line", type=argparse.FileType('r'))
    parser.add_argument("-o", "--order", help="order\t[%(default)s]", type=int, default=2)
    parser.add_argument("-u", "--unknown", help="omit unknown token\t[%(default)s]", action='store_false', default=False)

    parser.add_argument("textfile", help="text file", type=argparse.FileType('r'))
    parser.add_argument("ARPAfile", help="ARPA output file", type=argparse.FileType('w'))
    args = parser.parse_args()

    abbreviations = set()
    if args.a:
        abbreviations = set(w.strip() for w in args.a.readlines())
        args.a.close()

    order = args.order

    tft = common.tokenize.TextFileTokenizer(args.textfile)
    sent = common.tokenize.SentenceTokenizer(tft, abbreviations=abbreviations)
    normalizer = common.tokenize.TokenNormalizer(sent)
    counter = lm.probability.NgramCounter(order)

    for token in normalizer:
        if token == common.tokenize.TOKEN_BEG_SENTENCE:
            counter.nullContext()
            counter.shift(token)
        else:
            counter.append(token)
    args.textfile.close()

    model = learning.backoff.BackoffModel(counter, not args.unknown, args.order)
    model.dumpToARPA(args.ARPAfile)
    args.ARPAfile.close()

    

if __name__ == '__main__':
    main()



