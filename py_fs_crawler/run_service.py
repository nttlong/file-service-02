import os
import threading
from time import sleep

print(__file__)
path_to_fs='/usr/share/fscrawler/bin/fscrawler'
import subprocess
def run():
    subprocess.run(["/usr/share/fscrawler/bin/fscrawler"])
th=threading.Thread(target=run,args=())
th.start()
th.join()


