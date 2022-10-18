import pathlib

import kink
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
import api_models.documents
class  DBItem(dict):
    def __init__(self,*args,**kwargs):
        dict.__init__(self, *args,**kwargs)
    def __getitem__(self, item):
        import ReCompact.dbm.DbObjects.Docs
        if isinstance(item,ReCompact.dbm.DbObjects.Docs.Fields):
            return self.get(item.__name__)
        return self.get(item)
    def get(self,key,dv=None):
        import ReCompact.dbm.DbObjects.Docs
        if isinstance(key,ReCompact.dbm.DbObjects.Docs.Fields):
            return dict.get(self,key.__name__,dv)
        return dict.get(self,key,dv)
    def __setitem__(self, key, value):
        import ReCompact.dbm.DbObjects.Docs
        if isinstance(key, ReCompact.dbm.DbObjects.Docs.Fields):
            return self.update({key.__name__:value})
        return  self.update({key:value})

ret= DBItem(
    code=1
)
fx =ret.get(api_models.documents.Files._id,"123")
print(ret)