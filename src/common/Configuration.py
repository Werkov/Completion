from ui.Filter import EndingAggegator
from lm.origin import *
from lm.Selection import *
from lm.Sorting import *
from ui.Filter import *


class Configuration:
    selector        = None
    sorter          = None
    filter          = None
    userInputModel  = None
    contextLength   = 2

class ConfigurationBuilder:
    _methodPrefix = "_create"
    def __getitem__(self, name):
        name = name[0].upper() + name[1:]
        return ConfigurationBuilder.__dict__[self._methodPrefix + name]()
    
    def _createDebug():
        result = Configuration()

        klm = KenLMModel("../sample-data/povidky.arpa")
        result.selector = SuggestionSelector(dict=klm.dictionary)
        result.sorter = SuggestionSorter(klm)
        
        return result

    def _createBidebug():
        result = Configuration()

        klm = KenLMModel("../sample-data/povidky.arpa")
        slm = SimpleLangModel(open("../sample-data/povidky.txt"))
        result.selector = SuggestionSelector(bigramDict=slm.search)
        result.sorter = SuggestionSorter(klm)
        result.filter = EndingAggegator()

        return result
    