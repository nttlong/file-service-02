import pathlib
import os
import sys
import fastapi
import pydantic


class Test(pydantic.BaseModel):
    pass
fx= fastapi.FastAPI()
@fx.get("X",response_model=Test)
def test_a():
    pass
fc=test_a
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