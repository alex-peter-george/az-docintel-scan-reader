import inject
from documentintel.formARecognizerClass import FormARecognizerClass
from documentintel.physioReceiptRecognizerClass import PhysioReceiptRecognizerClass
from documentintel.analyzeOlsgFormA import extractContent as extractContentOlsg
from documentintel.analyzePhysioReceipt import extractContent as extractContentPhysio

def configure_injection(binder):
    # configure the actual injections of the two document analysis functions
    binder.bind(FormARecognizerClass, FormARecognizerClass(extractContentOlsg))
    binder.bind(PhysioReceiptRecognizerClass, PhysioReceiptRecognizerClass(extractContentPhysio))

if __name__ == "__main__":
    inject.configure(configure_injection)

    # extract the content from Olsg FormA document
    formARecognizer_instance = inject.instance(FormARecognizerClass)
    formARecognizer_instance.analyzeDocument()

    # extract the content from Physio Therapy receipt document
    physyioReceiptRecognizer_instance = inject.instance(PhysioReceiptRecognizerClass)
    physyioReceiptRecognizer_instance.analyzeDocument()