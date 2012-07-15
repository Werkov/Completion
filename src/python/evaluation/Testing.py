from common.Tokenize import TextFileTokenizer

class AutomatedTest:
    def __init__(self, file):
        self.file = file
        self.metrics = []

    def runTest(self):
        tokenizer = TextFileTokenizer(self.file)
        history = ["", ""] # TODO
        for (_, token) in tokenizer:
            for metric in self.metrics:
                metric.measure(history, token)
            history.append(token)

    def result(self):
        print("{}:\t{}".format(self.file.name, "\t".join([str(m.result()) for m in self.metrics])))