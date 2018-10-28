from typing import Iterable, Callable, Dict

from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response

from sparse_wsgi import get_sparse_wsgi_application


def get_sparse_werkzeug_application(preprocessors: Iterable[Callable] = None,
                                    path_rules: Dict[str, Callable] = None,
                                    exception_rules: Dict[int, Callable] = None):
    def get_url_map(rules):
        url_map = Map()
        [url_map.add(Rule(path, endpoint=response)) for path, response in rules.items()]

        return url_map

    def get_exception_handler_provider(rules):
        def _exception_handler_provider(exception, environ):
            handlers = {500: lambda env: Response(str(exception), status=500), **rules}
            code = getattr(exception, 'code', 500)

            return handlers[code](environ)

        return _exception_handler_provider

    def get_request_handler(rules):
        url_map = get_url_map(rules)

        def handle_request(environ):
            map_adapter = url_map.bind_to_environ(environ=environ)
            command, command_parameters = map_adapter.match()
            response_provider = command(**command_parameters)

            return response_provider

        return handle_request

    request_handler = get_request_handler(rules=path_rules)
    exception_handler = get_exception_handler_provider(rules=exception_rules)

    return get_sparse_wsgi_application(preprocessors=preprocessors,
                                       request_handler=request_handler,
                                       exception_handler_provider=exception_handler)
