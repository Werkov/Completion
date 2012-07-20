import argparse
from common import pathFinder
import common.tokenize
from common.configuration import Configuration as Configuration
import lm.model
import lm.selection
from lm.kenlm import Model as KenLMModel
import ui.completion
import ui.filter



class Basic(Configuration):
    description = """Stupid configuration."""
    aliases     = []

    @staticmethod
    def configureArgParser(parser):
        parser.add_argument('-abbr', help='path to abbreviatrons file')


    def _initialize(self):
        # add listeners separately from creation to avoid cycles
        contextHandler = self.contextHandler
        contextHandler.addListener(self.selector)
        contextHandler.addListener(self.languageModel)

    def _createFilterChain(self):
        return [
            self.addedCharsFilter,
            self.probabilityFilter,
            self.sortFilter,
            self.limitFilter,
            self.capitalizeFilter
        ]

    def _createSelector(self):
        return lm.Selector()

    def _createContextHandler(self):
        contextHandler = ui.ContextHandler(self.stringTokenizer, self.sentenceTokenizer)
        return contextHandler

    def _createLanguageModel(self):
        return lm.LangModel()

    # suggestions filters
    def _createAddedCharsFilter(self):
        return ui.filter.AddedCharacters(self.contextHandler)

    def _createCapitalizeFilter(self):
        return ui.filter.SentenceCapitalizer(self.contextHandler)

    def _createProbabilityFilter(self):
        return ui.filter.ProbabilityEstimator(self.languageModel)

    def _createLimitFilter(self):
        return ui.filter.SuggestionsLimiter()

    def _createSortFilter(self):
        def sortFilter(suggestions):
            return sorted(suggestions, key=lambda sugg: (sugg[1], len(sugg[0])), reverse=True)
        return sortFilter

    # tokenization
    def _createStringTokenizer(self):
        return common.tokenize.StringTokenizer()

    def _createTextFileTokenizerClass(self):
        return common.tokenize.TextFileTokenizer

    def _createSentenceTokenizer(self):
        if 'abbr' in self._params and self._params['abbr']:
            abbr = open(pathFinder(self._params['abbr']), 'r')
            abbreviations = [l.strip() for l in abbr.readlines()]
            abbr.close()
        else:
            abbreviations = []
        return common.tokenize.SentenceTokenizer(abbreviations=abbreviations)

    # UI
    def _createPredictNext(self):
        return False

class Simple(Basic):
    description = """KenLM for probability evaluation and its vocabulary for uniform selector."""
    aliases     = ['s']

    def configureArgParser(parser):
        Basic.configureArgParser(parser)
        parser.add_argument('-lm', help='path to ARPA file', required=True)


    def _createSelector(self):
        return lm.selection.UniformSelector(languageModel=self.languageModel)

    def _createLanguageModel(self):
        return KenLMModel(pathFinder(self._params['lm']))

class Uniform(Simple):
    description = """KenLM for probability evaluation and another's KenLM vocabulary for
        uniform selector."""
    aliases     = ['u']

    def configureArgParser(parser):
        Basic.configureArgParser(parser)
        parser.add_argument('-lm', help='path to probability ARPA file', required=True)
        parser.add_argument('-voc', help='path to vocabulary ARPA file', required=True)


    def _createSelector(self):
        return lm.selection.UniformSelector(KenLMModel(pathFinder(self._params['voc'])).vocabulary())
    def _createLanguageModel(self):
        return KenLMModel(pathFinder(self._params['lm']))

class Bigram(Simple):
    description = """KenLM for probability evaluation and bigram selector based
    on ARPA file."""
    aliases     = ['b']

    def configureArgParser(parser):
        Basic.configureArgParser(parser)
        parser.add_argument('-lm', help='path to probability ARPA file', required=True)
        parser.add_argument('-sel', help='path to selector ARPA file', required=True)


    def _createSelector(self):
        return lm.selection.BigramSelector(pathFinder(self._params['sel']), self.contextHandler)
    def _createLanguageModel(self):
        return KenLMModel(pathFinder(self._params['lm']), False)


class BigramCached(Bigram):
    description = """KenLM for probability evaluation and bigram selector based
    on ARPA file + cache."""
    aliases     = ['bc']


    def _createSelector(self):
        multi = lm.selection.MultiSelector()
        multi.addSelector(lm.selection.BigramSelector(pathFinder(self._params['sel']), self.contextHandler))
        multi.addSelector(lm.selection.UniformSelector(languageModel=self.cachedModel))
        return multi
    
    def _createLanguageModel(self):
        lin = lm.model.LInterpolatedModel()
        lin.addModel(KenLMModel(pathFinder(self._params['lm']), False), 0.93)
        lin.addModel(self.cachedModel, 0.07)
        return lin
    
    def _createCachedModel(self):
        return lm.model.CachedModel()

class BigramNext(BigramCached):
    description = """KenLM for probability evaluation and bigram selector based
    on ARPA file + cache. EXPERIMENATL: Suggests also continuations of the first word."""
    aliases     = ['bcn']

    def _createPredictNext(self):
        return True

    def _createPrimaryChain(self):
        return [
            self.addedCharsFilter,
            self.probabilityFilter,
            self.sortFilter,
            self.limitFilter,
            self.capitalizeFilter
        ]

    def _createSecondaryChain(self):
        return [
            self.addedCharsFilter,
            self.probabilityFilter,
            self.sortFilter,
            self.limitFilter,
            # don't need capitalization
        ]
    def _createMerger(self):
        def merge(primary, secondary):
            primary = list(primary)
            if not primary:
                return []
            pred = primary[0][1]
            return [(a, b, ui.completion.TextEdit.TYPE_NORMAL) for a, b, _ in primary] + [(a, pred+b, ui.completion.TextEdit.TYPE_NEXT) for a, b, _ in secondary]
        return merge

    def _createCommonChain(self):
        return [self.sortFilter]