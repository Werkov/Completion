import sys
sys.path.append("../")


class LangModel:
    """
    Language model that assigns probabilites to tokens
    according to known history of a text.
    """

    def vocabulary(self):
        """Return container of tokens representing words in model's vocabulary."""
        return frozenset()

    def reset(self, context=[]):
        """Set the model to the state reached by the sequence of given words or to the begin-sentence state."""
        pass

    def probability(self, token, changeContext=True):
        """
        Return log2 probability of word in model's current state.
        Word is used to change the state of model unless specified changeState = False.

        For unknown words -100 is returned.
        """
        return -100

    def shift(self, token):
        """
        Change model's current state with given token.
        """
        self.probability(token, True)



