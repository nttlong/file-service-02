import os
import uuid
import subprocess
def build_command_line(
        libre_office_path,
        user_profile_dir,
        file_path,
        out_put_dir,
        extent_file
        ):
    user_profile_id = str(uuid.uuid4())  # Tạo user profile giả, nếu kg có điều này LibreOffice chỉ tạo 1 instance,
    # kg xử lý song song được
    full_user_profile_path = os.path.join(user_profile_dir, user_profile_id)
    uno = f"Negotiate=0,ForceSynchronous=1;"
    arg = f"--outdir {out_put_dir} {file_path.replace(os.sep, '/')}"
    arg_list = [
        f'"{libre_office_path}"',

        "--headless",
        f"--convert-to {extent_file}",
        f"--accept={uno}",
        f"-env:UserInstallation=file:///{full_user_profile_path.replace(os.sep, '/')}",
        arg
    ]
    full_comand_line = " ".join(arg_list)
    # full_comand_line = f'"{config.libre_office_path}"  --convert-to png --outdir {out_put_dir} -env:UserInstallation=file:///{full_user_profile_path.replace(os.sep, "/")} '
    # full_comand_line =r'"C:\Program Files\LibreOffice\program\soffice.exe"  --convert-to png --outdir C:\test C:\test\x.docx -env:UserInstallation=file:///C:/dj-apps-2022-05-25/jd-apps/consumers/LibreOfficeTempProfiles/xxx --headless --accept=Negotiate=0,ForceSynchronous=1;'
    # p = subprocess.Popen(full_comand_line, shell=False)

    # ret = p.communicate()  # Đợi
    return full_comand_line

def covert_to_text_file(
        libre_office_path,
        user_profile_dir,
        file_path,
        out_put_dir
        ):
    user_profile_id = str(uuid.uuid4())  # Tạo user profile giả, nếu kg có điều này LibreOffice chỉ tạo 1 instance,
        # kg xử lý song song được
    full_user_profile_path = os.path.join(user_profile_dir, user_profile_id)
    uno = f"Negotiate=0,ForceSynchronous=1;"
    if not os.path.isdir(out_put_dir):
        os.makedirs(out_put_dir)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"'{file_path}' was not found")
    arg = f"--outdir { out_put_dir} {file_path.replace(os.sep,'/')}"
    arg_list = [
        f'"{libre_office_path}"',

        "--headless",
        "--convert-to txt:Text",
        f"--accept={uno}",
        f"-env:UserInstallation=file:///{full_user_profile_path.replace(os.sep, '/')}",
        arg
    ]
    full_comand_line = " ".join(arg_list)
    p = subprocess.Popen(full_comand_line  , shell=False)


    ret=p.communicate() # Đợi
    return ret