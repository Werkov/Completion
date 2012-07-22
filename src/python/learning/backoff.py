import math
import sys

import collections
from common import SimpleTrie
import common.tokenize
import lm.probability

class BackoffModel:
    """Estimate Katz's backoff model from trained on data stored in
    `lm.probability.ngramCounter` object.
    1) Estimate conditional probability for each ngram (MLE or discounted)
    2) Calculate back-off weights, in order to probs add to one.

    Based on SRI LM implementation.
    """
    precision = 6 # to compensate limited precision in ARPA file
    
    def __init__(self, counter, unk=True, order=2, discounts=None):
        """
        counter     `lm.probability.ngramCounter` with counts data
        unk         create '<unk>' token for probabilty freed by discounting
        order
        discounts   dictionary of discount callables for each ngram length
                    callable gets count of occurencies and should returned
                    discounted number
        """
        self.trie = SimpleTrie()
        self.BOWs = {}
        self.order = order

        if not discounts:
            discounts = {n: lm.probability.NoDiscount() for n in range(1, order + 1)}
        self._initProbabilites(counter, unk, discounts)
        self._calculateBOWs()

    def _initProbabilites(self, counter, unk, discounts):
        N = len(counter)
        self.probs = {}
        self.ngrams = set() # non discounted ngrams

        for ngram, count in counter.items():
            n = len(ngram)
            if not n:
                continue

            if n == 1:
                prevCount = N
            elif n > 1:
                prevCount = counter[ngram[:-1]]

            # hack assumed from SRI LM
            #  however here applied always with GT discount
            if isinstance(discounts[n], lm.probability.GoodTuringDiscount):# and disdiscounts[n].validCoefficients():
                prevCount += 1
            
            # discount only the queried ngram count
            #   prevCount is unchanged as we discount conditional frequency (probability) only
            prob = discounts[n](count) / prevCount

            if prob > 0 and ngram not in [(common.tokenize.TOKEN_BEG_SENTENCE,)]:
                logProb = round(math.log10(prob), self.precision)
                self.probs[ngram] = logProb
                self.ngrams.add(ngram)
            else:
                self.probs[ngram] = lm.probability.logNegInf
                # don't add to ngrams, that will eliminate discounted ngrams
                

            # add ngram to trie for search
            node = self.trie
            for token in ngram:
                node = node[token]

        self.ngrams.add((common.tokenize.TOKEN_BEG_SENTENCE,))
        self.probs[(common.tokenize.TOKEN_BEG_SENTENCE,)] = lm.probability.logNegInf
        if unk:
            self.ngrams.add((common.tokenize.TOKEN_UNK,))
            self.probs[(common.tokenize.TOKEN_UNK,)] = lm.probability.logNegInf
            _ = self.trie[common.tokenize.TOKEN_UNK]


    def _calculateBOWs(self):
        # see Ngram::computeBOW in SRI LM
        # calculate from low order to high (FIFO trie walk)
        queue = collections.deque()
        queue.append(())

        while len(queue):
            context = queue.popleft()
            result = self._BOWforContext(context)
            if result:
                numerator, denominator = result
                if len(context) == 0:
                    self._distributeProbability(numerator, context)
                elif numerator == 0 and denominator == 0:
                    self.BOWs[context] = 0 # log 1
                else:
                    self.BOWs[context] = math.log10(numerator) - math.log10(denominator) if numerator > 0 else lm.probability.logNegInf
            else:
                self.BOWs[context] = lm.probability.logNegInf

            if len(context) < self.order:
                node = self.trie
                for token in context:
                    node = node[token]
                for k in node:
                    queue.append(context + (k,))

    def _BOWforContext(self, context):
        denominator = 1

        node = self.trie
        for token in context:
            node = node[token]

        numerator = 1
        denominator = 1
        for w in node:
            ngram = context + (w, )
            numerator -= 10 ** self.probs[ngram]
            if len(ngram) > 1:
                denominator -= 10 ** self.probs[ngram[1:]] # lower order estimate

        # rounding errors
        #if numerator < 0 and numerator > -lm.probability.epsilon:
        #   numerator = 0
        #if denominator < 0 and denominator > -lm.probability.epsilon:
        #   denominator = 0
        if abs(numerator) < lm.probability.epsilon:
            numerator = 0
        if abs(denominator) < lm.probability.epsilon:
            denominator = 0

        if denominator == 0 and numerator > lm.probability.epsilon:
            if numerator == 1: # shouldn't be
                return None
            scale = -math.log10(1-numerator) # log factor to scale sum context probabilities to one
            for w in node:
                ngram = context + (w, )
                self.probs[ngram] += scale
            numerator = 0
        elif numerator < 0:
            # erroneous state
            return None
        elif denominator <= 0:
            if numerator > lm.probability.epsilon:
                # erroneous state
                return None
            else:
                numerator = 0
                denominator = 0

        return numerator, denominator

    def _distributeProbability(self, probability, context):
        if probability == 0:
            return
        node = self.trie
        for token in context:
            node = node[token]
        if common.tokenize.TOKEN_UNK in node:
            print("Assigning {:.3g} probability to {} in context {}.".format(probability, common.tokenize.TOKEN_UNK, context), file=sys.stderr)
            ngram = context + (common.tokenize.TOKEN_UNK, )
            self.probs[ngram] = math.log10(probability)
        else:
            print("Distributing {:.3g} probability over {} tokens in context {}.".format(probability, len(node), context), file=sys.stderr)
            amount = probability / len(node)
            for k in node:
                ngram = context + (k, )
                self.probs[ngram] = math.log10(10 ** self.probs[ngram] + amount)

    def dumpToARPA(self, file):
        """Write estimated model to ARPA text file."""
        print('\\data\\', file=file)
        for i in range(self.order):
            print('ngram {}={}'.format(i + 1, len([1 for ngram in self.ngrams if len(ngram) == i + 1])), file=file)
        print(file=file)

        for n in range(1, self.order + 1):
            print('\\{}-grams:'.format(n), file=file)
            for k in sorted(self.ngrams):
                if len(k) != n:
                    continue
                if k in self.BOWs and self.BOWs[k] != 0:
                    print('{:.7g}\t{}\t{:.7g}'.format(self.probs[k], ' '.join(k), self.BOWs[k]), file=file)
                else:
                    print('{:.7g}\t{}'.format(self.probs[k], ' '.join(k)), file=file)
            print(file=file)

        print('\\end\\', file=file)

