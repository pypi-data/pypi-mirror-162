import contextlib
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Type

import rpyc
from apscheduler.util import obj_to_ref, undefined
from contextvars import ContextVar
from rpyc.core.protocol import Connection as RemoteConnection

from dropland.log import tr, worker_logger


# noinspection PyProtectedMember
def register_exception(exc: Type[Exception]):
    class_key = f'{exc.__module__}.{exc.__name__}'
    rpyc.core.vinegar._generic_exceptions_cache[class_key] = exc


class RemoteScheduler(object):
    def __init__(self, host: str, port: int, num_connect_attempts: int = 10, rpc_timeout: Optional[timedelta] = None):
        self._host = host
        self._port = port
        self._conn: ContextVar[RemoteConnection] = ContextVar('_conn')
        self._config = rpyc.core.protocol.DEFAULT_CONFIG.copy()
        self._config.update({'allow_public_attrs': True, 'allow_pickle': True})
        self._num_connect_attempts = max(1, num_connect_attempts)
        if rpc_timeout:
            self._config['sync_request_timeout'] = rpc_timeout.total_seconds()

    @contextlib.contextmanager
    def _ensure_connection(self):
        conn = self._conn.get(None)
        if conn:
            yield conn
        else:
            with rpyc.connect(self._host, self._port, config=self._config, keepalive=True) as conn:
                worker_logger.debug(tr('dropland.scheduler.service.rpc-connected')
                                    .format(host=self._host, port=self._port))

                token = self._conn.set(conn)
                try:
                    yield conn
                finally:
                    if self._conn.get(None) is conn:
                        self._conn.reset(token)
                        worker_logger.debug(tr('dropland.scheduler.service.rpc-disconnected')
                                            .format(host=self._host, port=self._port))

    def _execute(self, func: Callable[[RemoteConnection], Any]):
        attempt_num = self._num_connect_attempts

        while attempt_num > 0:
            with self._ensure_connection() as conn:
                try:
                    return func(conn)
                except EOFError as e:
                    worker_logger.error(tr('dropland.scheduler.service.rpc-exception')
                                        .format(attempt_num=attempt_num, e=e))
                    attempt_num -= 1

        return None

    def _prepare_args(self, args: tuple) -> tuple:
        result = []
        for value in args:
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%dT%H:%M:%S.%f')
            elif isinstance(value, type(undefined)):
                value = undefined
            elif isinstance(value, Callable):
                value = obj_to_ref(value)
            result.append(value)
        return tuple(result)

    def _prepare_kwargs(self, args: dict) -> dict:
        for k, value in args.items():
            if isinstance(value, datetime):
                args[k] = value.strftime('%Y-%m-%dT%H:%M:%S.%f')
            elif isinstance(value, type(undefined)):
                args[k] = undefined
            elif isinstance(value, Callable):
                args[k] = obj_to_ref(value)
        return args

    def __getattr__(self, item):
        res = self._execute(lambda conn: getattr(conn.root, item))
        if not isinstance(res, Callable):
            return res

        def wrapped(*args, **kwargs):
            def _call(conn: RemoteConnection):
                func = getattr(conn.root, item)
                return func(*self._prepare_args(args), **self._prepare_kwargs(kwargs)) if func else None

            return self._execute(_call)

        return wrapped
