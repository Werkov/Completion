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
    parser.add_argument("-u", "--unknown", help="add unknown token\t[%(default)s]", action='store_true', default=False)
    parser.add_argument("-d", "--discount", help="discounting method (none, Good-Turing, constant discount)\t[%(default)s]",
                        choices=['no', 'const', 'GT'], default='GT')
    parser.add_argument("-cd", "--cdiscount", help="constant to discount for const method\t[%(default)s]",
                        type=float, default=0.5)

    parser.add_argument("textfile", help="text file", type=argparse.FileType('r'))
    parser.add_argument("ARPAfile", help="ARPA output file", type=argparse.FileType('w'))
    args = parser.parse_args()

    abbreviations = set()
    if args.a:
        abbreviations = set(w.strip() for w in args.a.readlines())
        args.a.close()


    # tokenize
    tft = common.tokenize.TextFileTokenizer(args.textfile)
    sent = common.tokenize.SentenceTokenizer(tft, abbreviations=abbreviations)
    normalizer = common.tokenize.TokenNormalizer(sent)
    counter = lm.probability.NgramCounter(args.order)

    # count ngrams
    for token in normalizer:
        if token == common.tokenize.TOKEN_BEG_SENTENCE:
            counter.resetContext()
            counter.shift(token)
        else:
            counter.append(token)
    args.textfile.close()
    
    
    # train backoff model    
    countsOfCounts = lm.probability.CountsOfCounts(counter)
    discounts = {}
    for order, CoC in countsOfCounts.items():
        if args.discount == 'GT':
            # SRI LM default values
            gtMin = 1 if order <= 2 else 2
            gtMax = 1 if order <= 1 else 7

            discounts[order] = lm.probability.GoodTuringDiscount(CoC, gtMax=gtMax, gtMin=gtMin)
        elif args.discount == 'const':
            discounts[order] = lm.probability.AbsoluteDiscount(args.cdiscount)
        else:
            discounts[order] = lm.probability.NoDiscount()

    # write
    model = learning.backoff.BackoffModel(counter, args.unknown, args.order, discounts)
    model.dumpToARPA(args.ARPAfile)
    args.ARPAfile.close()

    

if __name__ == '__main__':
    main()



