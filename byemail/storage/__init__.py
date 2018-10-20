from importlib import import_module

from byemail.conf import settings

class Storage():
    def __init__(self, loop=None):
        self.loop = loop
        self._storage = None

    def load_storage(self, loop=None):
        global storage
        config = dict(settings.STORAGE)
        module_path, _, backend = config.pop('backend').rpartition('.')

        # Load storage backend
        module = import_module(module_path)

        return getattr(module, backend)(loop=loop, **config)

    def __getattr__(self, name):
        if not getattr(self, '_storage'):
            self._storage = self.load_storage(self.loop) 

        return getattr(self._storage, name)


storage = Storage()
