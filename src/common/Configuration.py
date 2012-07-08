import ui.Filter
from lm.Selection import *
from lm.Sorting import *
from lm.kenlm import Model as KenLMModel
import common.Tokenize


class Configuration:
    _cache              = dict()
    _params             = dict()
    _factoryPrefix      = "_create"

    def __init__(self, **kwargs):
        self._params = kwargs
        
    def __getattr__(self, name):
        if name not in self._cache:
            try:
                factoryMethod = self.__getattribute__(self._factoryPrefix + name[0].upper() + name[1:])
                self._cache[name] = factoryMethod()
            except KeyError:
                raise AttributeError(name)

        return self._cache[name]


class DebugConfiguration(Configuration):
    def _createFilterChain(self):
        return [
            self.probabilityFilter,
            self.sortFilter,
            self.limitFilter,
            self.capitalizeFilter
        ]
    
    def _createSelector(self):
        return UniformSelector(self.languageModel.vocabulary())

    def _createContextHandler(self):
        contextHandler = ui.Completion.ContextHandler(self.stringTokenizer, self.sentenceTokenizer)
        contextHandler.addListener(self.selector)
        contextHandler.addListener(self.languageModel)
        return contextHandler

    def _createLanguageModel(self):
        return KenLMModel("../sample-data/povidky.arpa")

    # suggestions filters
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


class ConfigurationBuilder:
    _methodPrefix = "_create"
    def __getitem__(self, name):
        name = name[0].upper() + name[1:]
        return ConfigurationBuilder.__dict__[self._methodPrefix + name]()
    
    def _createDebug():
        result = Configuration()

        result.languageModel = KenLMModel("../sample-data/povidky.arpa")
        result.selector = UniformSelector(result.languageModel.vocabulary())
        #result.selector = UniformSelector("akát blýskavice cílovníci dálava erb Filipíny hrachovina ibis jasmín bílý krákorá lupíneček mává národ papír poprava".split())
        
        return result

    def _createBidebug():
        result = Configuration()

        klm = KenLMModel("../sample-data/povidky.arpa")
        slm = SimpleLangModel(open("../sample-data/povidky.txt"))
        result.selector = SuggestionSelector(bigramDict=slm.search)
        result.sorter = SuggestionSorter(klm)
        result.filter = EndingAggegator()

        return result

    def _createWiki():
        result = Configuration()

        klm = KenLMModel("../large-data/wiki.ces.arpa")
        slm = SimpleLangModel(open("../sample-data/povidky.txt"))
        result.selector = SuggestionSelector(bigramDict=slm.search)
        result.sorter = SuggestionSorter(klm)
        #result.filter = EndingAggegator()

        return result
    def _createWikivoc():
        result = Configuration()

        klm = KenLMModel("../large-data/wiki.ces.arpa")
        slm = SimpleLangModel(open("../sample-data/povidky.txt"))
        result.selector = SuggestionSelector(dict=klm.dictionary)
        result.sorter = SuggestionSorter(klm)
        #result.filter = EndingAggegator()

        return result
    