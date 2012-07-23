#!/usr/bin/env python3

import argparse
import datetime
import configparser

import common.configuration
from common import pathFinder
import evaluation.testing
import evaluation.metrics

def main():
    # initialize own parser
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", help="file(s) with test text", type=argparse.FileType('r'), dest="files", metavar="file", nargs='+')
    group.add_argument("-l", help="list of test text files, one per line, searched also in TESTPATH", type=argparse.FileType('r'), dest="list", metavar="listfile")
    parser.add_argument("-i", help="INI file\t[%(default)s]", type=argparse.FileType('r'), default='lmconfig.ini', dest='inifile')
        
    # append subparsers for configuration parameters
    common.configuration.updateParser(parser)

    # create configuration
    args = parser.parse_args()
    iniParser = configparser.ConfigParser()
    iniParser.read_file(args.inifile)
    common.configuration.createFromParams(args, iniParser)
    args.inifile.close()

    if args.list:
        files = [open(pathFinder(f.strip(), 'TESTPATH'), 'r') for f in args.list]
    else:
        files = args.files

    tests = [evaluation.testing.TextFileTest(file, common.configuration.current) for file in files]
    test = evaluation.testing.MultiTest(common.configuration.current, tests)
    

    test.metrics.append(evaluation.metrics.Metric(common.configuration.current))
    test.metrics.append(evaluation.metrics.PerplexityMetric(common.configuration.current))
    test.metrics.append(evaluation.metrics.QwertyMetric(common.configuration.current))
    #test.metrics.append(evaluation.metrics.SelectorMetric(common.configuration.current))

    
    
    startTime = datetime.datetime.now()
    print('# Start at {}'.format(startTime))
    print(common.configuration.current)
    test.printHeader()
    test.runTest()
    test.printResult()
    endTime = datetime.datetime.now()
    print('# End at {}'.format(endTime))
    print('# Took {}'.format(endTime - startTime))
    

if __name__ == '__main__':
    main()

