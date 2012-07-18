import common.Tokenize

class Metric:
    """Metric class has its own state. It could be changed by `measure` method
    that's called for every input token. Metric results (tuple for given state)
    are returned by `result` method. `reset` will put metric into initial state.
    
    IMPORTANT: Metric must not change the state of used objects.
    """
    name = "tokens"
    
    def __init__(self, config):
        self._config = config
        self.reset()

    def reset(self):
        self._n = 0
        self._c = 0

    def measure(self, token):
        self._n += 1
        self._c += len(token) + 1
    
    def result(self):
        return self._n,

    def _suggestions(self, prefix = ""):
        ll = self._config.selector.suggestions(prefix)
        for filter in self._config.filterChain:
            ll = filter(ll)
        return list(ll)



class PerplexityMetric(Metric):
    """Cross entropy per (word) token for model on given text."""

    name = "pplxity"

    def reset(self):
        super().reset()
        self._entropy = 0

    def measure(self, token):
        super().measure(token)
        prob = self._config.languageModel.probability(token, False)
        self._entropy  += -prob    

    def result(self):
        return 2 ** (self._entropy / self._n),

class QwertyMetric(Metric):
    """Emulates optimal typing on classical keyboard (full QWERTY-like layout).
    Neglects cognition load caused by selections list. As metrics get only tokens
    from the text, suppose that they're separated with single space."""

    name = "QWERTY"

    def reset(self):
        super().reset()
        self._charCnt        = 0
        self._keystrokeCnt   = 0

    def measure(self, token):
        super().measure(token)
        if token in [common.Tokenize.TOKEN_END_SENTENCE]:
            return
        keystrokes = 0 # per token
        prefix = ""

        for c in token:
            ll = self._suggestions(prefix)

            completeSuggestions = [s for s, _, partial in ll if not partial]
            partialSuggestions  = [s for s, _, partial in ll if partial]
            allSuggestions      = [s for s, _, _ in ll]

            
            if token in completeSuggestions:
                # +1 use fast accept || +n down arrow +1 enter
                autoComplete = 1 if allSuggestions.index(token) == 1 else allSuggestions.index(token) + 1
                # write remaining chars + space
                typeManually = len(token) - len(prefix) + 1
                # what is better
                keystrokes += min(autoComplete, typeManually)
                break
            elif token in partialSuggestions:
                # +1 use fast accept || +n down arrow +1 enter
                autoComplete = 1 if allSuggestions.index(token) == 1 else allSuggestions.index(token) + 1
                # write remaining chars
                typeManually = len(token) - len(prefix) + 1
                # what is better
                keystrokes += min(autoComplete, typeManually)
                prefix = token
                continue
            else: # manual typing
                keystrokes += 1
            prefix += c
        else: # for
            keystrokes += 1 # separating space for manual typing

        self._charCnt += len(token) + 1 # with separating space
        self._keystrokeCnt += keystrokes


    def result(self):
        return self._keystrokeCnt / self._charCnt,

class BikeyboardMetric:
    pass

class SelectorMetric(Metric):
    """Measure of selector effeciency.
    Count hits of selector w/out any given prefix.Suggestions are evaluated by their position. Missing suggestions are penalised."""

    name = "selector"
    N    = 1

    def reset(self):
        super().reset()
        self._sumOrder      = 0
        self._hitCnt        = [0, 0]
        self._saved         = 0

    def measure(self, token):
        super().measure(token)
        if token in [common.Tokenize.TOKEN_END_SENTENCE]:
            return

        sugg = [w for w, _, _ in self._suggestions()]
        if token in sugg[:self.N]:
            self._hitCnt[0] += 1
            self._hitCnt[1] += 1
            self._saved     += len(token)
        elif len(token) > 1:
            sugg = [w for w, _, _ in self._suggestions(token[0])]
            if token in sugg[:self.N]:
                self._hitCnt[1] += 1
                self._saved     += len(token) - 1
#        else:
#            self._sumOrder += self.missingPenalty


    def result(self):
        return self._hitCnt[0] / self._n, self._hitCnt[1] / self._n, 1 - (self._saved / self._c)# if self._hitCnt > 0 else None

