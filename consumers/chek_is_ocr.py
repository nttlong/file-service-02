import pdfplumber
file_path=r"C:\Users\nttlong\Downloads\test2.pdf"
with pdfplumber.open(file_path) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()
    print(text)