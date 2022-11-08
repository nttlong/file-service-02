import os.path
import pathlib

import cy_kit
class Configs:
    def __init__(self):

        self.working_dir = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.source = cy_kit.yaml_config(
            path= os.path.join(self.working_dir,"config.yml"),
            apply_sys_args= True
        )
