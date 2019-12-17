import os as _os
import pickle as _pickle
import functools as _functools
import types as _types
import contextlib as _contextlib

CACHE_DIR = '.persist'
OBJECTS_DIR = _os.path.join(CACHE_DIR, 'objects')
ENVIRONMENT_DIR = _os.path.join(CACHE_DIR, 'environments')

if not _os.path.exists(CACHE_DIR): _os.mkdir(CACHE_DIR)
if not _os.path.exists(OBJECTS_DIR): _os.mkdir(OBJECTS_DIR)
if not _os.path.exists(ENVIRONMENT_DIR): _os.mkdir(ENVIRONMENT_DIR)

def persist(x):
    """Persist the result of a function to avoid recalling to the object. Accept a name given
    to be the name of the object saved - else it shall be the name of the function.
    """

    # Define the name that is to be given to the object when it is called
    if isinstance(x, types.FunctionType):
        filename = x.__name__
    elif isinstance(x, str):
        filename = x
    else:
        raise ValueError()

    # Define path to the persited object - delete any old cache file at that location
    path = _os.path.join(CACHE_DIR, filename)
    if _os.path.exists(path): _os.remove(path)

    # Define the wrapping function
    def wrapper(func):

        @_functools.wraps(func)
        def inner(*args, **kwargs):

            # If the object has been saved before, load it again from source
            if _os.path.exists(path):
                with open(path, 'rb') as fh:
                    print("opened")
                    return _pickle.load(fh)

            result = func(*args, **kwargs)

            with open(path, 'wb') as fh:
                _pickle.dump(result, fh)

            return result
        return inner

    if isinstance(x, _types.FunctionType):
        return wrapper(x)
    else:
        return wrapper

def load(name):
    with open(_os.path.join(CACHE_DIR, name), 'rb') as fh:
        return _pickle.load(fh)


@_contextlib.contextmanager
def save_environment(name, environment):

    GLOBAL = environment()
    modules = {}

    for k, v in GLOBAL.items():
        if k.startswith('_') or not isinstance(v, _types.ModuleType): continue
        modules[k] = v

    for k in modules.keys():
        del GLOBAL[k]

    yield None

    imported = {}

    for k, v in environment().items():
        if k.startswith('_') or not isinstance(v, _types.ModuleType): continue
        imported[k] = v.__name__

    environment().update(modules)

    with open(_os.path.join(ENVIRONMENT_DIR, name), 'wb') as fh:
        _pickle.dump(imported, fh)

def load_environment(name):
    with open(_os.path.join(ENVIRONMENT_DIR, name), 'rb') as fh:
        imported = _pickle.load(fh)

    loaded = {}
    for alias, module in imported.items():
        loaded[alias] = __import__(module)

    return loaded
