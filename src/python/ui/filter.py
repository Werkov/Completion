import ui.completion
import math
import itertools

from common import Trie
import common.tokenize
import ui


class EndingAggegator:
    """Group suggestions that are identical at the first 'len(prefix) + leastCommonPrefix' characters."""
    leastCommonPrefix = 3
    def filter(self, suggestions, prefix):
        class Node:
            def __init__(self, partial, suggestion, probability=0):
                self.partial = partial
                self.suggestion = suggestion
                self.probability = probability

        t = Trie()
        sugg = 0
        for suggestion, probability, _ in suggestions:
            t[suggestion] = Node(False, True, probability)
            sugg += 1

        result = []
        added = set()

        if t._findNode(prefix) == None:
            return []
        for sugg in t.children(prefix):
            best = sugg
            while len(sugg) > len(prefix) + self.leastCommonPrefix: # climb the trie
                sugg = sugg[:-1]
                if len(t._findNode(sugg)[1]) > 1:
                    best = sugg

            if best in added:
                continue

            childProbs = [2 ** t[prefix].probability for prefix in t.children(best)]
            if best in t:
                probability = math.log(sum(childProbs) + 2 ** t[best].probability) / math.log(2)
                partial = False
            else:
                probability = math.log(sum(childProbs)) / math.log(2)
                partial = True

            result.append((best, probability, partial))
            added.add(best)



    #        result = [(prefix, t[prefix].probability, t[prefix].partial) for prefix in t if t[prefix].suggestion]
        result.sort(key=lambda item: -item[1]) # sorted by probability
        return result

class SentenceCapitalizer:
    """
    Suggestions starting a new sentence have capitalized first character.
    """
    def __init__(self, contextHandler):
        self._contextHandler = contextHandler

    def __call__(self, suggestions):
        return map(self._process, suggestions)

    def _process(self, suggestion):
        if self._contextHandler.context[-1] == common.tokenize.TOKEN_BEG_SENTENCE \
            or self._contextHandler.context[-1] == common.tokenize.TOKEN_END_SENTENCE:
            return (suggestion[0][0].upper() + suggestion[0][1:], suggestion[1], suggestion[2])
        else:
            return suggestion

class ProbabilityEstimator:
    """
    Suggestions are "extended" by their probability in the lagnuage model.

    Language model must be synchronized with the inserted text.
    """
    def __init__(self, languageModel, type = ui.completion.TextEdit.TYPE_NORMAL):
        self._languageModel = languageModel
        self._type = type

    def __call__(self, suggestions):
        return map(self._process, suggestions)

    def _process(self, suggestion):
        return (suggestion, self._languageModel.probability(suggestion, False), self._type)

class SuggestionsLimiter:
    """
    Limit the number of suggestions by the minimal (log 2) probability and
    maximal count. This should reduce the cognitive load.
    """
    def __init__(self, minProbability = -16, maxCount = 10):
        self._minProbability = minProbability
        self._maxCount = maxCount

    def __call__(self, suggestions):
        probLimited = itertools.takewhile(lambda sugg: sugg[1] >= self._minProbability, suggestions)
        return itertools.islice(probLimited, self._maxCount)

class AddedCharacters:
    """
    Accept only those suggestions that are longer than prefix by given
    difference.
    Can be active only for nonempty prefix.
    Works with simple suggestions (not tuples).
    """
    def __init__(self, contextHandler, difference = 0, emptyPrefix = False):
        self._contextHandler = contextHandler
        self._difference = difference
        self._emptyPrefix = emptyPrefix

    def __call__(self, suggestions):
        if self._emptyPrefix and self._contextHandler.prefix == "":
            return suggestions
        return filter(self._condition, suggestions)

    def _condition(self, suggestion):
        return len(suggestion) > len(self._contextHandler.prefix) + self._difference


