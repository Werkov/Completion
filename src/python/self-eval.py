#!/usr/bin/env python3

import argparse
import common.configuration
import evaluation.testing
import evaluation.metrics

def main():
    # initialize own parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="file with test text", type=argparse.FileType('r'), metavar="file", dest="file", required=True)
    # append subparsers for configuration parameters
    subparsers = parser.add_subparsers(title='Configurations', metavar="CONFIGURATION")
    common.configuration.fillSubparsers(subparsers)

    # create configuration
    args = parser.parse_args()
    common.configuration.createFromArgs(args)
        
    test = evaluation.testing.AutomatedTest(args.file, common.configuration.current)

    test.metrics.append(evaluation.metrics.Metric(common.configuration.current))
    test.metrics.append(evaluation.metrics.PerplexityMetric(common.configuration.current))
    test.metrics.append(evaluation.metrics.QwertyMetric(common.configuration.current))
#    test.metrics.append(evaluation.metrics.SelectorMetric(common.configuration.current))

    
    test.runTest()
    test.result()
    

if __name__ == '__main__':
    main()

