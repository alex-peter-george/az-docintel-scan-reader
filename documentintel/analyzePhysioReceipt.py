"""
This code sample shows Prebuilt Read operations with the Azure Form Recognizer client library. 
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Document Intelligence (formerly Form Recognizer) SDKs
https://learn.microsoft.com/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?pivots=programming-language-python
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import csv
from datetime import datetime
from tempfile import NamedTemporaryFile
import shutil
import uuid

from dotenv import load_dotenv
import os

"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""

# Load the .env file
load_dotenv()

# Get the value of an environment variable
key = os.getenv('API_KEY')
endpoint = os.getenv('DOCINTEL_URL')

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

def analyze_read(row):
    # formUrl = row['DocumentURL']
    formPath = f"forms/{row['DocumentFileName']}"
    print('*** Analyze document:',row['DocumentName'])
    
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    
    with open(formPath, "rb") as form:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-layout", document=form, locale="en-US")

    # poller = document_analysis_client.begin_analyze_document_from_url(
    #         "prebuilt-read", formUrl)
    result = poller.result()

    row['ExtractedContent'] = '<see output text file>' #result.content.encode('unicode_escape')
    outstring = "****Document content:\n"
    outstring += "{}\n".format(result.content)
    outstring += '\n'

    for idx, style in enumerate(result.styles):
        row['IsHandwritten'] = "Document contains {} content".format(
                "handwritten" if style.is_handwritten else "no handwritten"
            )

    for page in result.pages:
        outstring += "****Analyzing Read from page {}\n".format(page.page_number)

        for line_idx, line in enumerate(page.lines):
            outstring += ".......Line # {} has text content '{}' within bounding box '{}'\n".format(
                    line_idx,
                    line.content,
                    format_bounding_box(line.polygon)
                )
        outstring += '\n'
        confidenceLevel = "****Extracted words confidence levels\n"
        for word in page.words:
            confidenceLevel = confidenceLevel + ".......{}:{}\n".format(
                    word.content, word.confidence
                )
        outstring += confidenceLevel
        
        # Generate a random UUID
        docguid = uuid.uuid4()   
        row['DocumentId'] = docguid 
        row['ConfidenceLevels'] = '<see output text file>' #confidenceLevel
    
    # writes analysis results to text file
    filepath = f'analysisresults/{docguid}.txt'
    with open(filepath, 'w',encoding='utf-8') as file:
        # Write the string to the file
        file.write(outstring)

    print("*** Finished analysis")
    row['LastAnalyseDate'] = f'runtime: {datetime.now()}'
    return row

# Define the condition and update function
def condition(row):
    return row[0] == 1


def extractContent():
    filename = 'documents.csv'
    tempfile = NamedTemporaryFile(mode='w', newline='', delete=False)

    fields = ['RunAnalysis','DocumentId','DocumentName','DocumentFileName','DocumentURL','ExtractedContent','IsHandwritten','ConfidenceLevels','LastAnalyseDate']

    with open(filename, 'r') as csvfile, tempfile:
        reader = csv.DictReader(csvfile, fieldnames=fields)
        writer = csv.DictWriter(tempfile, fieldnames=fields)
        for row in reader:
            if row['RunAnalysis'] == '2':
                row = analyze_read(row)
            row = {'RunAnalysis': row['RunAnalysis'], 
                   'DocumentName': row['DocumentName'], 
                   'DocumentId': row['DocumentId'], 
                   'DocumentFileName': row['DocumentFileName'], 
                   'DocumentURL': row['DocumentURL'], 
                   'ExtractedContent': row['ExtractedContent'], 
                   'DocumentURL': row['DocumentURL'], 
                   'IsHandwritten': row['IsHandwritten'],
                   'ConfidenceLevels': row['ConfidenceLevels'],
                   'LastAnalyseDate': row['LastAnalyseDate']}
            writer.writerow(row)

    shutil.move(tempfile.name, filename)
