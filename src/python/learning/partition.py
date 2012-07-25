#!/usr/bin/env python3
import sys

class BlankLineSeparator:
    """Units are delimited by N or more consecutive blank lines."""
    def __init__(self, N):
        self._emptyLines = 0
        self._N = N

    def __call__(self, line):
        result = False
        if line.strip() == "":
            self._emptyLines += 1
        else:
            if self._emptyLines >= self._N:
                result = True
            self._emptyLines = 0
        return result

class WikiSeparator(BlankLineSeparator):
    def __init__(self):
        super().__init__(2)

class TexSeparator(BlankLineSeparator):
    def __init__(self):
        super().__init__(1)

def lineSeparator(line):
    """Every line is a single unit."""
    return True

def constructPartitionFilename(filename, partition):
    components = filename.split('.')
    if components[-1] == 'txt':
        components.insert(-1, str(partition))
    else:
        components.append(str(partition))
    return '.'.join(components)

def splitFile(file, distribution, separator=lineSeparator):
    """Split text file several text files, with given distribution. Generated
    files take data uniformly from original file. By default atomic unit is
    a line.
    Argument `separator` could be a callable that returns True iff current line
    is begining of a new unit.

    Example:
        splitFile(file, [1, 2, 1])  split `file` into three files according to the pattern:
        1
        2
        2
        3
        1
        2
        2
        3
        ...
    """
    F = len(distribution)   # files count
    M = sum(distribution)
    cums = [sum(distribution[k:]) for k in range(F)] # auxiliary list to dispatch output to file

    files = [open(constructPartitionFilename(file.name, f + 1), "w") for f in range(F)]
    units = [0] * F

    unit = -1
    f = 0
    for line in file:
        if separator(line) or unit == -1: # unit == -1 <=> detect first line
            units[f] += 1
            unit += 1
        f = len([1 for d in cums if d >= M-unit % M]) - 1
        files[f].write(line)
        

    for f in range(F):
        print("File `{}` contains {} unit(s).".format(files[f].name, units[f]), file=sys.stderr)
        files[f].close()

