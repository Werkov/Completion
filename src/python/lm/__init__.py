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
        """Return log2 probability of word in model's current state.
        Word is used to change the state of model unless specified changeState = False.

        For unknown words -100 is returned.
        """
        return -100

    def shift(self, token):
        """Change model's current state with the given token.
        """
        self.probability(token, True)


class Selector:
    """According to the current context returns candidates for possible
    continuation of the text.
    """

    def reset(self):
        """Set initial context."""
        pass

    def shift(self, token):
        """Change context with the given token."""
        pass

    def suggestions(self, prefix):
        """Suggestions for current context, filtered by the prefix."""
        return ([], 0)


