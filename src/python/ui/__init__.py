import common.tokenize

class ContextHandler:
    """
    Keep components with state synchronized with input text.

    Components (listeners) are considered to have a state that can be changed with incoming
    token in only forward direction. Normally, state is changed gradually as the
    text is typed; in the case of cursor moves/correcting text, components are
    reset to the beginning state and "shifted" to current state.

    Listeners must have `shift(token)` and `reset()` methods.
    """
    def __init__(self, tokenizer, sentencer, normalizer=None):
        self.context = []
        self.prefix = ""
        self._tokenizer = tokenizer
        self._sentencer = sentencer
        self._normalizer = common.tokenize.TokenNormalizer() if not normalizer else normalizer
        self._listeners = []

    def addListener(self, listener):
        """Register a listener to keep in sync with text."""
        self._listeners.append(listener)

    def update(self, text):
        """Call with the text that should be the new context."""
        self._tokenizer.reset(text, True)
        self._sentencer.reset(self._tokenizer)
        self._normalizer.reset(self._sentencer)

        tokens = list(self._normalizer)
        self.prefix = self._tokenizer.uncompleteToken[0] if self._tokenizer.uncompleteToken else ""

        if len(tokens) < len(self.context) or tokens[:len(self.context)] != self.context:
            print("reseting whole model")
            self._reset()
            self.context = []

        newTokens = tokens[len(self.context):]
        if newTokens and newTokens[-1] == common.tokenize.TOKEN_END_SENTENCE:
            newTokens.append(common.tokenize.TOKEN_BEG_SENTENCE)

        for token in newTokens:
            self._shift(token)
        self.context += newTokens

    def _reset(self):
        for listener in self._listeners:
            listener.reset()

    def _shift(self, token):
        for listener in self._listeners:
            listener.shift(token)

    def reset(self):
        self.context = []
        self.prefix = ""
        self._reset()

    def shift(self, token):
        self.context.append(token)
        self._shift(token)
