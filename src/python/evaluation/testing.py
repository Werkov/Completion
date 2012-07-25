import sys
import common.tokenize
from evaluation import *

class AutomatedTest:
    metrics = []
    colPadding = 3

    def printResult(self, data=None, comment=False):
        if not data:
            data = self.result()
        headerWidths = []
        formats = []
        row = []
        for m in self.metrics:
            headerWidths.extend([len(r) for r in m.resultHeader()])
            formats.extend(m.resultFormat())

        for val, length, format in zip(data, headerWidths, formats):
            if not format:
                if isinstance(val, float):
                    format = "{:" + str(length + self.colPadding) + ".4g}"
                elif isinstance(val, int):
                    format = "{:" + str(length + self.colPadding) + "d}"
                else:
                    format = "{:" + str(length + self.colPadding) + "s}"
                    val = str(val)[:length]
            
            row.append(format.format(val))

        print(('#' if comment else ' ') + '\t'.join(row))

    def printHeader(self):
        row = []
        for m in self.metrics:
            for h in m.resultHeader():
                row.append(' ' * self.colPadding + h)
        print('#' + '\t'.join(row))

class TextFileTest(AutomatedTest):
    """Measure multiple metrics on given file.
    Metrics are be stored in (public) `metrics` attribute.
    """
    def __init__(self, file, configuration):
        self._file = file
        self._configuration = configuration
    

    def runTest(self):
        for m in self.metrics:
            m.reset()
        self._configuration.contextHandler.reset()
        self._resultCache = None

        tokenizer = self._configuration.textFileTokenizerClass(self._file)
        sentences = self._configuration.sentenceTokenizer
        sentences.reset(tokenizer)
        tokens = common.tokenize.TokenNormalizer(sentences)
        self._configuration.capitalizeFilter.enabled = False

        for token in tokens:
            if token != common.tokenize.TOKEN_BEG_SENTENCE:
                for metric in self.metrics:
                    self._configuration.contextHandler.prefix = ""
                    metric.measure(token)
            self._configuration.contextHandler.shift(token)
            self._configuration.suggestionCache.clear() # invalidate sugesstions cache

        for m in self.metrics:
            m.finish()
            
    def result(self):
        """Return list with concatenated results from all metrics; order is given
        by order of metrics in `metrics` list.
        """
        if not self._resultCache:
            self._resultCache = []
            for m in self.metrics:
                self._resultCache += m.result()
        return self._resultCache

    def printResult(self):
        print('# ' + self._file.name)
        super().printResult()

class MultiTest(AutomatedTest):
    """Run multiple tests with given metrics.
    Mean values over all tests are results for individual metrics.
    """
    def __init__(self, configuration, tests=[], trace=sys.stderr):
        self._configuration = configuration
        self._tests = tests
        self._trace = trace

    def runTest(self):
        self._results = [] # list of result tuples from tests
        self._resultsTr = [] # transposed results, list for each element in resluts tuple

        if not self._tests:
            return

        for i, test in enumerate(self._tests, 1):
            test.metrics = self.metrics # share metrics, individual tests resets them
            test.runTest()
            print("Test {} of {} done.".format(i, len(self._tests)), file=self._trace)
            self._results.append(test.result())

        # transpose results
        for i in range(len(self._results[0])):
            column = []
            for result in self._results:
                column.append(result[i])
            self._resultsTr.append(column)

    def result(self):
        return self.mean()
        
    def mean(self):
        return [mean(column) for column in self._resultsTr]

    def variance(self):
        return [variance(column) for column in self._resultsTr]

    def printResult(self):
        for test in self._tests:
            test.printResult()
        print('# ----------')
        print('# mean')
        super().printResult(comment=True)
        print('# variance')
        super().printResult(self.variance(), comment=True)