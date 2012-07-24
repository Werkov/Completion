import argparse
from common import pathFinder
from common.configuration import Configuration as Configuration
import common.tokenize
from lm.kenlm import Model as KenLMModel
import lm.model
import lm.selection
import ui.completion
import ui.filter

# Inheritance tree is as follows.
#   0   <   0c
#   ^       ^
#   u       uc   <   uuc
#   ^                 ^
#   n   <   nc       nuc

class Basic(Configuration):
    """Configuration defining basic objects for its descedants too."""
    
    description = """No suggestions at all."""
    alias = '0'


    def _initialize(self):
        # add listeners separately from creation to avoid cycles
        contextHandler = self.contextHandler
        contextHandler.addListener(self.selector)
        contextHandler.addListener(self.languageModel)

    def _createFilterChain(self, params):
        # if filter is None, skip it
        return [f for f in [
            self.addedCharsFilter,
            self.interpunctionFilter,
            self.probabilityFilter,
            self.sortFilter,
            self.suffixFilter,
            self.limitFilter,
            self.capitalizeFilter
        ] if f]

    def _createContextHandler(self, params):
        contextHandler = ui.ContextHandler(self.stringTokenizer, self.sentenceTokenizer)
        return contextHandler

    def _createSelector(self, params):
        return lm.Selector()

    def _createLanguageModel(self, params):
        return lm.LangModel()

    # suggestions filters
    def _createAddedCharsFilter(self, params):
        if params.getboolean('enabled', fallback=True):
            return ui.filter.AddedCharacters(self.contextHandler, ** params)

    def _createInterpunctionFilter(self, params):
        if params.getboolean('enabled', fallback=True):
            return ui.filter.FilterTokenType(common.tokenize.TYPE_DELIMITER)

    def _createCapitalizeFilter(self, params):
        if params.getboolean('enabled', fallback=True):
            return ui.filter.SentenceCapitalizer(self.contextHandler)

    def _createProbabilityFilter(self, params):
        if params.getboolean('enabled', fallback=True):
            return ui.filter.ProbabilityEstimator(self.languageModel)

    def _createLimitFilter(self, params):
        if params.getboolean('enabled', fallback=True):            
            p = dict(params)
            p['prefix_condition'] = params.getboolean('prefix_condition')
            return ui.filter.SuggestionsLimiter( ** p)

    def _createSortFilter(self, params):
        if params.getboolean('enabled', fallback=True):
            def sortFilter(suggestions):
                suggestions[0].sort(key=lambda sugg: (sugg[1], len(sugg[0])), reverse=True)
                return suggestions
                #return (sorted(suggestions[0], key=lambda sugg: (sugg[1], len(sugg[0])), reverse=True), suggestions[1])
        return sortFilter

    def _createSuffixFilter(self, params):
        if params.getboolean('enabled', fallback=True):
            return ui.filter.SuffixAggegator(self.contextHandler, **params)

# tokenization
    def _createStringTokenizer(self, params):
        return common.tokenize.StringTokenizer()

    def _createTextFileTokenizerClass(self, params):
        return common.tokenize.TextFileTokenizer

    def _createSentenceTokenizer(self, params):
        if 'abbr_file' in params:
            abbr = open(pathFinder(params['abbr_file']), 'r')
            abbreviations = [l.strip() for l in abbr.readlines()]
            abbr.close()
        else:
            abbreviations = []
        return common.tokenize.SentenceTokenizer(abbreviations=abbreviations)

    # UI
    def _createPredictNext(self, params):
        return False

    # self-evaluation
    def _createSuggestionCache(self, params):
        return {}

class Unigram(Basic):
    description = """Unigram model for suggestions."""
    alias = 'u'

    @staticmethod
    def configureArgParser(parser):
        parser.add_argument('-mlm', help='path to ARPA file with model')
        parser.add_argument('-msel', help='path to ARPA file with model for selector')

    def _createLanguageModel(self, params):
        return self.mainModel

    def _createSelector(self, params):
        return self.mainSelector

    def _createMainModel(self, params):
        filename = self._CLIparams['mlm'] if self._CLIparams['mlm'] else params['file']
        return KenLMModel(pathFinder(filename))

    def _createMainSelector(self, params):
        filename = self._CLIparams['msel'] if self._CLIparams['msel'] else params['file']
        return lm.selection.UnigramSelector(pathFinder(filename), self.contextHandler, ** params)



class Ngram(Unigram):
    description = """Ngram (n > 1) model for suggestions. Bigram selector."""
    alias = 'n'

    def _createMainSelector(self, params):
        filename = self._CLIparams['msel'] if self._CLIparams['msel'] else params['file']
        return lm.selection.BigramSelector(pathFinder(filename), self.contextHandler, ** params)
    

class BasicCached(Basic):
    description = """Suggestions based on cache."""
    alias = '0c'

    def _createLanguageModel(self, params):
        return self.cachedModel

    def _createSelector(self, params):
        return self.cachedSelector

    def _createCachedModel(self, params):
        return lm.model.CachedModel(** params)

    def _createCachedSelector(self, params):
        return lm.selection.UniformSelector(languageModel=self.cachedModel)

class UnigramCached(BasicCached):
    description = """Suggestions mixed from unigram model + cached."""
    alias = 'uc'

    @staticmethod
    def configureArgParser(parser):
        Unigram.configureArgParser(parser)

    def _createLanguageModel(self, params):
        lin = lm.model.LInterpolatedModelBi()
        lin.addModel(self.mainModel, float(params['main_weight']))
        lin.addModel(self.cachedModel, float(params['cached_weight']))
        lin.normalizeWeights()
        lin.compile()
        return lin

    def _createSelector(self, params):
        multi = lm.selection.MultiSelector()
        multi.addSelector(self.mainSelector)
        multi.addSelector(self.cachedSelector)
        return multi

    def _createMainModel(self, params):
        return Unigram._createMainModel(self, params)

    def _createMainSelector(self, params):
        return Unigram._createMainSelector(self, params)

class NgramCached(UnigramCached):
    description = """Suggestions mixed from ngram model + cached."""
    alias = 'nc'

    def _createMainModel(self, params):
        return Ngram._createMainModel(self, params)

    def _createMainSelector(self, params):
        return Ngram._createMainSelector(self, params)

class UnigramUserCached(UnigramCached):
    description = """Suggestions mixed from unigram model, user model + cached."""
    alias = 'uuc'

    @staticmethod
    def configureArgParser(parser):
        parser.add_argument('-ulm', help='path to ARPA file with user model')
        parser.add_argument('-usel', help='path to ARPA file with model for user selector')

    def _createLanguageModel(self, params):
        lin = lm.model.LInterpolatedModelTri()
        lin.addModel(self.mainModel, float(params['main_weight']))
        lin.addModel(self.userModel, float(params['user_weight']))
        lin.addModel(self.cachedModel, float(params['cached_weight']))
        lin.normalizeWeights()
        lin.compile()
        return lin

    def _createSelector(self, params):
        multi = lm.selection.MultiSelector()
        multi.addSelector(self.mainSelector)
        multi.addSelector(self.userSelector)
        multi.addSelector(self.cachedSelector)
        return multi

    def _createUserModel(self, params):
        filename = self._CLIparams['ulm'] if self._CLIparams['ulm'] else params['file']
        return KenLMModel(pathFinder(filename))

    def _createUserSelector(self, params):
        filename = self._CLIparams['usel'] if self._CLIparams['usel'] else params['file']
        if params.getboolean('bigram', fallback=False):
            return lm.selection.UnigramSelector(pathFinder(filename), self.contextHandler, ** params)
        else:
            return lm.selection.UnigramSelector(pathFinder(filename), self.contextHandler, ** params)

class NgramUserCached(UnigramUserCached):
    description = """Suggestions mixed from ngram model, user model + cached."""
    alias = 'nuc'

    def _createMainSelector(self, params):
        return Ngram._createMainSelector(self, params)

#
#class Simple(Basic):
#    description = """KenLM for probability evaluation and its vocabulary for uniform selector."""
#    alias = 's'
#
#    def configureArgParser(parser):
#        Basic.configureArgParser(parser)
#        parser.add_argument('-lm', help='path to ARPA file', required=True)
#
#
#    def _createSelector(self):
#        return lm.selection.UniformSelector(languageModel=self.languageModel)
#
#    def _createLanguageModel(self):
#        return KenLMModel(pathFinder(self._params['lm']))
#
#class Uniform(Simple):
#    description = """KenLM for probability evaluation and another's KenLM vocabulary for
#        uniform selector."""
#    alias = 'u'
#
#    def configureArgParser(parser):
#        Basic.configureArgParser(parser)
#        parser.add_argument('-lm', help='path to probability ARPA file', required=True)
#        parser.add_argument('-voc', help='path to vocabulary ARPA file', required=True)
#
#
#    def _createSelector(self):
#        return lm.selection.UniformSelector(KenLMModel(pathFinder(self._params['voc'])).vocabulary())
#    def _createLanguageModel(self):
#        return KenLMModel(pathFinder(self._params['lm']))
#
#class Bigram(Simple):
#    description = """KenLM for probability evaluation and bigram selector based
#    on ARPA file."""
#    alias = 'b'
#
#    def configureArgParser(parser):
#        Basic.configureArgParser(parser)
#        parser.add_argument('-lm', help='path to probability ARPA file', required=True)
#        parser.add_argument('-sel', help='path to selector ARPA file', required=True)
#
#
#    def _createSelector(self):
#        return lm.selection.BigramSelector(pathFinder(self._params['sel']), self.contextHandler)
#    def _createLanguageModel(self):
#        return KenLMModel(pathFinder(self._params['lm']), False)
#
#
#class BigramCached(Bigram):
#    description = """KenLM for probability evaluation and bigram selector based
#    on ARPA file + cache."""
#    alias = 'bc'
#
#
#    def _createSelector(self):
#        multi = lm.selection.MultiSelector()
#        multi.addSelector(lm.selection.BigramSelector(pathFinder(self._params['sel']), self.contextHandler))
#        multi.addSelector(lm.selection.UniformSelector(languageModel=self.cachedModel))
#        return multi
#
#    def _createLanguageModel(self):
#        lin = lm.model.LInterpolatedModel()
#        lin.addModel(KenLMModel(pathFinder(self._params['lm']), False), 0.93)
#        lin.addModel(self.cachedModel, 0.2)
#        return lin
#
#    def _createCachedModel(self):
#        return lm.model.CachedModel()
#
#class BigramNext(BigramCached):
#    description = """KenLM for probability evaluation and bigram selector based
#    on ARPA file + cache. EXPERIMENATL: Suggests also continuations of the first word."""
#    alias = 'bcn'
#
#    def _createPredictNext(self):
#        return True
#
#    def _createPrimaryChain(self):
#        return [
#            self.addedCharsFilter,
#            self.probabilityFilter,
#            self.sortFilter,
#            self.limitFilter,
#            self.capitalizeFilter
#        ]
#
#    def _createSecondaryChain(self):
#        return [
#            self.addedCharsFilter,
#            self.probabilityFilter,
#            self.sortFilter,
#            self.limitFilter,
#            # don't need capitalization
#        ]
#    def _createMerger(self):
#        def merge(primary, secondary):
#            primary = list(primary)
#            if not primary:
#                return []
#            pred = primary[0][1]
#            return [(a, b, ui.completion.TextEdit.TYPE_NORMAL) for a, b, _ in primary] + [(a, pred + b, ui.completion.TextEdit.TYPE_NEXT) for a, b, _ in secondary]
#        return merge
#
#    def _createCommonChain(self):
#        return [self.sortFilter]