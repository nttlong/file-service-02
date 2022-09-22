import sys
import os
for k,v in os.environ.items():
    if 'file_server_' in k:
        print(f"{k}={v}")

print(os.environ.get('file_server_db_port'))