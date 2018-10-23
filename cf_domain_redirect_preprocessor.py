import os
from json import loads

from brochure_wsgi.command_preprocessors.domain_redirect_preprocessor import DomainRedirectPreprocessor

from common import url_from_environment


def get_cf_domain_redirect_preprocessor():
    domain_redirect_preprocessor = DomainRedirectPreprocessor(
        url_from_environment=url_from_environment,
        source_domain_provider=lambda: loads(os.environ.get("BROCHURE_SOURCE_DOMAINS", "[]")),
        destination_domain_provider=lambda: loads(os.environ.get("BROCHURE_TARGET_DOMAIN", "{}")).get("target_domain",
                                                                                                      "example.com")
    )

    return domain_redirect_preprocessor
