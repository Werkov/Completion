from lm.origin import *


class Configuration:
    selector = None
    sorter = None
    userInputModel = None
    contextLength = 2

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
    