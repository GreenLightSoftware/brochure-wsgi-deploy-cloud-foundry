from typing import Dict
from urllib.parse import urlunsplit

from brochure_wsgi.command_preprocessors.upgrade_to_ssl_preprocessor import UpgradeToSSLPreprocessor


def get_cf_upgrade_to_ssl_preprocessor():
    secure_schemes = ("https",)

    def is_insecure(environ: Dict):
        return environ.get("HTTP_X_FORWARDED_PROTO", False) not in secure_schemes

    def url_from_environment(environ: Dict):
        scheme = environ.get("HTTP_X_FORWARDED_PROTO")
        netloc = environ.get("HTTP_HOST")
        path = environ.get("PATH_INFO")
        query_string = environ.get("QUERY_STRING")
        fragment = None
        parsed_url = urlunsplit(components=(scheme, netloc, path, query_string, fragment,))

        return parsed_url

    upgrade_to_ssl_preprocessor = UpgradeToSSLPreprocessor(is_insecure=is_insecure,
                                                           url_from_environment=url_from_environment)

    return upgrade_to_ssl_preprocessor
