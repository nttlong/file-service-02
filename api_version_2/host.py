import pathlib
import os
import sys
import fastapi
import pydantic

def get_appx(app_name:str):
    return f"{app_name}_XXX"
class Test(pydantic.BaseModel):
    pass
fx= fastapi.FastAPI()
class OK1(pydantic.BaseModel):
    cod:str
def test_a(c:str=fastapi.Form(),appx=fastapi.Depends(get_appx))->OK1:
    pass
fc=fx.get("X",response_model=Test)(test_a)
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import re_quicky
if __name__ =="__main__":
    re_quicky.create_app(
        working_dir=pathlib.Path(__file__).parent.__str__(),
        host_url="http://172.16.13.72:8012",
        bind="0.0.0.0:8012",
        controller_dirs=["./controllers"],
        dev_mode=True

    )
    re_quicky.uvicon_start()