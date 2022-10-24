import enig
import re


class TextProcessService(enig.Singleton):
    def __init__(self):
        self.patterns_vn = {
            '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
            '[đ]': 'd',
            '[èéẻẽẹêềếểễệ]': 'e',
            '[ìíỉĩị]': 'i',
            '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
            '[ùúủũụưừứửữự]': 'u',
            '[ỳýỷỹỵ]': 'y'}

    def vn_clear_accent_mark(self, content: str):
        """
            Convert from 'Tieng Viet co dau' thanh 'Tieng Viet khong dau'
            text: input string to be converted
            Return: string converted
            """
        output = content
        for regex, replace in self.patterns_vn.items():
            output = re.sub(regex, replace, output)
            # deal with upper case
            output = re.sub(regex.upper(), replace.upper(), output)
        return output