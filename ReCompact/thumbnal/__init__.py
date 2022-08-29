from moviepy.editor import *
from matplotlib import pyplot as plt
from PIL import Image
import io
import matplotlib
def video_create_thumb(in_put,scale_witdh,scale_height,second=5)->io.BytesIO:
    """
    Hàm này sẽ cắt 1 khung trong file video
    Bóp lại vừa vặn với khung scale_width,scale_height
    :param in_put:
    :param scale_witdh:
    :param scale_height:
    :param second:
    :return:
    """
    clip= VideoFileClip(
        in_put
    )
    second,_ = divmod(clip.duration, 2)
    """
    Lấy khung giữa
    """
    clip = clip.subclip(second, second)
    frame = clip.get_frame(0)
    height,width,_ = frame.shape
    rate = scale_witdh/width # Mac dinh la bop theo chieu rong
    if height>width: # Nhung vi anh co chieu cao lon hon chieu rong
        rate = scale_height/height # Nen quye dinh la bop theo chieu chie doc
    new_witdth,new_height= int(width*rate),int(height*rate)
    # res = cv2.resize(frame, dsize=(new_witdth,new_height)) #, interpolation=cv2.INTER_CUBIC)
    # img = Image.fromarray(res, 'RGB')
    # img.save('my.png')
    img = Image.fromarray(frame, 'RGB')
    new_img = img.resize(size =(new_witdth, new_height))
    img_byte_arr = io.BytesIO()
    new_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    ret = io.BytesIO(img_byte_arr)
    new_img.close()
    img.close()
    clip.close()

    return ret