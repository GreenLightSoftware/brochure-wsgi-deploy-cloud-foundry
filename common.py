from typing import Dict
from urllib.parse import urlunsplit


def url_from_environment(environ: Dict):
    scheme = environ.get("HTTP_X_FORWARDED_PROTO") or environ.get("wsgi.url_scheme")
    netloc = environ.get("HTTP_HOST")
    path = environ.get("PATH_INFO")
    query_string = environ.get("QUERY_STRING")
    fragment = None
    parsed_url = urlunsplit(components=(scheme, netloc, path, query_string, fragment,))

    return parsed_url
