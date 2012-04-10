class EntropyMetric:
    def __init__(self, languageModel, contextLength):
        self.languageModel = languageModel
        self.entropy = 0
        self.tokenCnt = 0
        self.contextLength = contextLength

    def measure(self, history, token):
        context = history[-self.contextLength:]
        prob = self.languageModel.probability(context, token)
        self.entropy += -prob
        self.tokenCnt += 1

    def result(self):
        entropyPerToken = self.entropy / self.tokenCnt
        return 2 ** entropyPerToken

class QwertyMetric:
    pass
class BikeyboardMetric:
    pass

class SuggesitionsMetric:
    missingPenalty = 1000

    def __init__(self, selector, sorter, contextLength):
        self.selector = selector
        self.sorter = sorter
        self.contextLength = contextLength
        self.tokenCnt = 0
        self.aggOrder = 0
    
    def measure(self, history, token):
        context = history[-self.contextLength:]
        suggestions = [suggestion for suggestion, _ in self.sorter.getSortedSuggestions(context, self.selector.getSuggestions(context))]
        if token in suggestions:
            self.aggOrder += suggestions.index(token)
        else:
            self.aggOrder += self.missingPenalty
        self.tokenCnt += 1

    def result(self):
        return self.aggOrder / self.tokenCnt

