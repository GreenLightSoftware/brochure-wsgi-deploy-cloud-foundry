import multiprocessing
import os

import gunicorn.app.base
from brochure.brochure_application import BrochureApplication
from brochure.commands.command_types import CommandType
from brochure_wsgi.brochure_wsgi_application import BrochureWSGIApplication
from brochure_wsgi.http_user_interface import HTTPUserInterfaceProvider
from brochure_wsgi.path_command_provider import GetPathCommandProvider
from brochure_wsgi.value_fetchers.environment_contact_method_fetcher import environment_contact_method_fetcher
from brochure_wsgi.value_fetchers.environment_cover_section_fetcher import environment_cover_section_fetcher
from brochure_wsgi.value_fetchers.environment_enterprise_fetcher import environment_enterprise_fetcher
from gunicorn.six import iteritems
from werkzeug.routing import Map, Rule

from cf_domain_redirect_preprocessor import get_cf_domain_redirect_preprocessor
from cf_favicon_preprocessor import get_cf_favicon_preprocessor
from cf_upgrade_to_ssl_preprocessor import get_cf_upgrade_to_ssl_preprocessor


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
    brochure_application_command_map = Map()
    brochure_application_command_map.add(Rule("/", endpoint=lambda: CommandType.SHOW_COVER))
    get_path_command_provider = GetPathCommandProvider(url_map=brochure_application_command_map)

    domain_application = BrochureApplication(contact_method_fetcher=environment_contact_method_fetcher,
                                             cover_section_fetcher=environment_cover_section_fetcher,
                                             enterprise_fetcher=environment_enterprise_fetcher)
    user_interface_provider = HTTPUserInterfaceProvider()
    domain_redirect_preprocessor = get_cf_domain_redirect_preprocessor()
    upgrade_to_ssl_preprocessor = get_cf_upgrade_to_ssl_preprocessor()
    favicon_preprocessor = get_cf_favicon_preprocessor()
    command_preprocessors = (domain_redirect_preprocessor, upgrade_to_ssl_preprocessor, favicon_preprocessor,)

    brochure_wsgi_application = BrochureWSGIApplication(domain_application=domain_application,
                                                        user_interface_provider=user_interface_provider,
                                                        get_path_command_provider=get_path_command_provider,
                                                        command_preprocessors=command_preprocessors)
    GunicornApplication(application=brochure_wsgi_application,
                        options=option_dictionary).run()
