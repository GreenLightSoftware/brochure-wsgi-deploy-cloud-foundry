from typing import Dict, Collection, Callable, Optional, Any
from urllib.parse import urlunsplit, urlsplit


def get_domain_redirect_preprocessor(source_domains: Collection[str],
                                     target_domain: str,
                                     source_url_provider: Callable[[Dict[str, str]], str],
                                     force_target_scheme: Optional[str] = None):
    if not len(source_domains):
        raise ValueError("source_domains must not be empty")
    if not len(target_domain):
        raise ValueError("target_domain must not be empty")

    def _wrap_application(applicaton: Callable) -> Callable:

        def _domain_redirect(environ, start_response):
            source_url = source_url_provider(environ)
            scheme, source_domain, source_path, source_query, source_fragment = urlsplit(source_url)

            if source_domain == target_domain:
                return applicaton(environ, start_response)

            if source_domain in source_domains:
                target_scheme = force_target_scheme or scheme
                split_url = (target_scheme, target_domain, source_path, source_query, source_fragment)
                secure_destination_url = urlunsplit(split_url)

                start_response("301 Moved Permanently", [("Location", secure_destination_url)])

                return [b'']

            return applicaton(environ, start_response)

        return _domain_redirect

    return _wrap_application


def get_redirect_to_secure_scheme_preprocessor(is_insecure: Callable[[Dict[str, Any]], bool],
                                               source_url_provider: Callable[[Dict[str, Any]], str],
                                               secure_scheme: str = "https"):
    def _wrap_application(applicaton: Callable) -> Callable:
        def _secure_redirect(environ, start_response):
            if is_insecure(environ):
                insecure_source_url = source_url_provider(environ)
                scheme, netloc, path, query, fragment = urlsplit(insecure_source_url)
                secure_destination_url = urlunsplit((secure_scheme, netloc, path, query, fragment))
                if secure_destination_url == insecure_source_url:
                    return applicaton(environ, start_response)

                start_response("301 Moved Permanently", [("Location", secure_destination_url)])

                return [b'']

            return applicaton(environ, start_response)

        return _secure_redirect

    return _wrap_application
