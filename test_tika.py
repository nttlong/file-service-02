import os
import pathlib
check_path = os.path.join(str(pathlib.Path(__file__).parent),"enig_frames/services/ext_libs/icoextract")
print(check_path)
print(os.path.isfile(check_path))
print("-------------------")
# working_path= str(pathlib.Path(__file__).parent)
# os.environ['TIKA_SERVER_JAR'] =os.path.join(working_path,"tika-server","tika-server.jar")
# os.environ['TIKA_PATH'] = os.path.join(working_path,"tika-server")
# from tika import parser
#
# print(working_path)
# fx=r'test.docx'
#
# parsed_pdf = parser.from_file(fx)
# content =parsed_pdf['content']
# print(content)