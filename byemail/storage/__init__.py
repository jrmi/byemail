from importlib import import_module

from byemail.conf import settings
from byemail.storage.tinydb import Backend

storage = None

def init_storage():
    global storage
    config = dict(settings.STORAGE)
    module_path, _, backend = config.pop('backend').rpartition('.')

    # Load storage backend
    module = import_module(module_path)

    storage = getattr(module, backend)(**config)
