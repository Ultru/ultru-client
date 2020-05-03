class Filters:
    available_filters = {
        "type": ["amcache", "directory_listing", "error", "file", "group", "host",
                 "log", "memory_map", "persistence", "prefetch", "process", "profile",
                 "run_info", "service", "shimcache", "user", "yara"],
        "md5": True,
        "sha1": True,
        "sha256": True,
        "engagement": True
    }

    def __init__(self):
        self.lhv = None

    def __getattr__(self, name):
        if name in self.available_filters.keys():
            self.lhv = name
        return self

    def compare(self, rhv):
        if isinstance(self.available_filters.get(self.lhv), list):
            return rhv in self.available_filters[self.lhv]
        else:
            return rhv

    def eq(self, rhv):
        return f"{self.lhv} = {rhv}"

    @property
    def value(self):
        return self.lhv