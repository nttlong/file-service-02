from .Model_Files import DocUploadRegister, FsFile
from .ModelApps import sys_applications
from .Model_Users import User
from .Model_Container import ZipContainer

Fs_File = FsFile()
Files = DocUploadRegister()
"""
Mongodb Document của phần Upload File
"""
Apps =sys_applications()
"""
Mongodb của phần application
"""
Users = User()
"""
Mongodb của phần quản lý user
"""
Zip_Container =ZipContainer()
"""
Mongodb của phần ZIP
Thông tin của các file nằm trong file zip sẽ được đóng gói ở đây
"""