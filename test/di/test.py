import pathlib

import kink
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
import enig
import enig_frames.db_context
import enig_frames.services.applications
import enig_frames.services.accounts
from enig_frames.containers import Container
fx=Container.config.config.jwt

print(fx.__data__)