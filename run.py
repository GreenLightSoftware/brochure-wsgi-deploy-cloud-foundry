import os
from json import loads

from werkzeug.wrappers import Response

from common import url_from_environment
from gunicorn_application import GunicornApplication
from pure_wsgi import get_redirect_to_secure_scheme_preprocessor, get_domain_redirect_preprocessor
from sparse_werkzeug import get_sparse_werkzeug_application
from whitenoise_handler import get_static_file_handler_provider


def main():
    static_file_handler_provider = get_static_file_handler_provider()
    favicon_url = "/favicon.ico"
    favicon_request_handler = static_file_handler_provider(favicon_url, get_relative_filepath("static", "favicon.ico"))

    path_rules = {
        "/": lambda: Response("Welcome to our place"),
        favicon_url: lambda: favicon_request_handler,
        "/sections/<name>": lambda name: Response("Welcome to the {} section.".format(name)),
    }

    exception_rules = {
        404: lambda environ: Response("Not Found: '{}'".format(environ.get("PATH_INFO", "UNKNOWN")), status=404),
        405: lambda environ: Response("Not Allowed", status=405),
    }

    preprocessors = tuple()
    if not os.environ.get("LOCAL"):
        secure_scheme = "https"
        source_domains = loads(os.environ.get("BROCHURE_SOURCE_DOMAINS", "[]"))
        target_domain = loads(os.environ.get("BROCHURE_TARGET_DOMAIN", "{}")).get("target_domain", "localhost")

        domain_redirect_preprocessor = get_domain_redirect_preprocessor(source_domains=source_domains,
                                                                        target_domain=target_domain,
                                                                        source_url_provider=url_from_environment,
                                                                        force_target_scheme=secure_scheme)
        upgrade_to_https = get_redirect_to_secure_scheme_preprocessor(
            is_insecure=lambda e: e.get("HTTP_X_FORWARDED_PROTO", False) not in (secure_scheme,),
            source_url_provider=url_from_environment,
            secure_scheme=secure_scheme
        )

        preprocessors = (domain_redirect_preprocessor, upgrade_to_https)

    wsgi_application = get_sparse_werkzeug_application(preprocessors=preprocessors,
                                                       path_rules=path_rules,
                                                       exception_rules=exception_rules)
    gunicorn_application = GunicornApplication(application=wsgi_application)
    gunicorn_application.run()


def get_relative_filepath(*path_fragments):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), *path_fragments)


if __name__ == "__main__":
    main()
