#!/usr/bin/env python3

import argparse
import common.configuration
import evaluation.Testing
import evaluation.Metrics

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
        
    test = evaluation.Testing.AutomatedTest(args.file, common.configuration.current)

    test.metrics.append(evaluation.Metrics.Metric(common.configuration.current))
    test.metrics.append(evaluation.Metrics.PerplexityMetric(common.configuration.current))
    test.metrics.append(evaluation.Metrics.QwertyMetric(common.configuration.current))
#    test.metrics.append(evaluation.Metrics.SelectorMetric(common.configuration.current))

    
    test.runTest()
    test.result()
    

if __name__ == '__main__':
    main()

