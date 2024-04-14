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
    
        position_inx = 0
        work20hr_inx = 0
        work400hr_inx = 0
        publicsec_inx = 0
        reserve_inx = 0

        outstring += "\n****Extract user selections in all checkboxes\n"

        index = 0
        for para in result.paragraphs:
            if ('3. What is the name of your position' in para.content):
                position_inx = index
            if ('5. Will you (do you expect to) work at least 20 hours' in para.content):
                work20hr_inx = index
            if ('6. Will you (do you expect to) work at least 400 hours' in para.content):
                work400hr_inx = index
            if ('8. Is your organization a broader public sector organization' in para.content):
                publicsec_inx = index
            if ('8a. Does your organization operate on a First Nations reserve' in para.content):
                reserve_inx = index
            index = index + 1

        # get selected position(s)
        if (position_inx > 0):
            position_lst = result.paragraphs[position_inx+1:position_inx+7]
            outstring += '**Selection question: 3. What is the name of your position/occupation with this employer?\n'
            for line in position_lst:
                outstring += ".......{}\n".format(line.content)

        # get selected 20 hrs/month committment
        if (work20hr_inx > 0):
            work20hr_lst = result.paragraphs[work20hr_inx+1:work20hr_inx+3]
            outstring += '**Selection question: 5. Will you (do you expect to) work at least 20 hours a month?\n'
            for line in work20hr_lst:
                outstring += ".......{}\n".format(line.content)

        # get selected 400 hrs/6-month committment
        if (work400hr_inx > 0):
            work400hr_lst = result.paragraphs[work400hr_inx+1:work400hr_inx+3]
            outstring += '**Selection question: 6. Will you (do you expect to) work at least 400 hours during the six months following your start date?\n'
            for line in work400hr_lst:
                outstring += ".......{}\n".format(line.content)
        
        # get selected public sector organization
        if (publicsec_inx > 0):
            publicsec_lst = result.paragraphs[publicsec_inx+1:publicsec_inx+3]
            outstring += '****Selection question: 8. Is your organization a broader public sector organization under the Broader Public Sector Accountability Act?\n'
            for line in publicsec_lst:
                outstring += ".......{}\n".format(line.content)

        # get selected organization opearates on reserve
        if (reserve_inx > 0):
            reserve_lst = result.paragraphs[reserve_inx+1:reserve_inx+3]
            outstring += '**Selection question: 8a. Does your organization operate on a First Nations reserve or primarily serve First Nations, Metis or Inuit communities?\n'
            for line in reserve_lst:
                outstring += ".......{}\n".format(line.content)
    
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
            if row['RunAnalysis'] == '1':
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
