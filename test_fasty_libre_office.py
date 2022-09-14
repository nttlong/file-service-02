import os.path

import fasty_libre_office
libre_office_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
profile_dir =f"C:\dj-apps-2022-05-25\jd-apps\consumers\LibreOfficeTempProfiles"
file =r"\\192.168.18.36\fscrawler-es7-2.9\docs\app-test-dev\ca4a9a9d-a102-47ec-9254-f1d7300f8c3e.pdf"
dir =f"C:\dj-apps-2022-05-25\jd-apps\out_put"
p_dir =r"\\172.16.7.81\DocStoresEOffice"

cmd = fasty_libre_office.build_command_line(
    libre_office_path,
    profile_dir,
    file_path=file,
    out_put_dir=dir,
    extent_file="txt:Text "

)

print(cmd)
file =os.path.join(p_dir,'OpenEdx.docx')
file =os.path.join(p_dir,'ok.xls')
ret = fasty_libre_office.covert_to_text_file(
    libre_office_path,
    profile_dir,
    file_path=file,
    out_put_dir=dir

)
print(ret)
#"C:\Program Files\LibreOffice\program\soffice.exe" --headless --convert-to png  --accept=Negotiate=0,ForceSynchronous=1; -env:UserInstallation=file:///C:/dj-apps-2022-05-25/jd-apps/consumers/LibreOfficeTempProfiles/0ae000b3-7a67-4b74-9498-b4388e1f2691 --outdir C:\dj-apps-2022-05-25\jd-apps\out_put \\192.168.18.36\fscrawler-es7-2.9\docs\app-test-dev\ca4a9a9d-a102-47ec-9254-f1d7300f8c3e.pdf
#soffice.exe --headless --convert-to png  --accept=Negotiate=0,ForceSynchronous=1; -env:UserInstallation=file:///C:/dj-apps-2022-05-25/jd-apps/consumers/LibreOfficeTempProfiles/0ae000b3-7a67-4b74-9498-b4388e1f2691 --outdir C:\dj-apps-2022-05-25\jd-apps\out_put \\192.168.18.36\fscrawler-es7-2.9\docs\app-test-dev\ca4a9a9d-a102-47ec-9254-f1d7300f8c3e.pdf
#soffice.exe --headless --convert-to png   -env:UserInstallation=file:///C:/dj-apps-2022-05-25/jd-apps/consumers/LibreOfficeTempProfiles/0ae000b3-7a67-4b74-9498-b4388e1f2691 --outdir C:\dj-apps-2022-05-25\jd-apps\out_put \\192.168.18.36\fscrawler-es7-2.9\docs\app-test-dev\ca4a9a9d-a102-47ec-9254-f1d7300f8c3e.pdf