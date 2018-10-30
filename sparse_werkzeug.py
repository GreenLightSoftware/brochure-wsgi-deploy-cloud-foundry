from typing import Iterable, Callable, Dict, Any, Optional

from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response

from sparse_wsgi import get_sparse_wsgi_application


def get_sparse_werkzeug_application(preprocessors: Optional[Iterable[Callable]] = None,
                                    path_rules: Dict[str, Dict[str, Any]] = None,
                                    exception_rules: Optional[Dict[int, Callable]] = None):
    def get_url_map(rules: Optional[Dict] = None):
        final_rules = rules or {}
        url_map = Map()
        for path, options in final_rules.items():
            options.setdefault("methods", ("GET", "HEAD"))
            url_map.add(Rule(path, **options))

        return url_map

    def get_exception_handler_provider(rules: Optional[Dict[int, Callable]] = None):
        def _exception_handler_provider(exception, environ):
            final_rules = rules or {}

            def _generic_execption(status):
                return lambda env: Response(str(exception), status=status)

            handlers = {500: _generic_execption(500), **final_rules}
            status_code = getattr(exception, 'code', 500)

            return handlers.get(status_code, _generic_execption(status_code))(environ)

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
