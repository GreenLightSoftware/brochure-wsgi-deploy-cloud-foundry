import os
from functools import partial

from werkzeug.serving import run_simple
from werkzeug.wrappers import Response
from werkzeug.wsgi import get_current_url
from whitenoise import WhiteNoise

from wsgi_common import get_domain_redirect_preprocessor, get_redirect_to_secure_scheme_preprocessor
from gunicorn_application import GunicornApplication
from sparse_werkzeug import get_sparse_werkzeug_application


def main():
    whitenoise = WhiteNoise(None)
    favicon_url = "/favicon.ico"
    serve_favicon = get_static_file_handler(whitenoise, favicon_url, get_relative_filepath("static", "favicon.ico"))

    path_rules = {
        "/": {"endpoint": lambda: Response("Welcome to our place")},
        "/sections/<name>": {"endpoint": lambda name: Response("Welcome to the {} section.".format(name))},
        favicon_url: {"endpoint": serve_favicon},
    }

    exception_rules = {
        404: lambda environ: Response("Not Found: '{}'".format(environ.get("PATH_INFO", "UNKNOWN")), status=404),
        405: lambda environ: Response("Not Allowed", status=405),
    }

    port = int(os.environ.get("PORT", 8000))
    secure_scheme = os.environ.get("SECURE_SCHEME", "https")
    localhost = "localhost"
    target_domain = os.environ.get("TARGET_DOMAIN", localhost)
    source_domains = os.environ.get("SOURCE_DOMAINS", target_domain).split(",")
    domain_redirect_preprocessor = get_domain_redirect_preprocessor(source_domains=source_domains,
                                                                    target_domain=target_domain,
                                                                    source_url_provider=get_current_url,
                                                                    force_target_scheme=secure_scheme)
    upgrade_to_https_preprocessor = get_redirect_to_secure_scheme_preprocessor(
        is_insecure=lambda e: e.get("HTTP_X_FORWARDED_PROTO", False) not in (secure_scheme,),
        source_url_provider=get_current_url,
        secure_scheme=secure_scheme
    )

    preprocessors = (domain_redirect_preprocessor, upgrade_to_https_preprocessor)

    wsgi_application = get_sparse_werkzeug_application(preprocessors=preprocessors,
                                                       path_rules=path_rules,
                                                       exception_rules=exception_rules)

    in_production_mode = target_domain != localhost
    get_runner = get_production_runner if in_production_mode else get_development_runner

    run_application = get_runner(wsgi_application, target_domain, port)

    run_application()


def get_production_runner(wsgi_application, hostname, port):
    options = {"bind": "%s:%s" % (hostname, port)}
    return GunicornApplication(application=wsgi_application, options=options).run


def get_development_runner(wsgi_application, hostname, port):
    return partial(run_simple, **{"application": wsgi_application,
                                  "hostname": hostname,
                                  "port": port,
                                  "use_reloader": True,
                                  "use_debugger": True})


def get_static_file_handler(whitenoise, url, path):
    favicon_static_file = whitenoise.get_static_file(path=path, url=url)
    whitenoise.files[url] = favicon_static_file

    favicon_handler = partial(whitenoise.serve, static_file=favicon_static_file)

    return lambda: favicon_handler


def get_relative_filepath(*path_fragments):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), *path_fragments)


if __name__ == "__main__":
    main()
