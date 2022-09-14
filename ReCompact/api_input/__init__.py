ERROR_TYPE_INVALID_DATA = 1
ERROR_TYPE_MISSING_DATA = 2
ERROR_TYPE_ITEM_WAS_NOT_FOUND = 2
from django.http import JsonResponse, HttpResponse


class Error:
    def __init__(self):
        self.message = None
        self.code = None
        self.field = None

    def raise_item_was_not_found(self):
        self.code = ERROR_TYPE_ITEM_WAS_NOT_FOUND
        self.message = 'Item was not found'
        return self

    def raise_invalid_field(self, fiel_name, description=None):
        self.code = ERROR_TYPE_INVALID_DATA
        self.field = fiel_name
        if description is not None:
            self.message = description
        else:
            self.message = f"{self.field} is invalid data type or format"
        return self

    def to_json(self):
        return JsonResponse(dict(
            error=dict(
                message=self.message,
                code=self.code,
                field=self.field
            )
        ), safe=False)

    def to_error_500(self):
        return HttpResponse(status=500, content=str.encode(self.message))


def map_param(cls_params):
    param_cls = cls_params

    old_get_attr = getattr(param_cls, "__getattribute__")
    cls_properties = {}
    for k, v in param_cls.__dict__.items():
        if not (k.__len__() > 4 and k[0:2] == "__" and k[-2:] == "__"):
            cls_properties[k] = v

    def new_get_attr(obj, item):
        if item == "JSON_DATA":
            ret = {}
            for k, v in obj.__dict__.items():
                if not (k.__len__() > 4 and k[0:2] == "__" and k[-2:] == "__"):
                    ret[k] = v
            return JsonResponse(dict(
                data=ret
            ), safe=False)

        if item.__len__() > 4 and item[0:2] == "__" and item[-2:] == "__":
            return old_get_attr(obj, item)
        if not hasattr(type(obj), item):
            raise Exception(f"{item} not found in {param_cls.__module__}.{param_cls.__name__}")
        field = getattr(type(obj), item)
        ret = obj.__dict__.get(item, None)
        if isinstance(field, type):
            return ret
        elif isinstance(field, tuple) and field.__len__()>1:
            if field[1]:
                if not ret is None:
                    return ret
                else:
                    raise Exception(f"{item} not found in {param_cls.__module__}.{param_cls.__name__}")
            else:
                return ret

    setattr(param_cls, "__getattribute__", new_get_attr)

    def remap_params(fn, kwargs, data, error):
        if isinstance(kwargs, dict) and callable(fn):
            for k, v in fn.__annotations__.items():
                if isinstance(data, v):
                    kwargs[k] = data
                elif isinstance(error, v):
                    kwargs[k] = error
                else:
                    kwargs[k] = None

    def ret(*__args, **__kwargs):
        hanlder = __args[0]

        def re_handler(*x, **y):
            from django.utils.datastructures import MultiValueDict
            from django.core.files.uploadedfile import InMemoryUploadedFile,TemporaryUploadedFile,UploadedFile
            import json
            request = x[0]
            post_data = {}
            post_data_txt = None
            if request.FILES and isinstance(request.FILES, MultiValueDict):
                post_data_txt = request.POST["data"]
                post_data = json.loads(post_data_txt)
                for k, v in request.FILES.items():
                    if type(v) in [InMemoryUploadedFile,TemporaryUploadedFile,UploadedFile]:
                        post_data[k] = v
                    else:
                        fx = v

            else:
                post_data_txt = request.body.decode("utf-8")
                post_data = json.loads(post_data_txt)
            setattr(request, "data_body", post_data)
            obj_data = param_cls()
            error = None
            for k, f in cls_properties.items():
                v = post_data.get(k, None)

                if isinstance(f, tuple) and f.__len__() == 1:
                    f = f[0]
                if isinstance(f, type):
                    if v != None and not isinstance(v, f):
                        error = __make__error__(
                            error,
                            error_type=ERROR_TYPE_INVALID_DATA,
                            field_name=k,
                            message=f'The value of {k} is invalid. Data type of {k} must be  {f.__name__}'
                        )
                        remap_params(hanlder, y, None, error)
                        return hanlder(x, y)
                    else:
                        obj_data.__dict__[k] = v
                elif isinstance(f, tuple):
                    data_type = f[0]
                    is_require = f[1]
                    if v == None and is_require:
                        error = __make__error__(
                            error,
                            error_type=ERROR_TYPE_MISSING_DATA,
                            field_name=k,
                            message=f"{k} is missing"
                        )
                        remap_params(hanlder, y, None, error)
                        return hanlder(*x, **y)
                    if v != None and not isinstance(v, data_type):
                        error = __make__error__(
                            error,
                            error_type=ERROR_TYPE_INVALID_DATA,
                            field_name=k,
                            message=f'The value of {k} is invalid. Data type of {k} must be  {f.__name__}'
                        )
                        remap_params(hanlder, y, None, error)
                        return hanlder(*x, **y)

                obj_data.__dict__[k] = v
            remap_params(hanlder, y, obj_data, None)
            return hanlder(*x, **y)

        return re_handler

    return ret


def __make__error__(error, error_type, field_name, message):
    if error is None:
        error = Error()
    error.field = field_name
    error.code = error_type
    error.message = message
    return error
