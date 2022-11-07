import re_quicky

class Application:
    Name:str


@re_quicky.handle_get("{app_name}/images")
def register(app_name:str )->Application:
    return Application(

    )