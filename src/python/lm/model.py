import math
from operator import __contains__
import sys

import collections
import common.tokenize
import lm
from lm import probability
import lm.probability

class CachedModel(lm.LangModel):
    def __init__(self, size=100, ** kwargs):
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
        self._vocabulary = MultiVocabulary()

    def addModel(self, model, weight):
        self._models.append(model)
        self._weights.append(weight)
        self._vocabulary.addModel(model)

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

    def vocabulary(self):
        return self._vocabulary

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
            return entropy, newWeights
        # --
        data = list(data) # cache data from sequence for repeated iterations
        print("Running EM algorithm on {} training tokens.".format(len(data)), file=trace)
        iterations = -1

        prevEntropy, newWeights = iteration()
        while True:
            print("{} Weights:\t".format(iterations) + "\t".join(["{:.2f}".format(w) for w in self._weights]), file=trace)
            self._weights = newWeights
            entropy, newWeights = iteration()
            delta = (entropy-prevEntropy) / entropy
            print("{} Entropy:\t{:.1f} -> {:.1f}\td = {:.1f}%".format(iterations, prevEntropy, entropy, delta * 100), file=trace)
            if delta > 0:
                print("{}\tSomething went wrong, entropy increased ({}%).".format(iterations, delta * 100), file=trace)
                break
            if (stopDelta and abs(delta) < stopDelta) or iterations >= stopIterations:
                break
            prevEntropy = entropy
        print("{} Weights:\t".format(iterations) + "\t".join(["{:.2f}".format(w) for w in self._weights]), file=trace)
        print(file=trace)

class LInterpolatedModelBi(LInterpolatedModel):
    """Optimized case of LInterpolatedModel for two models."""

    def compile(self):
        self.w0 = self._weights[0]
        self.w1 = self._weights[1]
        self.m0 = self._models[0]
        self.m1 = self._models[1]

    def probability(self, token, changeContext=True):
        # This is about 30% faster than generic method.
        return math.log(
                        self.w0 * 2 ** self.m0.probability(token, changeContext) +
                        self.w1 * 2 ** self.m1.probability(token, changeContext)
                        , 2)

class LInterpolatedModelTri(LInterpolatedModel):
    """Optimized case of LInterpolatedModel for two models."""

    def compile(self):
        self.w0 = self._weights[0]
        self.w1 = self._weights[1]
        self.w2 = self._weights[2]
        self.m0 = self._models[0]
        self.m1 = self._models[1]
        self.m2 = self._models[2]

    def probability(self, token, changeContext=True):
        return math.log(
                        self.w0 * 2 ** self.m0.probability(token, changeContext) +
                        self.w1 * 2 ** self.m1.probability(token, changeContext) +
                        self.w2 * 2 ** self.m2.probability(token, changeContext)
                        , 2)

class MultiVocabulary:
    def __init__(self):
        self._models = []

    def addModel(self, model):
        self._models.append(model)

    def __contains__(self, token):
        for model in self._models:
            if token in model.vocabulary():
                return True
        return False