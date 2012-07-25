import math

import collections
import common
import common.tokenize
import datetime
import ui.completion

class Metric:
    """Metric class has its own state. It could be changed by `measure` method
    that's called for every input token. Metric results (tuple of numbers
    for given state) are returned by `result` method. `reset` will put metric
    into initial state.
    
    IMPORTANT: Metric must not change the state of used objects.
    """
    name = "tokens"


    def __init__(self, config):
        self._config = config
        self.reset()

    def reset(self):
        self._n = 0
        self._c = 0
        # share profiling information across metric instances
        Metric.profileChain = collections.defaultdict(datetime.timedelta)

    def measure(self, token):
        self._n += 1
        self._c += len(token) + 1
    
    def result(self):
        #       # DEBUG:
        #       # place for printing out a profe of filter chain.
        #        print("BEHOLD:")
        #        for k, v in Metric.profileChain.items():
        #            print("#\t{}: {}".format(k, v))
        return self._n, self._c

    def resultHeader(self):
        return 'tokens', 'chars'

    def resultFormat(self):
        return [None] * len(self.resultHeader())

    def _suggestions(self, prefix=""):
        cache = self._config.suggestionCache
        if prefix not in cache:
            ## profile time spent in individual parts of the chain
            #start = datetime.datetime.now()
            ll = self._config.selector.suggestions(prefix)
            #end = datetime.datetime.now()
            #Metric.profileChain['selector'] += end-start; start = end

            for filter in self._config.filterChain:
                ll = filter(ll)
                #end = datetime.datetime.now()
                #k = filter.__class__.__name__
                #Metric.profileChain[k] += end-start; start = end

            cache[prefix] = ll

        return cache[prefix]

    def __hash__(self):
        return self.name

    def finish(self):
        pass



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
        if self._n == 0:
            return float('NaN'),
        else:
            return 2 ** (self._entropy / self._n),

    def resultHeader(self):
        return 'pplxity',

class PerplexityOOVMetric(PerplexityMetric):
    """Cross entropy per (word) token for model on given text.
    Ignore OOV tokens

    IMPORTANT: To work properly, language model must have vocabulary that
               correctly implements `in` operator.
    """

    name = "pplxity OOV"

    def reset(self):
        super().reset()
        self._OOVs = 0

    def measure(self, token):
        if token in self._config.languageModel.vocabulary():
            super().measure(token)
        else:
            self._OOVs += 1

    def resultHeader(self):
        return 'pplxity\'', 'OOV'

    def result(self):
        return  super().result() + (self._OOVs, )

class CharacterPerplexityOOCMetric(PerplexityMetric):
    """Cross entropy per character for model on given text.
    Ignore OOC letters (OOC is for out-of-characters).
    """

    name = "char pplxity OOC"

    def reset(self):
        super().reset()
        self._OOCs = 0

    def measure(self, token):        
        if token in [common.tokenize.TOKEN_END_SENTENCE, common.tokenize.TOKEN_NUMERIC]:
            return

        prefix = ''
        ll, _ = self._config.selector.suggestions(prefix)
        prob = sum(2 ** self._config.languageModel.probability(sugg, False) for sugg in ll)
        prevProb = prob
        for c in token:
            prefix += c
            self._config.contextHandler.prefix = prefix
            ll, _ = self._config.selector.suggestions(prefix)
            prob = sum(2 ** self._config.languageModel.probability(sugg, False) for sugg in ll)

            if prob > 0 and prevProb > 0:
                # NOTE: bigram selector can give less suggestions previously than
                #       with current prefix, therefore crop probability to one
                self._entropy -= min(math.log(prob / prevProb, 2), 0)
                self._c += 1
            else:
                self._OOCs += 1
            prevProb = prob



    def resultHeader(self):
        return 'cpplxity\'', 'OOC'

    def result(self):
        if self._c == 0:
            ppl = float('NaN')
        else:
            ppl = 2 ** (self._entropy / self._c)
        return  ppl, self._OOCs

class KeystrokesMetric(Metric):
    """Emulate typing on classical keyboard (full QWERTY-like layout).
    Optimal typing uses suggestion if it's valid. First F suggestions
    are counted as a single keystroke. If there are any other suggestions,
    they are used only when it's less keystrokes (down arrow presses) than typing
    the rest of the word.

    This metric neglects cognition load and non-perfect utilization in the real case.
    """

    name = "KS"

    def __init__(self, config, F=5, trace=common.DevNullFile()):
        super().__init__(config)
        self._trace = trace
        self._F = F

    def reset(self):
        super().reset()
        self._charCnt        = 0
        self._keystrokeCnt   = 0
        self._positionSum    = 0
        self._hitCnt         = 0

    def measure(self, token):
        super().measure(token)
        if token in [common.tokenize.TOKEN_END_SENTENCE]:
            return
        keystrokes = 0 # per token
        prefix = ""

        print(token, file=self._trace)
        for i, c in enumerate(token):
            if i < len(prefix):
                continue
            self._config.contextHandler.prefix = prefix
            ll = self._suggestions(prefix)

            completeSuggestions = [s for s, _, type in ll if type != ui.completion.TextEdit.TYPE_PARTIAL]
            partialSuggestions  = [s for s, _, type in ll if type == ui.completion.TextEdit.TYPE_PARTIAL and token.startswith(s)]
            allSuggestions      = [s for s, _, _ in ll]


            
            if token in completeSuggestions:
                position = allSuggestions.index(token) # zero based
                # +1 use fast accept || +n down arrow +1 enter
                autoComplete        = 1 if position  < self._F else position + 1
                # write remaining chars + space
                typeManually        = len(token) - len(prefix) + 1
                # what is better
                keystrokes          += min(autoComplete, typeManually)
                print("\tfound in suggestions", file=self._trace)
                self._positionSum   += position + 1
                self._hitCnt        += 1
                break
            elif len(partialSuggestions) > 0:
                suggestion = max(partialSuggestions, key=lambda s: len(s))
                print("\tusing partial {} for {}".format(suggestion, token), file=self._trace)
                # +1 use fast accept || +n down arrow +1 enter
                autoComplete = 1 if allSuggestions.index(suggestion) == 1 else allSuggestions.index(suggestion) + 1
                # write remaining chars
                typeManually = len(suggestion) - len(prefix) + 1
                # what is better
                keystrokes += min(autoComplete, typeManually)
                prefix = suggestion
                continue
            else: # manual typing
                print("\ttype '{}'".format(c), file=self._trace)
                keystrokes += 1
            prefix += c
        else: # for
            print("\ttype ' '", file=self._trace)
            keystrokes += 1 # separating space for manual typing

        self._charCnt += len(token) + 1 # with separating space
        self._keystrokeCnt += keystrokes


    def result(self):
        if self._hitCnt > 0:
            meanPos = self._positionSum / self._hitCnt
        else:
            meanPos = float('NaN')
        if self._charCnt > 0:
            meanKS = self._keystrokeCnt / self._charCnt
        else:
            meanKS = float('NaN')
            
        return meanKS, meanPos

    def resultHeader(self):
        return 'keystroke ratio', 'mean pos'

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
        if token in [common.tokenize.TOKEN_END_SENTENCE]:
            return

        sugg = [w for w, _, _ in self._suggestions()]
        if token in sugg[:self.N]:
            self._hitCnt[0] += 1
            self._hitCnt[1] += 1
            self._saved     += len(token)
#        elif len(token) > 1:
#            sugg = [w for w, _, _ in self._suggestions(token[0])]
#            if token in sugg[:self.N]:
#                self._hitCnt[1] += 1
#                self._saved     += len(token) - 1
#        else:
#            self._sumOrder += self.missingPenalty


    def result(self):
        return self._hitCnt[0] / self._n, self._hitCnt[1] / self._n, 1 - (self._saved / self._c)# if self._hitCnt > 0 else None

    def resultHeader(self):
        return 'sugg ratio', '1st char sugg ratio', 'QWERTY\''

class TimeMetric(Metric):
    """Evaluate time performace of measuring script."""

    name = "time"
    
    def reset(self):
        super().reset()
        self._start = datetime.datetime.now()


    def result(self):
        return self._n / (self._end - self._start).total_seconds(),

    def resultHeader(self):
        return 'tok/s',

    def finish(self):
        self._end = datetime.datetime.now()