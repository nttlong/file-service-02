import typing
class AppInfo:
    """
    Infomation of application, an application is one-one mapping to tanent
    """
    AppId:str
    """
    The name of application
    """
    Name:str
    Description: typing.Optional[str]
    Domain: typing.Optional[str]
    LoginUrl:typing.Optional[str]
    ReturnUrlAfterSignIn:typing.Optional[str]