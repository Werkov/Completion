import collections

epsilon = 1e-12
logNegInf = -99


class NgramCounter(collections.Counter):
    """Count occurencies of ngrams up to given order in token stream.
    Token can be any hashable object and ngrams are represented as tuples
    of tokens (specially single token must be 1-tuple).
    """
    def __init__(self, order=2):
        self._order = order
        self.reset()

    def reset(self, tokens=[]):
        """Reset statistics, current context and vocabulary."""
        self._context = () # null context
        self._len = 0
        self._vocabulary = set()
        for token in tokens:
            self.append(token)

    def resetContext(self):
        """Reset context only."""
        self._context = ()

    def append(self, token):
        """Add token to the stream."""
        self.shift(token)
        self._len += 1
            
    def shift(self, token):
        """Like `append` with the exception, it doesn't increase stream length.
        Useful for padding context.
        """
        self._context = self._context + (token,)
        if len(self._context) > self._order:
            self._context = self._context[1:]
        for n in range(self._order):
            if len(self._context[n:]): # omit null contexts
                self[self._context[n:]] += 1
        self._vocabulary.add(token)


    def __len__(self):
        """Length of processed token stream."""
        return self._len

    def vocabulary(self):
        """All tokens that occured in the stream."""
        return self._vocabulary

    

class CountsOfCounts(collections.defaultdict):
    """Get counts of counts from `ngramCounter` object.
    Data are divided into groups of ngram length.
    Example:
    >>> CoC = CountsOfCounts(ngramCounter)
    >>> CoC[2][4] # get no. of bigrams that occured 4 times
    """
    def __init__(self, ngramCounter):
        super().__init__(collections.Counter)
        for ngram, count in ngramCounter.items():
            self[len(ngram)][count] += 1

class NoDiscount:
    """No discounting. For testing."""
    def __call__(self, count):
        return count

    def validCoefficients(self):
        """Specifiy whether discounting coefficient had to be cropped, rounded
        or somehow else changed. This value involves in backoff.Backoff._initProbabilities
        """
        return True

class AbsoluteDiscount(NoDiscount):
    """Discount all counts by given constant.
    Minimal count is zero.
    """
    def __init__(self, amount):
        self._amount = amount

    def __call__(self, count):
        return max(count - self._amount, 0)

class GoodTuringDiscount(NoDiscount):
    """Good-Turing discounting method, based on counts of counts, used only for
    low counts.
    
    SEE: SRI LM ngram-discount manual.
    """
    def __init__(self, countsOfCounts, gtMax=1, gtMin=1):
        self._gtMax = gtMax
        self._gtMin = gtMin
        self._discounts = {}
        self._validCoeffs = True
        A = (gtMax + 1) * (countsOfCounts[gtMax + 1] / countsOfCounts[1])
        for count in range(gtMin, gtMax + 1):
            if count > gtMax:
                self._discounts[count] = count
            elif countsOfCounts[count] == 0:
                self._discounts[count] = count
                self._validCoeffs = False
            else:
                reduced = (count + 1) * countsOfCounts[count + 1] / (countsOfCounts[count])
                scale = (reduced / count - A) / (1-A)
                if scale < epsilon or scale > 1:
                    scale = 1
                    self._validCoeffs = False
                self._discounts[count] = count * scale

    def validCoefficients(self):
        return self._validCoeffs

    def __call__(self, count):
        if count > self._gtMax:
            return count
        elif count < self._gtMin:
            return 0
        else:
            return self._discounts[count]
        