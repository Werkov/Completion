from math import log

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
#        if prob == 0:
#            self.entropy += float("inf")
#        else:
#            self.entropy += -log(prob, 2)

        self.tokenCnt += 1

    def result(self):
        entropyPerToken = self.entropy / self.tokenCnt
        return 2 ** entropyPerToken

class QwertyMetric:
    pass
class BikeyboardMetric:
    pass
class SuggesitionsMetric:
    pass


