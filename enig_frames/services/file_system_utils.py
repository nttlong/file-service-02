import enig
import os
import pathlib



class FileSystemUtils(enig.Singleton):

    def get_file_extenstion(self, file_path) -> str:
        ret = os.path.splitext(file_path)[1]
        return ret[1:]

    def get_file_name_only(self, file_path):
        return pathlib.Path(file_path).stem

    def get_mime_type(self, file_path: str) -> str:
        import fasty.mime_data
        import mimetypes
        ret, _ = mimetypes.guess_type(file_path)
        return ret
