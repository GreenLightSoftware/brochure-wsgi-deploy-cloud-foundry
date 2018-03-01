import multiprocessing
import os

import gunicorn.app.base
from brochure_wsgi.brochure_wsgi_application import get_brochure_wsgi_application
from gunicorn.six import iteritems


class GunicornApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, application, options=None):
        self.options = options or {}
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


if __name__ == "__main__":
    option_dictionary = {
        "bind": '%s:%s' % ('0.0.0.0', os.environ.get("PORT", "8000")),
        "workers": (multiprocessing.cpu_count() * 2) + 1,
    }
    GunicornApplication(application=get_brochure_wsgi_application(),
                        options=option_dictionary).run()
