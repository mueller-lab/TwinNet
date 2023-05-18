import json
from pathlib import Path
import platform
import uuid


class ProjectConfig:
    def __init__(self, name_, **kwargs):
        self.basename = "config.json"

        self.dirpath_root = kwargs.get("dirpath_root",
                                       Path().resolve() / name_)

        self.revision = kwargs.get("revision",
                                   platform.system())

        self.uuid = uuid.uuid4()

        self.load()

    def load(self):
        self.dirpath = self.dirpath_root / str(self.revision)

        self.dirpath.mkdir(parents=True, exist_ok=True)

        self.filepath = self.dirpath / self.basename                  

        print(f"ProjectConfig: {self.filepath}")
        
        with open(self.filepath, "r") as filehandle:
            self.json = json.load(filehandle)
