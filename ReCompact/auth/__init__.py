def validator(is_public=False, *args,**kwargs):
    from django.http import HttpResponse
    import json
    current_handler = None
    def ret(*_args,**_kwargs):
        import sys
        old_handler = _args[0]
        setattr(current_handler,"__original__handler__",old_handler)
        app_name = old_handler.__module__.split('.')[0]
        ret_handler = None
        def handler(*__args,**__kwargs):
            import ReEngine
            app_urls = sys.modules[app_name + ".urls"]
            ch= current_handler
            rh= ret_handler
            request = __args[0]
            if request.session.get('current_user',None):
                setattr(request,"current_user",request.session["current_user"])
                setattr(request, "is_aut", True)
            else:
                setattr(request, "current_user", None)
                setattr(request, "is_aut", False)
            root_api_path = ReEngine.info["APPS"][app_name]
            setattr(request,"root_api_path",root_api_path)
            tenant_app = None
            for m in app_urls.urlpatterns:
                r = m.pattern.match(request.path)
                if r:
                    tenant_app = r[-1:][0].get('app_name')
                    break
            if not is_public:
                import jwt
                data_body ={}
                if not hasattr(request,"data_body"):
                    data_body = json.loads(request.body.decode("utf-8"))
                else:
                    data_body = getattr(request,"data_body")

                if not data_body.get("Token",None):
                    return HttpResponse('401 Unauthorized', status=401)
                else:
                    setattr(request,"data_body",data_body)
                    return old_handler(*__args,**__kwargs)
            else:
                data_body = json.loads(request.body.decode("utf-8"))
                setattr(request, "data_body", data_body)
                return old_handler(*__args, **__kwargs)
        ret_handler =handler
        return ret_handler

    current_handler =ret
    return ret

