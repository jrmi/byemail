from importlib import import_module

from byemail.conf import settings
from byemail.storage.tinydb import Backend

storage = None

def init_storage():
    global storage
    module_path, _, backend = settings.STORAGE['backend'].rpartition('.')

    # Load storage backend
    module = import_module(module_path)

    storage = getattr(module, backend)()
