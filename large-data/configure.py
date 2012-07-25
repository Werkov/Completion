#!/usr/bin/env python3
from itertools import product
import os.path

#
#   -- Configure here --
#

datafiles = {
    'matka.txt': {
        'distribution': [80, 10, 8, 2],
        'type': 'l',
        'tests': [1] * 10
    },
    'wiki.cs.txt': {
        'distribution': [10000, 1000, 10, 2],
        'type': 'w',
        'tests': [1] * 10
    }
}

backoffOptions = {
    'no': {
        'name': 'No discounting',
        'options': '-cdiscount 0'
    },
    'gt': {
        'name': 'Good-Turing discounting',
        'options': ''
    },
    'kn': {
        'name': 'Kneser-Nay discounting, backoff',
        'options': '-ukndiscount'
    },
    'kni': {
        'name': 'Kneser-Nay discounting, interpolate',
        'options': '-ukndiscount -interpolate'
    },
    'mkn': {
        'name': 'Modified Kneser-Nay discounting, backoff',
        'options': '-kndiscount'
    },
    'mkni': {
        'name': 'Modified Kneser-Nay discounting, interpolate',
        'options': '-kndiscount -interpolate'
    },
}

orders = [1, 3]


#
#   below is generation of Makefile*
#  vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

#
#   Makefile.inc
#


backoffOptionsVars = []
for abbr, data in sorted(backoffOptions.items()):
    backoffOptionsVars.append("#\t{}\nLM_{}={}\n".format(data['name'], abbr.upper(), data['options']))
backoffOptionsVars = "\n".join(backoffOptionsVars)

precious = []
for order in orders:
    precious.append(' '.join(["%.lm{}{}.gz".format(order, abbr) for abbr in sorted(backoffOptions.keys())]))
precious = ' \\\n\t'.join(precious)

srilmCalls = []
for order in orders:
    for abbr in sorted(backoffOptions.keys()):
        if order == 1:
            srilmCalls.append(
                              """%.lm{order}{abbr}: %.txt.sentences
\t$(SRILM) -lm $@ -text $< $(SRI_OPT) $(LM_{ABBR}) -order {order} 2>$@.about
\ted $@ < $(UNTOBI)"""
                              .format(order=order, abbr=abbr, ABBR=abbr.upper()))
        else:
            srilmCalls.append(
                              """%.lm{order}{abbr}: %.txt.sentences
\t$(SRILM) -lm $@ -text $< $(SRI_OPT) $(LM_{ABBR}) -order {order} 2>$@.about"""
                              .format(order=order, abbr=abbr, ABBR=abbr.upper()))
srilmCalls = "\n".join(srilmCalls)

kenlmCalls = []
for order in orders:
    for abbr in sorted(backoffOptions.keys()):
        kenlmCalls.append("""%.lm{order}{abbr}.bin: %.lm{order}{abbr}.gz
\t$(BINKLM) $(KLM_OPT) $< $@"""
                          .format(order=order, abbr=abbr, ABBR=abbr.upper()))
kenlmCalls = "\n".join(kenlmCalls)

selectorCalls = []
for order in orders:
    for abbr in sorted(backoffOptions.keys()):
        selectorCalls.append("""%.lm{order}{abbr}.sel.bin: %.lm{order}{abbr}.gz
\t$(BINSEL) $(SEL_OPT) $< $@"""
                             .format(order=order, abbr=abbr, ABBR=abbr.upper()))
selectorCalls = "\n".join(selectorCalls)

gzipCalls = []
for order in orders:
    for abbr in sorted(backoffOptions.keys()):
        gzipCalls.append("""%.lm{order}{abbr}.gz: %.lm{order}{abbr}
\tgzip $<"""
                         .format(order=order, abbr=abbr, ABBR=abbr.upper()))
gzipCalls = "\n".join(gzipCalls)

warning = "# THIS FILE IS GENERATED AUTOMATICALLY, APPLY CHANGES TO `configure.py`"


output = open('Makefile.inc', 'w')

output.write("""
{warning}

#
# -- Tools --
#
FORMAT={path}/src/python/learning/formatText.py
SPLIT={path}/src/python/learning/textPartition.py
BINKLM={path}/bin/kenlm/build_binary
BINSEL={path}/bin/selector/build_binary
SRILM=ngram-count
UNTOBI={path}/src/other/1to2.ed
GZIP=gzip

#
# -- Options for training backoff models with SRI LM --
#

{backoffOptions}

# General options
SRI_OPT= -unk -debug 1

#
#  -- Options for creating binary files for models
#

#   Store as trie
KLM_OPT= -q 8 -b 8 trie

#   Include only bigrams with probability > 10^-5
SEL_OPT= -c -5


#  Those took long to create, don't rm them
#
.PRECIOUS: %.txt.sentences \\
\t{precious}


#
# -- Training tool chain --
#

#
#   Split to sentences
%.txt.sentences: %.txt wiki.cs.abbr
	$(FORMAT) -a wiki.cs.abbr $<

#
#   SRI LM training combinations
{srilmCalls}

#
#   Create binary
{kenlmCalls}


{selectorCalls}


#
#   -- Other --
#
{gzipCalls}
""".format(
             warning=warning,
             path=os.path.abspath(os.path.join(os.path.dirname(__file__), "../")),
             backoffOptions=backoffOptionsVars,
             precious=precious,
             srilmCalls=srilmCalls,
             kenlmCalls=kenlmCalls,
             selectorCalls=selectorCalls,
             gzipCalls=gzipCalls
             ))

output.close()


#
#  Makefile
#
names = ['train', 'em', 'test', 'debug']


splitCalls = []
testSplitCalls = []
allFiles = []

for datafile, info in datafiles.items():
    parts = datafile.split('.')
    files = []
    dists = []
    renames = []
    parts.insert(-1, None)
    for dist, name, i in zip(info['distribution'], names, range(1, len(info['distribution']) + 1)):
        parts[-2] = str(i)
        src = '.'.join(parts)
        parts[-2] = name
        dst = '.'.join(parts)
        files.append(dst)
        dists.append(str(dist))
        renames.append("mv {} {}".format(src, dst))

    splitCalls.append("""{files}: {datafile}
\t$(SPLIT) -u {type} $< {dist}
\t{renames}"""                      .format(
                      files=' '.join(files),
                      datafile=datafile,
                      type=info['type'],
                      dist=' '.join(dists),
                      renames="\n\t".join(renames)))
    allFiles.extend(files)

    files = []
    parts[-2] = names[2]
    datafile = '.'.join(parts)
    parts.insert(-1, None)
    for i, test in enumerate(info['tests'], 1):
        parts[-2] = str(i)
        dst = '.'.join(parts)
        files.append(dst)

    testSplitCalls.append("""{files}: {datafile}
\t$(SPLIT) -u {type} $< {dist}"""
                          .format(
                          files='\\\n'.join(files),
                          datafile=datafile,
                          type=info['type'],
                          dist=' '.join([str(t) for t in info['tests']]),
                          renames="\n\t".join(renames)))
    allFiles.extend(files)
                      
splitCalls = "\n".join(splitCalls)
testSplitCalls = "\n".join(testSplitCalls)

output = open('Makefile', 'w')

output.write("""\
{warning}

include Makefile.inc

.PHONY: all clean cleanall

all:\\
{all}

{splitCalls}

{testSplitCalls}


clean:
\trm -f *.bin

cleanall: clean
\trm -f *.sentences {clearNames}
""".format(
             warning=warning,
             all='\\\n'.join(allFiles),
             splitCalls=splitCalls,
             testSplitCalls=testSplitCalls,
             clearNames = ' '.join(["*.{}.txt".format(n) for n in names] + ["*.{}.*.txt".format(names[2])])
             ))
             
output.close()
