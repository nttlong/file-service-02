import sys
import pathlib
working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import datetime
import os



import cy_kit
from cyx.common.msg import MessageService
from cyx.common.msg_mongodb import MessageServiceMongodb

log_start = cy_kit.create_logs(os.path.join(working_dir,"logs","file-process"),"start")
log_start.info(f"start at {datetime.datetime.utcnow()}")
cy_kit.config_provider(
    from_class= MessageService,
    implement_class= MessageServiceMongodb
)
if __name__ == "__main__":
    if sys.platform == "linux":
        import signal
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    import watcher
    watcher.run(use_thread=False)

"""
python /home/vmadmin/python/v6/file-service-02/app_services/file_processing.py db.port=27018 db.username=admin-doc db.password=123456 db.authSource=lv-docs admin_db_name=lv-docs elastic_search.server=http://192.168.18.36:9200 elastic_search.prefix_index=lv-codx

"""