import common.tokenize

class AutomatedTest:
    def __init__(self, file, config):
        self._file = file
        self._config = config
        self.metrics = []

    def runTest(self):
        for m in self.metrics:
            m.reset()
        self._config.contextHandler.reset()

        tokenizer = self._config.textFileTokenizerClass(self._file)
        sentences = self._config.sentenceTokenizer
        sentences.reset(tokenizer)
        tokens = common.tokenize.TokenNormalizer(sentences)

        for token in tokens:
            if token != common.tokenize.TOKEN_BEG_SENTENCE:
                for metric in self.metrics:
                    metric.measure(token)
            self._config.contextHandler.shift(token)
            

    def result(self):        
        print("\t\t".join(['#' + ' '*(len(self._file.name)-1)] + [str(m.name) for m in self.metrics]))
        row = []
        for m in self.metrics:
            results = []
            for r in m.result():
                if isinstance(r, float):
                    results.append("{:.3f}".format(r))
                else:
                    results.append(str(r))
            row.append(' '.join(results))
            
        print("\t\t".join([self._file.name] + row))