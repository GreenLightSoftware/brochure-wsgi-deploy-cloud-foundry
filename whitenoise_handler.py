from functools import partial

from whitenoise import WhiteNoise


def get_static_file_handler_provider():
    whitenoise = WhiteNoise(None)

    def provide_handler(url, static_file_path):
        favicon_static_file = whitenoise.get_static_file(path=static_file_path, url=url)
        whitenoise.files[url] = favicon_static_file

        favicon_handler = partial(whitenoise.serve, static_file=favicon_static_file)

        return favicon_handler

    return provide_handler
