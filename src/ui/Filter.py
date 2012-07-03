import math

from common import Trie
import common.Tokenize

class EndingAggegator:
    """Group suggestions that are identical at the first 'len(preifx) + leastCommonPrefix' characters."""
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
    def __init__(self, contextHandler):
        self._contextHandler = contextHandler

    def __call__(self, suggestion):
        if self._contextHandler.context[-1] == common.Tokenize.TOKEN_BEG_SENTENCE \
            or self._contextHandler.context[-1] == common.Tokenize.TOKEN_END_SENTENCE:
            return (suggestion[0][0].upper() + suggestion[0][1:], suggestion[1], suggestion[2])
        else:
            return suggestion
