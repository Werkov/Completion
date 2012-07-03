class SuggestionSorter:
    def __init__(self, languageModel):
        self.languageModel = languageModel
    def getSortedSuggestions(self, context, suggestions):
        tips = []
        for token in suggestions:
            prob = self.languageModel.probability(token, False)
            tips.append((token, prob))

        tips.sort(key=lambda pair: -pair[1])
        return tips

