from enum import Enum


class ErrorCode(Enum):
    """
    Bảng liệt kê mã lỗi
    """
    NONE = "none"
    """
    Hổng có gì
    """
    REQUIRE = "require"
    """
    Thiếu thông tin
    """
    INVALID_DATA_TYPE = "InvalidDataType"
    """
    Sai kiểu
    """
    ITEM_WAS_NOT_FOUND ="ItemWasNotFound"
    """
    Hổng tìm thấy
    """
    LOGIN_FAIL="LoginFail"
    """
    Thật đáng tiếc login không được
    """
    FILE_TYPE_IS_NOT_SUPPORT="FileTypeIsNotSupport"
    """
    Loại file này kg hỗ trợ
    """


class __Field__:
    def __init__(self, *args, **kwargs):
        self.is_require = False
        if isinstance(args[0], tuple):
            if args[0].__len__() > 1:
                self.is_require = args[0][1]
            self.data_type = args[0][0]
        elif isinstance(args[0], type):
            self.data_type = args


class Error:
    """
    Lớp trả lỗi
    """

    def __init__(self):
        self.code = ErrorCode.NONE
        """
        Mã lỗi
        """
        self.message = ""
        """
        Thông báo cho dễ hiểu
        """
        self.field = ""
        """
        Thông tin gây ra lỗi
        """
        self.__name__ = ""

    def to_dict(self)->dict:
        """
        Chuyển ra dict
        :return:
        """
        ret = {}
        for k, v in self.__dict__.items():
            if not (k.__len__() > 4 and k[0:2] == "__" and k[-2:] == "__"):
                if isinstance(v, ErrorCode):
                    ret = {**ret, **{k: v.value}}
                else:
                    ret = {**ret, **{k: v}}
        return ret

    def as_exception(self):
        """
        Convert ra Exception để raise lỗi khi cần
        :return:
        """
        import json
        return Exception(json.dumps(self.to_dict()))


def constraints():
    """
    Constraints hạn chế sai sót cho class
    Một khi đã wrapper class sẽ bổ sung các hàm sau:
    get_error: Dùng để lấy lỗi,một lần chỉ một lỗi\n
    Ví dụ:
        class X:
            my_name=(str,true) # kiểu text và bắt buộc
        x=X({'my_name':124})
        err= x.get_error()
    to_dict: Lấy toàn bộ thông tin ra dạng dict
    Ví dụ:
        x.may_name="test"
        x.to_dict()
    :return:
    """
    def wrapper(*args, **kwargs):
        cls = args[0]
        for k, v in cls.__dict__.items():
            if not (k.__len__() > 4 and k[0:2] == "__" and k[-2:] == "__"):
                f = __Field__(v)

                f.__name__ = k
                setattr(cls, k, f)

        setattr(cls, "__init__", __wrapper_init__)
        setattr(cls, "get_error", __wrapper_get_error__)
        setattr(cls, "to_dict", __wrapper_to_dict__)
        old_get_attr = getattr(cls, "__getattribute__")
        old_set_attr = getattr(cls, "__setattr__")
        setattr(cls, "__old_getattr__", old_get_attr)
        setattr(cls, "__old_getattribute__", old_set_attr)
        setattr(cls, "__setattr__", __wrapper_setattr__)
        setattr(cls, "__getattr__", __wrapper_getattr__)

        return cls

    return wrapper


def __wrapper_to_dict__(*args, **kwargs):
    """
    Gắn thâm phương thức khởi tạo khi gọ
    :param args:
    :param kwargs:
    :return:
    """
    ret = {}
    for k,v in args[0].__data__.items():
        if hasattr(args[0],k) and not(k.__len__()>4 and k[0:2]=="__" and k[-2:]=="__"):
            vv= getattr(args[0],k)
            # if isinstance(vv,type):
            ret= {**ret,**{k:vv}}
        else:
            ret = {**ret, **{k, v}}
    return ret


def __wrapper_init__(*args, **kwargs):
    instance = args[0]
    """
    Instance của class
    """
    data = {}

    if kwargs == {}:
        """
        Nếu DEV không dùng keyword aguments
        """
        if isinstance(args, tuple):
            for x in args:
                if isinstance(x, dict):
                    for k, v in x.items():
                        if isinstance(k, str):
                            data = {**data, **{k: v}}
                        elif isinstance(k, __Field__):
                            data = {**data, **{k.__name__: v}}
    else:
        raise NotImplemented
    instance.__data__ = data


def __wrapper_get_error__(*args, **kwargs):
    instance = args[0]
    """
    Instance của class
    """
    cls = type(instance)
    """
    Class của instance
    """
    ret = Error()
    for k, v in cls.__dict__.items():
        if k in ["to_dict", "get_error"]:
            continue
        if isinstance(k, str):
            if not (k.__len__() > 4 and k[0:2] == "__" and k[-2:] == "__"):
                v = cls.__dict__.get(k)
                if isinstance(v, __Field__):
                    v_type, v_require = (v.data_type, v.is_require)
                    if v_require and instance.__data__.get(k, None) is None:
                        ret.code = ErrorCode.REQUIRE
                        ret.message = f"{k} is require"
                        ret.field = k
                        return ret
                    elif instance.__data__.get(k, None) is not None:
                        r_v = instance.__data__.get(k)
                        if isinstance(v_type,tuple) and len(v_type)==1:
                            v_type=v_type[0]
                        if type(r_v) != v_type:
                            ret.code = ErrorCode.INVALID_DATA_TYPE
                            ret.message = f"value {r_v} of {k} is invalid"
                            ret.field = k
                            return ret

                instance.__dict__[k] = instance.__data__.get(k)
                instance.DICT = {}
                for k, v in instance.__dict__.items():
                    instance.DICT = {**instance.DICT, **{k: v}}


def __wrapper_getattr__(*args, **kwargs):
    instance = args[0]
    attr_name = args[1]
    cls = type(instance)
    if attr_name == "to_dict":
        return instance.__old_getattribute__(attr_name)
    if attr_name.__len__() > 4 and attr_name[0:2] == "__" and attr_name[-2:] == "__":
        return instance.__old_getattribute__(attr_name)
    elif instance.__dict__["__data__"].get(attr_name,None) is not None:
        return instance.__dict__["__data__"].get(attr_name)

    raise Exception('__wrapper_getattr__')


def __wrapper_setattr__(*args, **kwargs):
    instance = args[0]
    attr_name = args[1]
    if attr_name == "to_dict":
        raise Exception("OK")
    cls = type(instance)
    if args[1] == "__data__":
        instance.__dict__[args[1]] = args[2]
        return
    elif not (attr_name.__len__() > 4 and attr_name[0:2] == "__" and attr_name[-2:] == "__"):
        value = args[2]
        field_define = cls.__dict__.get(attr_name, None)
        if isinstance(field_define, __Field__):
            if field_define.is_require and value is None:
                raise Exception(f"{cls.__module__}.{cls.__name__}.{field_define.__name__} can not be null")
            elif value is not None:
                if type(value) != field_define.data_type:
                    raise Exception(f"Thy try to set {cls.__module__}.{cls.__name__}.{field_define.__name__} is {value}"
                                    f"But {cls.__module__}.{cls.__name__}.{field_define.__name__} require value with {field_define.data_type} type")
        instance.__dict__[attr_name] = value
