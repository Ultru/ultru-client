class Types:
    types = {
        "AMCACHE": "amcache",
        "DIRECTORY_LISTING": "directory_listing",
        "ERROR": "error",
        "FILE": "file",
        "GROUP": "group",
        "HOST": "host",
        "LOG": "log",
        "MEMORY_MAP": "memory_map",
        "PERSISTENCE": "persistence",
        "PREFETCH": "prefetch",
        "PROCESS": "process",
        "PROFILE": "profile",
        "RUN_INFO": "run_info",
        "SERVICE": "service",
        "SHIMCACHE": "shimcache",
        "USER": "user",
        "YARA": "yara"
    }

    def __init__(self):
        self.lhv = None

    @property
    def value(self):
        return self.lhv

    @classmethod
    def from_type(cls, _type):
        c = cls()
        c.lhv = c.types[_type.upper()]
        return c

    def __getattr__(self, name):
        if name.upper() in self.types:
            self.lhv = self.types[name.upper()]
        return self

    def compare(self, rhv):
        return self.lhv == rhv

    def __repr__(self):
        return self.lhv