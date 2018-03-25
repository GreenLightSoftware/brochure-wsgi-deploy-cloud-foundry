import os

from brochure_wsgi.command_preprocessors.favicon_preprocessor import FaviconPreprocessor


def get_cf_favicon_preprocessor():
    favicon_url_path = "/favicon.ico"
    static_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")
    favicon_file_path = os.path.join(static_file_path, "favicon.ico")
    favicon_preprocessor = FaviconPreprocessor(favicon_url_path=favicon_url_path,
                                               favicon_file_path=favicon_file_path,
                                               request_path_provider=lambda e: e.get("PATH_INFO"))

    return favicon_preprocessor
