from .Model_Files import DocUploadRegister as __DocUploadRegister__, FsFile as __FsFile__, FsChunks as __FsChunks__
from .ModelApps import sys_applications as __sys_applications__
from .Model_Users import User
from .Model_Container import ZipContainer as __ZipContainer__
from .Model_SSO import SSO as __SSO__
Fs_File = __FsFile__()
Files = __DocUploadRegister__()
FsChunks = __FsChunks__()
"""
Mongodb Document của phần Upload File
"""
Apps =__sys_applications__()
"""
Mongodb của phần application
"""
Users = User()
"""
Mongodb của phần quản lý user
"""
Zip_Container =__ZipContainer__()
"""
Mongodb của phần ZIP
Thông tin của các file nằm trong file zip sẽ được đóng gói ở đây
"""
SSOs = __SSO__()