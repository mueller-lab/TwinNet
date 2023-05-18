import sys

from pathlib import Path

import uuid

class ToolSession:
    def __init__(dirpath_root_, session_uuid_):

        self.uuid = uuid.uuid4()

        self.path = Path( dirpath_root_+str(session_uuid_)+"/" )

        self.path.mkdir(parents=True, exist_ok=True)

        print( "Session dir created:", self.path )
