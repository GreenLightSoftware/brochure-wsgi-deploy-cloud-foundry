import multiprocessing
import os
from typing import Callable, Dict, Any, Optional

import gunicorn.app.base
from gunicorn.six import iteritems


class GunicornApplication(gunicorn.app.base.BaseApplication):
    def __init__(self,
                 application: Callable[[Dict[str, Any], Callable], Callable[[bytes], Any]],
                 options: Optional[Dict[str, Any]] = None):
        options = options or {}
        merged_options = {
            "bind": "%s:%s" % ("localhost", os.environ.get("PORT", "8000")),
            "workers": (multiprocessing.cpu_count() * 2) + 1,
            **options
        }
        self.options = merged_options
        self.application = application
        super().__init__()

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
