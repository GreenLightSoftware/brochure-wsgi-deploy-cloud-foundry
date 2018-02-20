import multiprocessing

import gunicorn.app.base
import os
from brochure_wsgi.brochure_wsgi_application import get_brochure_wsgi_application
from gunicorn.six import iteritems


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):
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
        "workers": number_of_workers(),
    }
    StandaloneApplication(application=get_brochure_wsgi_application(),
                          options=option_dictionary).run()
