from ui.Filter import EndingAggegator
from lm.Selection import *
from lm.Sorting import *
from ui.Filter import *
from lm.kenlm import Model as KenLMModel
import common.Tokenize


class Configuration:
    selector            = None
    sorter              = None
    filter              = None
    userInputModel      = None
    contextLength       = 2
    sentenceTokenizer   = common.Tokenize.SentenceTokenizer

class ConfigurationBuilder:
    _methodPrefix = "_create"
    def __getitem__(self, name):
        name = name[0].upper() + name[1:]
        return ConfigurationBuilder.__dict__[self._methodPrefix + name]()
    
    def _createDebug():
        result = Configuration()

        klm = KenLMModel("../sample-data/povidky.arpa")
        result.selector = UniformSelector("akát blýskavice cílovníci dálava erb Filipíny papír poprava".split())
        
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
    