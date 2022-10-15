import pathlib
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
sys.path.append(r'C:\code\python\file-service-02\enigma')

import enigma
import enigma.services
p=enigma.app_config.config_path
db = enigma.app_config.get_config('db')
accounts =enigma.services.accounts.client.get_db('admin')
print(p)