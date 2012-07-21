def mean(iterable):
    return sum(iterable) / len(iterable)

def variance(iterable):
    m = mean(iterable)
    return mean([(x-m) * (x-m) for x in iterable])