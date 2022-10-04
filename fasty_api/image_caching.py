import os.path
import pathlib
import threading

import pymongo.database

working_dir =str(pathlib.Path(__file__).parent.parent)
thumb_cach_dir= os.path.join(working_dir, "cache", "images")
if not os.path.isdir(thumb_cach_dir):
    os.makedirs(thumb_cach_dir,exist_ok=True)

__cach__ = {}
__lock__ = threading.Lock()
def check(directory:str):
    global __lock__
    global __cach__
    if __cach__.get(directory.lower()) is not None:

        return __cach__.get(directory.lower())
    keys = directory.split('/')
    key = keys[keys.__len__() - 2]
    _, file_extension = os.path.splitext(directory)
    file_path = os.path.join(thumb_cach_dir, f"{key}.{file_extension}")

    if os.path.isfile(file_path):
        __cach__[directory.lower()]=file_path
        return file_path
    return None

import gridfs
def sync(file_id,db:pymongo.database.Database,directory:str):
    global thumb_cach_dir
    global  __cach__
    def run():
        #fs:gridfs.grid_file.GridOut
        keys = directory.split('/')
        key= keys[keys.__len__()-2]
        _, file_extension = os.path.splitext(directory)
        file_path = os.path.join(thumb_cach_dir,f"{key}.{file_extension}")


        fs = gridfs.GridFS(db)
        m_file =fs.get(file_id);
        ret= m_file.read()
        with open(file_path,'wb') as f:
            f.write(ret)
        m_file.close()
        __cach__[directory.lower()] = file_path
    threading.Thread(target=run,args=()).start()
