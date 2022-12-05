import os
import pathlib
import pdfplumber
import fitz
import glob
import ocrmypdf


class PDFService:
    def __init__(self):
        self.processing_folder = os.path.abspath(
            os.path.join(pathlib.Path(__file__).parent.parent.parent.__str__(), "tmp", "pdf")
        )
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder, exist_ok=True)

    def get_image(self, file_path: str):
        pdf_file = file_path
        filename_only = pathlib.Path(pdf_file).stem
        image_file_path = os.path.join(self.processing_folder, f"{filename_only}.png")
        if os.path.isfile(image_file_path):
            return image_file_path
        if os.path.isfile(image_file_path):
            return image_file_path
        # To get better resolution
        zoom_x = 2.0  # horizontal zoom
        zoom_y = 2.0  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

        all_files = glob.glob(pdf_file)

        for filename in all_files:
            doc = fitz.open(filename)  # open document
            for page in doc:  # iterate through the pages
                pix = page.get_pixmap()  # render page to an image
                pix.save(image_file_path)  # store image as a PNG
                break  # Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
            break  # Hết vòng lặp luôn Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
        return image_file_path

    def has_text(self, pdf_file_path) -> bool:
        """
               Check is pdf file ready ORC?
               :param file_path:
               :return:
               """
        if not os.path.isfile(pdf_file_path):
            return True

        with pdfplumber.open(pdf_file_path) as pdf:
            """
            Check have pdf file been ORC?
            """
            if pdf.pages.__len__() == 0:
                """
                Nothing to do
                """
                return True
            for page in pdf.pages:
                text = page.extract_text()
                if text.__len__() > 0:
                    return True
            return False

    def ocr(self, pdf_file):
        """
                        Thuc hien ocr pdf file trong tien tring rieng biet
                        :param file_path:
                        :param out_put_file_path:
                        :return:
                        """
        file_name_only = pathlib.Path(pdf_file).stem
        out_put_file_path = os.path.join(self.processing_folder, f"{file_name_only}.pdf")
        fx = ocrmypdf.ocr(
            input_file=pdf_file,
            output_file=out_put_file_path,
            progress_bar=False,
            language="vie+eng",
            use_threads=False,
            skip_text=True,
            jobs=100,
            keep_temporary_files=True
        )
        return out_put_file_path
