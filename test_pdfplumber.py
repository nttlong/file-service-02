import requests
import pdfplumber
file =r"\\192.168.18.36\fscrawler-es7-2.9\docs\app-test-dev\ca4a9a9d-a102-47ec-9254-f1d7300f8c3e.pdf"
with pdfplumber.open(file) as pdf:
    page=pdf.pages[0]
    text=page.extract_text()
# from pdfminer.high_level import extract_text
# text  = extract_text(file, 'rb')
print(text)

pdfObject = open(file, 'rb')
from PyPDF2 import PdfFileReader
# creating a pdf reader object
pdfReader = PdfFileReader(pdfObject)

# Extract and concatenate each page's content
text=''
for i in range(0,pdfReader.numPages):
    # creating a page object
    pageObject = pdfReader.getPage(i)
    # extracting text from page
    text += pageObject.extractText()
print(text)