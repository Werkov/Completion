#!/usr/bin/python3
from evaluation.Metrics import QwertyMetric
import sys

from common.Configuration import ConfigurationBuilder
from evaluation.Testing import AutomatedTest
from evaluation.Metrics import *

configBuilder = ConfigurationBuilder()

if len(sys.argv) < 3:
    print("Usage: {} config-name test-file(s)".format(sys.argv[0]))
    sys.exit(1)

for filename in sys.argv[2:]:
    config  = configBuilder[sys.argv[1]]
    test    = AutomatedTest(open(filename))

    test.metrics.append(EntropyMetric(config.sorter.languageModel, config.contextLength))
    test.metrics.append(SuggesitionsMetric(config.selector, config.sorter, config.contextLength))
    test.metrics.append(QwertyMetric(config.selector, config.sorter, config.filter, config.contextLength))
    test.runTest()
    test.result()
