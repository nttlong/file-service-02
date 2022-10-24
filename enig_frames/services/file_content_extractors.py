import enig
import pathlib
import os
import sys
import tika


class FileContentExtractorService(enig.Singleton):
    def __init__(self):
        self.working_path = str(pathlib.Path(__file__).parent)
        os.environ['TIKA_SERVER_JAR'] = os.path.join(self.working_path, "tika-server", "tika-server.jar")
        os.environ['TIKA_PATH'] = os.path.join(self.working_path, "tika-server")
        if sys.modules.get("tika") is not None:
            import importlib
            importlib.reload(sys.modules["tika"])

    def get_text(self, file_path) -> (str, dict):
        from tika import parser
        ret = parser.from_file(file_path)
        return ret['content'], ret['metadata']
