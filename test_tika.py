from tika import parser
fx=r'test.docx'
parsed_pdf = parser.from_file(fx)
content =parsed_pdf['content']
print(content)