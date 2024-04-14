import inject
from documentintel.formARecognizerClass import FormARecognizerClass
from documentintel.physioReceiptRecognizerClass import PhysioReceiptRecognizerClass
from documentintel.analyzeOlsgFormA import extractContent as extractContentOlsg
from documentintel.analyzePhysioReceipt import extractContent as extractContentPhysio

def configure_injection(binder):
    binder.bind(FormARecognizerClass, FormARecognizerClass(extractContentOlsg))
    binder.bind(PhysioReceiptRecognizerClass, PhysioReceiptRecognizerClass(extractContentPhysio))

if __name__ == "__main__":
    inject.configure(configure_injection)

    formARecognizer_instance = inject.instance(FormARecognizerClass)
    formARecognizer_instance.analyzeDocument()

    physyioReceiptRecognizer_instance = inject.instance(PhysioReceiptRecognizerClass)
    physyioReceiptRecognizer_instance.analyzeDocument()