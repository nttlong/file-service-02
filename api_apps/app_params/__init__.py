import ReCompact.api_input
from django.core.files.uploadedfile import InMemoryUploadedFile
class AppParam:
    LogoFile = InMemoryUploadedFile
    Token = (str,True)
    Name = (str,True)
    Domain = (str,True)
    """
    Tên ứng dụng
    """
    LoginUrl = (str,True)
    """
    Địa chỉ login
    """
    Description =str
    """
    Ghi chú
    """
    ReturnUrlAfterSignIn = (str,True)

    def __init__(self):
        pass
    def __getattr__(self, item):
        return  1