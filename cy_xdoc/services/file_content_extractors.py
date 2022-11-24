import enig
import pathlib
import os
import sys
import tika


class FileContentExtractorService:
    def __init__(self):
        self.working_path = str(pathlib.Path(__file__).parent)
        self.ext_lib_folder= os.path.join(str(pathlib.Path(__file__).parent),"ext_libs")
        os.environ['TIKA_SERVER_JAR'] = os.path.join(self.ext_lib_folder, "tika-server.jar")
        os.environ['TIKA_PATH'] = self.ext_lib_folder
        if sys.modules.get("tika") is not None:
            import importlib
            importlib.reload(sys.modules["tika"])

    def get_text(self, file_path) -> (str, dict):
        """
        With Giga bytes file pdf, or other office file, need split to small doc with 100 pages oer doc
        :param file_path:
        :return:
        """

        import tika

        from tika import parser

        headers = {

        }
        ret = parser.from_file(file_path,  requestOptions={'headers': headers, 'timeout': 30000})
        # import psutil
        # import signal
        # for x in psutil.process_iter():
        #     if x.status() == 'sleeping' and x.__name__() == 'java':
        #         os.kill(x.pid, signal.SIGKILL)
        return ret['content'], ret['metadata']