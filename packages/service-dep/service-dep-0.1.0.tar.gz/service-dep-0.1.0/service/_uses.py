"""Internal uses funcs."""

import os
import sys
import inspect


def load_modules_from_path(path):
    """Import all modules from the given directory."""
    if path[-1:] != '/':
        path += '/'

    if not os.path.exists(path):
        raise OSError("Directory does not exist: %s" % path)

    sys.path.append(path)

    for f in os.listdir(path):
        if len(f) > 3 and f[-3:] == '.py':
            modname = f[:-3]
            __import__(modname, globals(), locals(), ['*'])


def load_class(fqdn_path: str):
    """Load class by fqdn module path."""
    paths = fqdn_path.split('.')
    modulename, classname = '.'.join(paths[:-1]), paths[-1]  # noqa
    __import__(modulename, globals(), locals(), ['*'])
    cls = getattr(sys.modules[modulename], classname)
    if not inspect.isclass(cls):
        raise TypeError("%s is not a class" % fqdn_path)
    return cls
