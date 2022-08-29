import datetime
import os
import shutil
import time
dir = r"\\192.168.18.36\Share\DjangoWeb"
if not os.path.isdir(dir):
    raise Exception(f"'{dir}' was not found")
while True:
    sub_dirs =list(os.walk(dir))
    for x in sub_dirs:
        if isinstance(x,tuple):
            r_dir = x[0]
            p_dir = x[1]
            p_files =x[2]
            if isinstance(p_files,list):
                for f in p_files:
                    full_file_path = os.path.join(r_dir,f)
                    stat = os.stat(full_file_path)
                    created_time= datetime.datetime.fromtimestamp(stat.st_ctime)
                    n= datetime.datetime.now()-created_time
                    if n.days>2:
                        try:
                            os.remove(full_file_path)
                        except IOError as e:
                            print(e)
                        finally:
                            print(f"'{full_file_path}' is lockec")

                    print(stat)
    time.sleep(500)
