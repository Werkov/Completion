#!/usr/bin/env python3

import sys
import argparse
import datetime
import configparser

import common
import common.configuration
import common.tokenize
import lm.model

def main():
    # initialize own parser
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="""\
        Estimate weights for linear iterpolated model using EM algorithm.
        Weights are written in a form of command line options to stdout.
        Stderr is used for estimating process.
        """)
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

    output = sys.stderr#common.DevNullFile()

    startTime = datetime.datetime.now()
    print('# Start at {}'.format(startTime), file=output)
    print('# Model weight order is main, (user), cached.', file=output)

    model.optimizeWeights(tokens, args.d, args.s, output)

    if len(model._weights) == 2:
        print("-mw {:.3g} -cw {:.3g}".format(model._weights[0], model._weights[1]))
    elif len(model._weights) == 3:
        print("-mw {:.3g} -uw {:.3g} -cw {:.3g}".format(model._weights[0], model._weights[1], model._weights[2]))
    else:
        print("Unsupported no. of model for commandlineoptions output.", file=output)

    
    args.file.close()
    endTime = datetime.datetime.now()
    print('# End at {}'.format(endTime), file=output)
    print('# Took {}'.format(endTime - startTime), file=output)
    print(common.configuration.current, file=output)



if __name__ == '__main__':
    main()

