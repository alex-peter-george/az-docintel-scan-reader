class FormARecognizerClass():
    def __init__(self, func):
        # inject the document analysis function
        self.func = func

    def analyzeDocument(self):
        # parse the form and extract the content
        self.func()