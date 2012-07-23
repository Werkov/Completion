import math
import sys
import collections

import lm
import lm.probability
import common.tokenize

class CachedModel(lm.LangModel):
    def __init__(self, size = 100, **kwargs):
        self._size = int(size)
        self.reset()

    def vocabulary(self):        
        return self._vocabulary.keys()

    def reset(self, context=[]):
        self._vocabulary = collections.Counter(context[-self._size:])
        self._queue = collections.deque(context[-self._size:])

    def probability(self, token, changeContext=True):
        if self._vocabulary[token] == 0:
            result = -100
        else:
            result = math.log(self._vocabulary[token] / len(self._queue), 2)
        if changeContext:
            self._vocabulary[token] += 1
            self._queue.append(token)
            if len(self._queue) > self._size:
                forget = self._queue.popleft()
                self._vocabulary[forget] -= 1
        return result


class UniformModel(lm.LangModel):
    def __init__(self, vocabularySize):
        self._probability = math.log(1 / vocabularySize, 2)

    def probability(self, token, changeContext=True):
        return self._probability

class LInterpolatedModel(lm.LangModel):
    def __init__(self):
        self._models = []
        self._weights = []

    def addModel(self, model, weight):
        self._models.append(model)
        self._weights.append(weight)

    def normalizeWeights(self):
        W = sum(self._weights)
        self._weights = list(map(lambda w: w / W, self._weights))

    def shift(self, token):
        for model in self._models:
            model.shift(token)

    def reset(self):
        for model in self._models:
            model.reset()

    def probability(self, token, changeContext=True):
        comb = [weight * 2 ** model.probability(token, changeContext) for model, weight in zip(self._models, self._weights)]
        return math.log(sum(comb), 2)

    def optimizeWeights(
                        self,
                        data,
                        stopDelta=None,
                        stopIterations=20,
                        trace=sys.stderr
                        ):
        """Optimize weights of model over training data using
        EM algorithm.
        IMPORTANT: Will reset state of self and subsidiary models.
        """
        def iteration():
            nonlocal iterations
            iterations += 1
            self.reset()
            self.normalizeWeights()

            contributions  = [0] * len(self._models)
            entropy = 0
            discount = 0
            for token in data:
                comb = [weight * 2 ** model.probability(token, True) for model, weight in zip(self._models, self._weights)]
                if token in [common.tokenize.TOKEN_BEG_SENTENCE]:  # only shift models, don't count
                    discount += 1
                    continue
                    
                total = sum(comb)
                for i in range(len(contributions)):
                    contributions[i] += comb[i] / total
                entropy -= math.log(total, 2)

            N = len(data) - discount # omitted begin sentences
            newWeights = [contribution / N for contribution in contributions]
            entropy /= N
            return 2**entropy, newWeights
        # --
        data = list(data) # cache data from sequence for repeated iterations
        print("Running EM algorithm on {} training tokens.".format(len(data)), file=trace)
        iterations = 0

        prevPplx, newWeights = iteration()
        while True:
            print("{} W:\t".format(iterations) + "\t".join(["{:.2f}".format(w) for w in self._weights]), file=trace)
            self._weights = newWeights
            pplx, newWeights = iteration()
            delta = (pplx-prevPplx) / pplx
            print("{} P:\t{:.1f}\t{:.1f}\td = {:.1f}%".format(iterations, prevPplx, pplx, delta*100), file=trace)
            if delta > 0:
                print("{}\tSomething went wrong, pplx increased ({}%).".format(iterations, delta*100), file=trace)
                break
            if (stopDelta and abs(delta) < stopDelta) or iterations > stopIterations:
                break
            prevPplx = pplx
        print("{} W:\t".format(iterations) + "\t".join(["{:.2f}".format(w) for w in self._weights]), file=trace)

