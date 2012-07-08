from ui.Filter import EndingAggegator
from lm.Selection import *
from lm.Sorting import *
from lm.kenlm import Model as KenLMModel
import common.Tokenize


class Configuration:
    selector            = None
    sentenceTokenizer   = common.Tokenize.SentenceTokenizer
    languageModel       = None

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
    