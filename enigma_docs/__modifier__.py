
def to_dict(*args,**kwargs):
    print((args))
    # ret= {}
    # for k,v in obj.__dict__.items():
    #     if k[0:2]!="__" and k[-2:]!="__":
    #         ret[k] = to_dict(v)
    # return ret



def define(cls):
    setattr(cls,"to_dict",to_dict)
    return cls