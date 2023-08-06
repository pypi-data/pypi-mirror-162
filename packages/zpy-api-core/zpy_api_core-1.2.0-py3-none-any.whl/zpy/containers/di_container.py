# Created by Noé Cruz | Zurckz 22 at 01/08/2022
# See https://www.linkedin.com/in/zurckz
import dataclasses
from functools import wraps
from inspect import isclass, signature
from typing import Callable, Optional, Any, Tuple
from zpy.logger import ZLogger
from zpy.utils.values import if_null_get
from zpy.app import zapp_context as ctx
import time


@dataclasses.dataclass
class DLazy:
    type: Any
    initializer: Callable[[Any], Any]


class DIContainer:

    def __init__(self, timeit: bool = False, x_logger: ZLogger = None,
                 notifier: Callable[[Any, Optional[Any]], None] = None) -> None:
        self.container: dict = dict()
        self.logger: ZLogger = if_null_get(x_logger, ctx().logger)
        self.timeit: bool = timeit
        self.notifier: Callable[[Any, Optional[Any]], None] = notifier
        self.throw_ex = True
        self.error_message_prefix = "Fatal"
        self.max_time_allowed = 5

    def with_notifier(self, notifier):
        self.notifier = notifier

    @classmethod
    def create(cls, timeit: bool = False, logger: ZLogger = None) -> 'DIContainer':
        return cls(timeit, logger)

    def setup(self, init_fn: Callable[['DIContainer'], None]) -> 'DIContainer':
        try:
            te = time.time()
            init_fn(self)
            ts = time.time()
            self.logger.info(f"🚀 Dependencies loaded successfully... {(ts - te) * 1000:2.2f} ms.")
        except Exception as e:
            self.logger.err("Failed to load dependencies...")
            if self.notifier:
                self.notifier(f"{self.error_message_prefix} - Failed to load dependencies: {str(e)}")
            if self.throw_ex:
                raise
        return self

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.container[key] = value

    def factory_register(self, x_type: Any, initializer: Callable[[Any], Any]):
        self[x_type] = self.__timeit__(self.timeit, initializer, x_type, self)

    def lazy_register(self, x_type, initializer: Callable[[Any], Any]):
        self[x_type] = DLazy(x_type, initializer)

    def get(self, x_type) -> Optional[Any]:
        dependency = self.container.get(x_type, None)

        if isinstance(dependency, DLazy):
            self.container[x_type] = self.__timeit__(self.timeit, dependency.initializer, x_type, self)
            return self.container[x_type]

        return dependency

    def __timeit__(self, timeit: bool, fn: Any, x_type: Any, *args):
        if not timeit:
            return fn(args[0])
        te = time.time()
        result = fn(args[0])
        ts = time.time()
        taken = ts - te
        self.logger.info(f"Dependency load time: {x_type} :: {taken * 1000:2.2f} ms.")
        if taken >= self.max_time_allowed:
            msg = f"The dependency: {str(x_type)} is exceeding the allowed time. Taken: {taken:2.2f} - Max: {self.max_time_allowed}s."
            self.logger.warn(msg)
            if self.notifier:
                self.notifier(msg)
        return result

    def __getattr__(self, item):
        return self.get(item)


zdi = DIContainer().create()


def populate(initializer, container):
    print(initializer)
    parameters_name: Tuple[str, ...] = tuple(signature(initializer).parameters.keys())
    parameters: Tuple[str, ...] = tuple(signature(initializer).parameters.items())
    print(parameters_name)
    print(parameters)

    @wraps(initializer)
    def _decorated(*args, **kwargs):
        # all arguments were passed
        # if len(args) == len(parameters_name):
        #    return service(*args, **kwargs)

        # if parameters_name == tuple(kwargs.keys()):
        #    return service(**kwargs)

        # all_kwargs = _resolve_kwargs(args, kwargs)
        return initializer(1, 2, 3)

    return _decorated


def inject(container: DIContainer = zdi):
    def _decorator(_service: Any) -> Any:
        if isclass(_service):
            setattr(
                _service,
                "__init__",
                populate(getattr(_service, "__init__"), container)
            )
            return _service

        return _service

    return _decorator
