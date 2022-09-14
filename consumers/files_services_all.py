import files_servcies_upload
import files_services_upload_thumb_pdf
import files_services_upload_ocr_pdf
import files_services_upload_elastic
import files_services_upload_thumb_video
import files_services_upload_thumb_office
import files_services_ocr_image
import files_services_upload_thumb_image
if __name__ == '__main__':

    files_services_upload_thumb_pdf.consumer.start_and_join()
    files_services_upload_ocr_pdf.consumer.start_and_join()
    files_services_upload_elastic.consumer.start_and_join()
    files_services_upload_thumb_video.consumer.start_and_join()
    files_services_upload_thumb_office.consumer.start_and_join()
    files_services_ocr_image.consumer.start_and_join()
    files_services_upload_thumb_image.consumer.start_and_join()
    files_servcies_upload.consumer.run()

