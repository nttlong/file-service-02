import signal
signal.signal(signal.SIGCHLD, signal.SIG_IGN)
import os
import pathlib
import sys
working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)

print("running")
if __name__ == "__main__":
    import watcher
    watcher.run()

"""
python /home/vmadmin/python/v6/file-service-02/app_services/file_processing.py db.port=27018 db.username=admin-doc db.password=123456 db.authSource=lv-docs admin_db_name=lv-docs elastic_search.server=http://192.168.18.36:9200 elastic_search.prefix_index=lv-codx

"""