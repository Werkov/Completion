import itertools
import math

from common import Trie
import common.tokenize
import evaluation
import ui

# Note to filters:
# List variants (w/out lazy iterators) is slightly faster (about 15%).
#

class SuffixAggegator:
    """Group suggestions that are identical at the first 'len(prefix) + leastCommonPrefix' characters."""
    leastCommonPrefix = 3
    def __init__(self, contextHandler, suffix_length=1, minimal_difference=2, excluded_count=1, float_variance=4, ** kwargs):
        self._contextHandler = contextHandler
        self._suffixLength = int(suffix_length)
        self._minimalDifference = int(minimal_difference)
        self._excludedCount = int(excluded_count)
        self._groupVariance = float(float_variance)
        self._groupKey = lambda sugg: sugg[0][:-self._suffixLength]

    def __call__(self, suggestions):
        prefix = self._contextHandler.prefix
        if len(prefix) > 0 and (self._contextHandler.context[-1] == common.tokenize.TOKEN_BEG_SENTENCE \
                                or self._contextHandler.context[-1] == common.tokenize.TOKEN_END_SENTENCE):
            prefix = prefix[0].lower() + prefix[1:]

        suggestions, cond = suggestions
        
        data = sorted(suggestions, key=self._groupKey)
        result = []
        for pseudoStem, group in itertools.groupby(data, self._groupKey):
            group = list(group)
            if len(group) == 1: # singleton groups are pass unchanged
                result.append(group[0])
            elif len(pseudoStem) - len(prefix) < self._minimalDifference:
                result.extend(group)
            else:
                group.sort(key=lambda item: -item[1]) # sorted by probability
                logProbs = [p for _, p, _ in group]
                if evaluation.variance(logProbs) > self._groupVariance: # magic constant
                    excluded = self._excludedCount # first are "very probable"
                else:
                    excluded = 0    # suppose all are similar

                result.extend(group[:excluded])
                # merge remaining tokens
                remaining = group[excluded:]
                if len(remaining) > 1:
                    prob = sum([2 ** p for _, p, _ in remaining])
                    result.append((pseudoStem, math.log(prob, 2), ui.Suggestion.TYPE_PARTIAL))

        # if partials are also valid suggestions merge them into one
        result.sort(key=lambda sugg:sugg[0])
        final = []
        for sugg, group in itertools.groupby(result, key=lambda sugg:sugg[0]):
            group = list(group)
            if len(group) > 1:
                probNormal = sum([2 ** p for _, p, type in group if type == ui.Suggestion.TYPE_NORMAL])
                prob = sum([2 ** p for _, p, type in group])
                result.append((sugg, math.log(prob, 2), ui.Suggestion.TYPE_NORMAL if 2 * probNormal > prob else ui.Suggestion.TYPE_PARTIAL))
            else:
                final.append(group[0])
        #final = result
        final.sort(key=lambda item: -item[1]) # sorted by probability
        return (final, cond)

class SentenceCapitalizer:
    """
    Suggestions starting a new sentence have capitalized first character.
    """
    def __init__(self, contextHandler):
        self._contextHandler = contextHandler
        self.enabled = True # for purposes of testing

    def __call__(self, suggestions):
        if self.enabled:
            return [self._process(suggestion)
                for suggestion in suggestions
                ]
        else:
            return suggestions
#        return map(self._process, suggestions)

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
    def __init__(self, languageModel, type=ui.Suggestion.TYPE_NORMAL):
        self._languageModel = languageModel
        self._type = type

    def __call__(self, suggestions):
        return ([(suggestion, self._languageModel.probability(suggestion, False), self._type)
                for suggestion in suggestions[0]
                ], suggestions[1])
#        return (map(self._process, suggestions[0]), suggestions[1])

    def _process(self, suggestion):
        return (suggestion, self._languageModel.probability(suggestion, False), self._type)

class SuggestionsLimiter:
    """
    Limit the number of suggestions by the minimal (log 2) probability and
    maximal count. This should reduce the cognitive load.
    """
    def __init__(self, min_probability=-16, max_count=10, prefix_condition=False, ** kwargs):
        self._minProbability = float(min_probability)
        self._maxCount = int(max_count)
        self._prefixCondition = prefix_condition

    def __call__(self, suggestions):
        if self._prefixCondition:
            shift = math.log(suggestions[1], 2) if suggestions[1] > 0 else -100
        else:
            shift = 0

        probLimited = list(itertools.takewhile(lambda sugg: sugg[1] - shift >= self._minProbability, suggestions[0]))
        return probLimited[:self._maxCount]
#        probLimited = itertools.takewhile(lambda sugg: sugg[1] - shift >= self._minProbability, suggestions[0])
#        return itertools.islice(probLimited, self._maxCount)

class AddedCharacters:
    """
    Accept only those suggestions that are longer than prefix by given
    difference.
    When empty prefix is true, don't apply filter for empty prefix.
    Works with simple suggestions (not tuples).
    """
    def __init__(self, contextHandler, difference=0, empty_prefix=True, ** kwargs):
        self._contextHandler = contextHandler
        self._difference = int(difference)
        self._emptyPrefix = empty_prefix

    def __call__(self, suggestions):
        if self._emptyPrefix and self._contextHandler.prefix == "":
            return suggestions
        return ([s for s in suggestions[0] if self._condition(s)], suggestions[1])
#        return (filter(self._condition, suggestions[0]), suggestions[1])
        
    def _condition(self, suggestion):
        return len(suggestion) > len(self._contextHandler.prefix) + self._difference

class FilterTokenType:
    """
    Exclude suggestions whose token type is of given type.
    """
    def __init__(self, tokenType):
        self.tokenType = tokenType
        self.tokenizer = common.tokenize.Tokenizer()

    def __call__(self, suggestions):
        return ([s for s in suggestions[0] if self._condition(s)], suggestions[1])
#        return (filter(self._condition, suggestions[0]), suggestions[1])

    def _condition(self, suggestion):
        return not self.tokenizer.isType(suggestion, self.tokenType)