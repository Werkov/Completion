#!/usr/bin/env python3

import sys
import argparse
import datetime
import configparser

import common.configuration
import common.tokenize
import lm.model

def main():
    # initialize own parser
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("file", help="file with training text", type=argparse.FileType('r'))
    parser.add_argument("-i", help="INI file\t[%(default)s]", type=argparse.FileType('r'), default='lmconfig.ini', dest='inifile')
    parser.add_argument("-d", help="relative entropy change to stop EM\t[%(default)s]", type=float, default=1e-3)
    parser.add_argument("-s", help="maximum no. of iterations\t[%(default)s]", type=int, default=20)

    # append subparsers for configuration parameters
    common.configuration.updateParser(parser)

    # create configuration
    args = parser.parse_args()
    iniParser = configparser.ConfigParser()
    iniParser.read_file(args.inifile)
    common.configuration.createFromParams(args, iniParser)
    args.inifile.close()

    model = common.configuration.current.languageModel
    if not isinstance(model, lm.model.LInterpolatedModel):
        print("Loaded configuration doesn't have interpolated model.", file=sys.stderr)
        sys.exit(1)

    tokenizer = common.configuration.current.textFileTokenizerClass(args.file)
    sentences = common.configuration.current.sentenceTokenizer
    sentences.reset(tokenizer)
    tokens = common.tokenize.TokenNormalizer(sentences)

    startTime = datetime.datetime.now()
    print('# Start at {}'.format(startTime))
    print(common.configuration.current)
    print('# Model weight order is main, (user), cached.')

    model.optimizeWeights(tokens, args.d, args.s, sys.stdout)
    
    args.file.close()
    endTime = datetime.datetime.now()
    print('# End at {}'.format(endTime))
    print('# Took {}'.format(endTime - startTime))


if __name__ == '__main__':
    main()

