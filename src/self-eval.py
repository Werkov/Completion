import sys

from common.Configuration import ConfigurationBuilder
from evaluation.Testing import AutomatedTest
from evaluation.Metrics import EntropyMetric

configBuilder = ConfigurationBuilder()

if len(sys.argv) < 3:
    print("Usage: {} config-name test-file".format(sys.argv[0]))
    sys.exit(1)

config  = configBuilder[sys.argv[1]]
test    = AutomatedTest(open(sys.argv[2]))

test.metrics.append(EntropyMetric(config.sorter.languageModel, config.contextLength))
test.runTest()
test.result()
