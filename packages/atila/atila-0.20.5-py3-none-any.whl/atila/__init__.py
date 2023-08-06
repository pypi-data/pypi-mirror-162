"""
2015. 12. 10
Hans Roh
"""

__version__ = "0.20.5"

version_info = tuple (map (lambda x: not x.isdigit () and x or int (x),  __version__.split (".")))
assert len ([x for  x in version_info [:2] if isinstance (x, int)]) == 2, 'major and minor version should be integer'

# mongkey patch
from .patches import skitaipatch
from .Atila import Atila
import os
from .events import *
from .collectors.multipart_collector import FileWrapper
import skitai

# remap
WS_OP_THREADSAFE = skitai.WS_THREADSAFE
WS_OP_NOPOOL = skitai.WS_NOPOOL
WS_CHANNEL = skitai.WS_COROUTINE
WS_SESSION = skitai.WS_REPORTY
WS_CHATTY = skitai.WS_CHATTY

file = FileWrapper
def preference (*args, **kargs):
    import skitai
    return skitai.preference (*args, **kargs)


class load:
    def __init__ (self, target, pref = None):
        from rs4 import importer
        from rs4.attrdict import AttrDict
        import os, copy
        import skitai
        from skitai.testutil import offline

        def init_app (directory, pref):
            modinit = os.path.join (directory, "__init__.py")
            if os.path.isfile (modinit):
                mod = importer.from_file ("temp", modinit)
                initer = None
                if hasattr (mod, "__config__"):
                    initer = mod.__config__
                elif hasattr (mod, "bootstrap"): # old version
                    initer = mod.bootstrap (pref)
                initer and initer (pref)

        if hasattr (target, "__file__"):
            if hasattr (target, '__skitai__'):
                target = target.__skitai__

            if hasattr (target, '__app__'):
                module, abspath, directory = target, os.path.abspath (target.__file__), None

            else:
                directory = os.path.abspath (os.path.join (os.path.dirname (target.__file__), "export", "skitai"))
                if os.path.isfile (os.path.join (directory, 'wsgi.py')):
                    _script = 'wsgi'
                else:
                    _script = '__export__' # old version
                module, abspath = importer.importer (directory, _script)

        else:
            directory, script = os.path.split (target)
            module, abspath = importer.importer (directory, script [-3:] == ".py" and script [:-3] or script)

        self.module = module
        pref = pref or skitai.preference ()
        if directory:
            init_app (directory, pref)
            app = module.app
        else:
            module.__config__ (pref)
            app = module.__app__ ()

        for k, v in copy.copy (pref).items ():
            if k == "config":
                if not hasattr (app, 'config'):
                    app.config = v
                else:
                    for k, v in copy.copy (pref.config).items ():
                        app.config [k] = v
            else:
                setattr (app, k, v)

        offline.activate ()
        self.wasc = offline.wasc
        app.set_wasc (self.wasc)

        hasattr (module, '__setup__') and run_hook (module.__setup__, app)
        hasattr (module, '__mount__') and run_hook (module.__mount__, app)
        hasattr (module, '__mounted__') and run_hook (module.__mounted__, app)
        self.app = app

    def __enter__ (self):
        return self.app

    def __exit__ (self, *args):
        module = self.module
        hasattr (module, '__umount__') and run_hook (module.__umount__, self.app)
        self.app.shutdown ()
        hasattr (module, '__umounted__') and run_hook (module.__umounted__, self.app)
        self.wasc.cleanup ()


def run_hook (fn, app):
    import inspect
    from warnings import warn

    def display_warning ():
        warn (f'use {fn.__name__} (context, app, opts)', DeprecationWarning)

    nargs = len (inspect.getfullargspec (fn).args)
    if nargs == 1:
        display_warning ()
        args = (app,)
    elif nargs == 2:
        display_warning ()
        args = (app, {})
    elif nargs == 3:
        args = (None, app, {})

    fn (*args)