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

    def _domain_redirect(environ: Dict[str, Any]):
        source_url = source_url_provider(environ)
        scheme, source_domain, source_path, source_query, source_fragment = urlsplit(url=source_url)

        if source_domain == target_domain:
            return None

        if source_domain in source_domains:
            target_scheme = force_target_scheme or scheme
            secure_destination_url = urlunsplit(
                (target_scheme, target_domain, source_path, source_query, source_fragment))

            def _redirect_to(environ: Dict, start_response: Callable):
                start_response("301 Moved Permanently", [("Location", secure_destination_url)])

                return ""

            return _redirect_to

    return _domain_redirect


def get_redirect_to_secure_scheme_preprocessor(is_insecure: Callable[[Dict[str, Any]], bool],
                                               source_url_provider: Callable[[Dict[str, Any]], str],
                                               secure_scheme: str = "https"):
    def _get_redirect_to(source_url: str) -> Optional[Callable[[Any], str]]:
        scheme, netloc, path, query, fragment = urlsplit(url=source_url)
        secure_destination_url = urlunsplit((secure_scheme, netloc, path, query, fragment))

        if secure_destination_url == source_url:
            return None

        def _redirect_to_secure_url(environ: Dict, start_response: Callable):
            start_response("301 Moved Permanently", [("Location", secure_destination_url)])

            return ""

        return _redirect_to_secure_url

    def _preprocess(environ: Dict[str, Any]) -> Optional[Callable[[Dict, Callable], str]]:
        if is_insecure(environ):
            insecure_source_url = source_url_provider(environ)
            redirect_to_secure_url = _get_redirect_to(source_url=insecure_source_url)

            return redirect_to_secure_url

    return _preprocess
