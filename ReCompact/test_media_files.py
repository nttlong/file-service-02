import ReCompact.media_files.pdf
import re_process.config
ReCompact.media_files.pdf.convert_to_image(
    in_put=r"\\192.168.18.36\Share\DjangoWeb\temp\app-test-dev\1bab62ee-3c38-4473-bbbc-496f4a82d7b5.pdf",
    out_put= r"\\192.168.18.36\Share\DjangoWeb\temp_thumb\test001.jpg",
    poppler_path= re_process.config.poppler_path
)
print("Xong")