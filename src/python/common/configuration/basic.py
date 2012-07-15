__all__ = [
    'Simple',
    'Extended'
]

from common.configuration import Configuration as Configuration

import common.Tokenize
import ui.Completion
import ui.Filter
import lm.Selection
from lm.kenlm import Model as KenLMModel


class Simple(Configuration):
    description = """KenLM for probability evaluation and its vocabulary for uniform selector."""
    aliases     = ['s']

    def configureArgParser(parser):
        parser.add_argument('-lm', help='path to KenLM model file', required=True)
    

    def _createFilterChain(self):
        return [
            self.addedCharsFilter,
            self.probabilityFilter,
            self.sortFilter,
            self.limitFilter,
            self.capitalizeFilter
        ]
    
    def _createSelector(self):
        return lm.Selection.UniformSelector(self.languageModel.vocabulary())

    def _createContextHandler(self):
        contextHandler = ui.Completion.ContextHandler(self.stringTokenizer, self.sentenceTokenizer)
        contextHandler.addListener(self.selector)
        contextHandler.addListener(self.languageModel)
        return contextHandler

    def _createLanguageModel(self):        
        return KenLMModel(self._params['lm'])

    # suggestions filters
    def _createAddedCharsFilter(self):
        return ui.Filter.AddedCharacters(self.contextHandler)

    def _createCapitalizeFilter(self):
        return ui.Filter.SentenceCapitalizer(self.contextHandler)

    def _createProbabilityFilter(self):
        return ui.Filter.ProbabilityEstimator(self.languageModel)

    def _createLimitFilter(self):
        return ui.Filter.SuggestionsLimiter()

    def _createSortFilter(self):
        def sortFilter(suggestions):
            return sorted(suggestions, key=lambda sugg: (sugg[1], len(sugg[0])), reverse=True)
        return sortFilter

    # tokenization
    def _createStringTokenizer(self):
        return common.Tokenize.StringTokenizer()

    def _createSentenceTokenizer(self):
        return common.Tokenize.SentenceTokenizer()

class Extended(Simple):
    description = """KenLM for probability evaluation and another's KenLM vocabulary for
        uniform selector."""
    aliases     = ['e']

    def configureArgParser(parser):
        parser.add_argument('-lm',  help='path to probability KenLM model file', required=True)
        parser.add_argument('-voc', help='path to vocabulary KenLM file', required=True)

    
    def _createSelector(self):
        return lm.Selection.UniformSelector(KenLMModel(self._params['voc']).vocabulary())
    def _createLanguageModel(self):
        return KenLMModel(self._params['lm'])

