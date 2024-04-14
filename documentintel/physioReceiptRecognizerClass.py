class PhysioReceiptRecognizerClass():
    def __init__(self, func):
        self.func = func

    def analyzeDocument(self):
        # parse the form and extract the content
        self.func()