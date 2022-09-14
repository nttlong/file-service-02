import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
__working_dir__ = None
__info__ = {}
__lock__ = threading.Lock()
__template__cache__ ={}
__observer__ = Observer()
__app_url_path__ ={}

class __cach_handler__(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        global __template__cache__
        global __info__
        __template__cache__={}
        __info__ ={}
def set_working_dir(working_dir):
    global __working_dir__
    global __observer__
    __working_dir__ =working_dir
    event_handler = __cach_handler__()
    __observer__.schedule(event_handler, working_dir, recursive=True)
    __observer__.start()
class AppInfo:
    def __init__(self,app_name):
        import os
        global __working_dir__
        self.app_name = app_name
        self.base_dir = os.path.join(__working_dir__,app_name)
        self.template_path = os.path.join(self.base_dir,"html")
    def get_template_content(self,rel_path):
        import os
        file_path=os.path.join(self.template_path,rel_path)
        txt = ""
        with open(file_path,'r',encoding='utf-8') as f:
            txt =f.readline()
        return  txt


def get_application(name_of_view):
    app_name = name_of_view.split('.')[0]
    global __info__
    if not __info__.get(app_name):
        __lock__.acquire()
        __info__[app_name]= AppInfo(app_name)
        __lock__.release()
    return __info__[app_name]

# class __obj_handler__:
#     def __init__(self,app_name,fn):
#         self.app_name = app_name
#         self.fn =fn
#     def handler(self,request):
#         self.fn(request)

class __request__render__:
    def __init__(self,request,fn_name):
        self.request =request
        self.fn_name =fn_name
        self.__model__ = {}
    def model(self,data):
        self.__model__ =data
        return self
    def render(self):
        from django.template import Context, Template
        from django.http import HttpResponse
        global __template__cache__
        global __lock__
        html_template = ""
        if not __template__cache__.get(self.fn_name):
            __lock__.acquire()
            file_path = self.request.view_template

            with open(self.request.full_template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
            __template__cache__[self.fn_name] = html_template
            __lock__.release()
        else:
            html_template =__template__cache__.get(self.fn_name)

        t = Template(html_template)
        c = Context(self.__model__)
        html = t.render(c)
        return HttpResponse(html,content_type='text/html')






def template(path_to_template,*args,**kwargs):

    import sys
    def ret(*_args,**_kwargs):
        fn = _args[0]
        module_name = fn.__module__
        app_name = fn.__module__.split('.')[0]
        def handler(*_args,**_kwargs):
            request=_args[0]
            global __working_dir__
            global __app_url_path__
            import web.settings
            import os
            setattr(request, "host_url", web.settings.ROOT_URL)
            setattr(request, "full_url", web.settings.ROOT_URL+"/"+request.path)
            setattr(request,"app_name",app_name)
            setattr(request, "view_template", path_to_template)
            setattr(request, "app_dir",os.path.join(__working_dir__,app_name))
            setattr(request, "full_template_path", os.path.join(__working_dir__, app_name,"html",path_to_template))
            setattr(request,"template",__request__render__(request,fn.__name__))
            setattr(request,"app_url",__app_url_path__[app_name])
            setattr(request, "full_app_url", web.settings.ROOT_URL+"/"+__app_url_path__[app_name])
            return fn(request)
        # return fn


        # setattr(sys.modules[fn.__module__], fn.__name__,handler)

        return handler
    return ret
