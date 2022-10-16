import pathlib

import kink
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
import enig
import enig_frames.db_context
import enig_frames.services.applications
import enig_frames.services.accounts
apps= enig.create_instance(enig_frames.services.applications.Applications)
apps.create(
    name="long-test",
    login_url="http://localhost:8011",
    domain="localhost",
    description=""
)
accs=enig.create_instance(enig_frames.services.accounts.Accounts)
app_name="admin"
username="root"
password="rootdsada"
ret=accs.verify(app_name, username,password)
print(ret)