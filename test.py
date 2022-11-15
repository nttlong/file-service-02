import pydantic
class DocumentObjectBase(pydantic.BaseModel,dict):

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        pydantic.BaseModel.dict(self,*args, **kwargs)

cx= DocumentObjectBase()
print(c)