from typing import Dict

from brochure_wsgi.command_preprocessors.upgrade_to_ssl_preprocessor import UpgradeToSSLPreprocessor

from common import url_from_environment


def get_cf_upgrade_to_ssl_preprocessor():
    secure_schemes = ("https",)

    def is_insecure(environ: Dict):
        return environ.get("HTTP_X_FORWARDED_PROTO", False) not in secure_schemes

    upgrade_to_ssl_preprocessor = UpgradeToSSLPreprocessor(is_insecure=is_insecure,
                                                           url_from_environment=url_from_environment)

    return upgrade_to_ssl_preprocessor
