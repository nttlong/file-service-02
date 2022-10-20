import sys
import pathlib

import enig
import enig_frames.containers

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
container = enig_frames.containers.Container
import enig_frames.plugins.video
plugin = enig.create_instance(enig_frames.plugins.video.PlugInVideo)
plugin.process(
    file_path=r"/home/vmadmin/python/v5/file-service-02/tmp/admin/d7b21347-f94b-4246-8b93-718859db189b.mp4",
    app_name="admin",
    upload_id="d7b21347-f94b-4246-8b93-718859db189b"
)