#!/usr/bin/python3
#from evaluation.Metrics import QwertyMetric
#import sys
#
#from common.Configuration import ConfigurationBuilder
#from evaluation.Testing import AutomatedTest
#from evaluation.Metrics import *
#
#configBuilder = ConfigurationBuilder()
#
#if len(sys.argv) < 3:
#    print("Usage: {} config-name test-file(s)".format(sys.argv[0]))
#    sys.exit(1)
#
#for filename in sys.argv[2:]:
#    config  = configBuilder[sys.argv[1]]
#    test    = AutomatedTest(open(filename))
#
#    test.metrics.append(EntropyMetric(config.sorter.languageModel, config.contextLength))
#    test.metrics.append(SuggesitionsMetric(config.selector, config.sorter, config.contextLength))
#    test.metrics.append(QwertyMetric(config.selector, config.sorter, config.filter, config.contextLength))
#    test.runTest()
#    test.result()

import argparse
import common.configuration
import evaluation.Testing
import evaluation.Metrics

#
#        config = common.configuration.current
#
#        self.txtMain                = ui.Completion.TextEdit(self)
#        self.txtMain.selector       = config.selector
#        self.txtMain.contextHandler = config.contextHandler
#
#        for filter in config.filterChain:
#            self.txtMain.addFilter(filter)
#
    

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
    test.metrics.append(evaluation.Metrics.SelectorMetric(common.configuration.current))

    
    test.runTest()
    test.result()
    

if __name__ == '__main__':
    main()

