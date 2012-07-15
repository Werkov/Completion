# TODO implement API for trigger based model also here
#      possibly accept whole Configuration object

class EntropyMetric:
    """Cross entropy per (word) token for model on given text."""
    def __init__(self, languageModel, contextLength):
        self.languageModel  = languageModel
        self.entropy        = 0
        self.tokenCnt       = 0
        self.contextLength  = contextLength

    def measure(self, history, token):
        context = history[-self.contextLength:]
        prob = self.languageModel.probability(context, token)
        self.entropy  += -prob
        self.tokenCnt += 1

    def result(self):
        entropyPerToken = self.entropy / self.tokenCnt
        return 2 ** entropyPerToken

class QwertyMetric:
    """Emulates optimal typing on classical keyboard (full QWERTY-like layout).
    Neglects congition load caused by selections list. As metrics get only tokens
    from the text, suppose that they're separated with single space.
    TODO Partial suggestions support."""
    
    def __init__(self, selector, sorter, filter, contextLength):
        self.selector       = selector
        self.sorter         = sorter
        self.filter         = filter
        self.contextLength  = contextLength
        self.tokenCnt       = 0
        self.charCnt        = 0
        self.keystrokeCnt   = 0

    def measure(self, history, token):
        context = history[-self.contextLength:]
        keystrokes = 0 # per token
        prefix = ""
        for c in token:
            rawSuggestions = self.sorter.getSortedSuggestions(context, self.selector.getSuggestions(context, prefix))
            suggestions = [(suggestion, probability, False) for suggestion, probability in rawSuggestions]
            if self.filter != None:
                suggestions = self.filter.filter(suggestions, prefix)

            suggestionsOnly = [suggestion for suggestion, _, _ in suggestions]
            # TODO partial tokens!
            if token in suggestionsOnly:
                autoComplete = 1 if suggestions.index(token) == 1 else suggestions.index(token) + 1 # use fast accept for first position
                typeManually = len(token) - len(prefix) + 1 # write remaining chars + space
                keystrokes += min(autoComplete, typeManually)
                break
            else: # manual typing
                keystrokes += 1
            prefix += c
        else:
            keystrokes += 1 # separating space for manual typing

        self.charCnt += len(token) + 1 # with separating space
        self.keystrokeCnt += keystrokes
        self.tokenCnt += 1

    def result(self):
        return self.keystrokeCnt / self.charCnt

class BikeyboardMetric:
    pass

class SuggesitionsMetric:
    """Measure of selector effeciency. Suggestions are evaluated by their position. Missing suggestions are penalised."""
    missingPenalty = 1000

    def __init__(self, selector, sorter, contextLength):
        self.selector       = selector
        self.sorter         = sorter
        self.contextLength  = contextLength
        self.tokenCnt       = 0
        self.aggOrder       = 0
    
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

