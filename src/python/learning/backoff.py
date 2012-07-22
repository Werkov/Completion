import math
import sys

import collections
from common import SimpleTrie
import common.tokenize

class BackoffModel:
    epsilon = 1e-6
    logNegInf = -99
    precision = 6 # to compensate limited precision in ARPA file
    
    def __init__(self, counter, unk=True, order=2):
        self.trie = SimpleTrie()
        self.probs = {}
        self.BOWs = {}
        self.order = order

        self._initProbabilites(counter, unk)
        self._calculateBOWs()

    def _initProbabilites(self, counter, unk):
        N = len(counter)
        V = len(counter.vocabulary())

        for ngram, count in counter.items():
            n = len(ngram)
            if not n:
                continue

            if n == 1:
                prevCount = N
            elif n > 1:
                prevCount = counter[ngram[:-1]]

            # discounting
            d = 0.5
            #prob = (count + d) / (prevCount + d * V)
            prob = (count - d) / (prevCount)

            if ngram[-1] == common.tokenize.TOKEN_BEG_SENTENCE:
                prob = 0
            logProb = round(math.log10(prob), self.precision) if prob > 0 else self.logNegInf
            self.probs[ngram] = logProb

            # add ngram to trie
            node = self.trie
            for token in ngram:
                node = node[token]
        if unk:
            self.probs[(common.tokenize.TOKEN_UNK,)] = self.logNegInf
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
                    self.BOWs[context] = math.log10(numerator) - math.log10(denominator) if numerator > 0 else self.logNegInf
            else:
                self.BOWs[context] = self.logNegInf

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
        if numerator < 0 and numerator > -self.epsilon:
            numerator = 0
        if denominator < 0 and denominator > -self.epsilon:
            denominator = 0

        if denominator == 0 and numerator > self.epsilon:
            scale = -math.log10(1-numerator) # log factor to scale sum context probabilities to one
            for w in node:
                ngram = context + (w, )
                self.probs[ngram] += scale
            numerator = 0
        elif numerator < 0:
            # erroneous state
            return None
        elif denominator <= 0:
            if numerator > self.epsilon:
                # erroneous state
                return None
            else:
                numerator = 0
                denominator = 0

        return numerator, denominator

    def _distributeProbability(self, probability, context):
        node = self.trie
        for token in context:
            node = node[token]
        if common.tokenize.TOKEN_UNK in node:
            print("Assigning {:.3g} probability to {} in context {}.".format(probability, common.tokenize.TOKEN_UNK, context), file=sys.stderr)
            ngram = context + (common.tokenize.TOKEN_UNK, )
            self.probs[ngram] = math.log10(probability)
        else:
            print("Distributing {:.g} probability over {} tokens in context {}.".format(probability, len(node), context), file=sys.stderr)
            amount = probability / len(node)
            for k in node:
                ngram = context + (k, )
                self.probs[ngram] = math.log10(10 ** self.probs[ngram] + amount)

    def dumpToARPA(self, file):
        print('\\data\\', file=file)
        for i in range(self.order):
            print('ngram {}={}'.format(i + 1, len([1 for ngram in self.probs if len(ngram) == i + 1])), file=file)
        print(file=file)

        for n in range(1, self.order + 1):
            print('\\{}-grams:'.format(n), file=file)
            for k, v in sorted(self.probs.items()):
                if len(k) != n:
                    continue
                if k in self.BOWs and self.BOWs[k] != 0:
                    print('{:.7g}\t{}\t{:.7g}'.format(v, ' '.join(k), self.BOWs[k]), file=file)
                else:
                    print('{:.7g}\t{}'.format(v, ' '.join(k)), file=file)
            print(file=file)

        print('\\end\\', file=file)


