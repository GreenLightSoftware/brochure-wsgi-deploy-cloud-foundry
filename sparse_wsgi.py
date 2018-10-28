from typing import Callable


def get_sparse_wsgi_application(preprocessors=None,
                                request_handler=None,
                                exception_handler_provider=None):
    def _ok(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'200 OK\n']

    def _internal_server_error_provider(exception):
        def _internal_server_error(environ, start_response):
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [b'500 Internal Server Error\n']

        return _internal_server_error

    def _sparse_wsgi(environ, start_response: Callable):
        # noinspection PyBroadException
        try:
            for preprocessor in preprocessors or tuple():
                response_provider = preprocessor(environ=environ)
                if response_provider is not None:
                    return response_provider(environ=environ, start_response=start_response)

            sparse_request_handlers: Callable = request_handler or _ok
            response_provider = sparse_request_handlers(environ)
            return response_provider(environ=environ, start_response=start_response)

        except Exception as exception:
            sparse_exception_handler_provider = exception_handler_provider or _internal_server_error_provider
            response_provider: Callable = sparse_exception_handler_provider(exception=exception, environ=environ)
            return response_provider(environ, start_response)

    request_handler = request_handler or _ok
    exception_handler_provider = exception_handler_provider or _internal_server_error_provider

    return _sparse_wsgi
