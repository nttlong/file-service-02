__app__= {}
import threading

import db_connection
from . import app_mamager
__lock__= threading.Lock()

def tanent_check(fail_value, *args,**kwargs):
    """
    Kiểm tra tanent nếu trật trả về fail_value
    :param fail_value: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    def w_init(*m,**n):
        print(*m)
    def wrapper(*x,**y):
        fn = x[0]
        def new_call(*a,**b):
            global __lock__
            global __app__
            if b.get("app_name",None) is not None:

                app_name= b.get("app_name","")
                if app_name=="admin":
                    app_name=db_connection.default_db_name
                else:
                    app_name=app_name.lower()
                b["app_name"]=app_name
                app = __app__.get(app_name,False)
                if isinstance(app,dict):
                    return fn(*a,**b)
                else:
                    __lock__.acquire()
                    try:
                        app=app_mamager.get_app_by_name(
                            db_connection.connection.get_database(
                                db_connection.default_db_name
                            ),
                            app_name
                        )
                        __app__[app_name]=app
                    except Exception as e:
                        raise e
                    finally:
                        __lock__.release()
                    if app is None:
                        return fail_value
                    else:
                        return fn(*a, **b)



        return new_call

    return wrapper


