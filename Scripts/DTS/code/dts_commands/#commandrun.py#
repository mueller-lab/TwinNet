import sys

from pathlib import Path

import uuid

class Session:
    def __init__(self, dirpath_root_, session_uuid_):

        self.uuid = uuid.uuid4()

        self.path = Path( dirpath_root_, "sessions", str(session_uuid_) )

        self.path.mkdir(parents=True, exist_ok=True)

        print( "Session dir created:", self.path )
