import logging
import traceback
from datetime import (
    datetime,
)
from time import (
    time,
)
from typing import (
    Any,
    List,
    Optional,
    Tuple,
)

from django.db.backends import (
    utils as backutils,
)
from m3_legacy.middleware import (
    get_thread_data,
)

from m3_db_utils.excludes import (
    is_path_must_be_excluded,
)
from m3_db_utils.settings import (
    SQL_LOG_QUERY,
    SQL_LOG_WITH_PARAMETERS,
    SQL_LOG_WITH_STACK_TRACE,
)


logger = logging.getLogger('sql_logger')


class DBUtilsCursorDebugWrapper(backutils.CursorDebugWrapper):
    """
    Расширение класса обертки над курсором.

    Создано для дополнения выводимого лога трейсбэком до строки, которая инициировала запрос.
    """

    def _get_stack_trace(self):
        """
        Получение трейса для выявления места вызова SQL-запроса.
        """
        lines = []
        stack = traceback.extract_stack()

        for path, linenum, func, line in stack:
            # уберем некоторые неинформативные строки
            # список исключаемых путей можно найти в
            # web_bb.debug_tools.ecxludes.EXCLUDED_PATHS
            if is_path_must_be_excluded(path):
                continue

            lines.append(f'File "{path}", line {linenum}, in {func}')
            lines.append(f'  {line}')

        return '\n'.join(lines)

    def _log_query(
        self,
        sql: str,
        duration: float,
        params: Tuple[Any],
        stack_trace: Optional[str],
    ):
        """
        Осуществляет логирование запроса.
        """
        sql = sql % tuple(params) if SQL_LOG_WITH_PARAMETERS and params else sql

        logger.info(
            msg=f'({duration}.3f) {sql}; args={params}',
            extra={'duration': duration, 'sql': sql, 'params': params, 'stack_trace': stack_trace},
        )

    def _log_queries(
        self,
        sql: str,
        duration: float,
        param_list: List[Tuple[Any]],
        stack_trace: Optional[str],
    ):
        """
        Осуществляет логирование запроса.
        """
        sql_queries = []

        for params in param_list:
            sql = sql % tuple(params) if SQL_LOG_WITH_PARAMETERS and params else sql

            sql_queries.append(sql)

        logger.info(
            msg=f'({duration}.3f) {sql}; args={param_list}',
            extra={
                'duration': duration,
                'sql': '\n'.join(sql_queries),
                'param_list': param_list,
                'stack_trace': stack_trace,
            },
        )

    def execute(self, sql, params=None):
        start = time()

        try:
            return super().execute(sql, params)
        finally:
            stop = time()
            duration = stop - start
            stack_trace = self._get_stack_trace() if SQL_LOG_WITH_STACK_TRACE else None

            self._log_query(sql=sql, duration=duration, params=params, stack_trace=stack_trace)

    def executemany(self, sql, param_list):
        start = time()

        try:
            return super().executemany(sql, param_list)
        finally:
            stop = time()
            duration = stop - start
            stack_trace = self._get_stack_trace() if SQL_LOG_WITH_STACK_TRACE else None

            self._log_queries(sql=sql, duration=duration, param_list=param_list, stack_trace=stack_trace)


# TODO EDUSCHL-18086 Перенести функциональность в DBUtilsCursorDebugWrapper и удалить обертку
class CursorWrapperWithLogging(backutils.CursorWrapper):
    """
    Расширение класса обертки над курсором.

    Создано для логирования трейсбэка до места, где создается запрос. Логируются только экшены, обёрнутые декоратором
    m3_db_utils.decorators.log_query(some_action_name). Где some_action_name - условное наименование экшена, для
    которого делается логирование.
    """

    @staticmethod
    def get_log_option_for_func():
        thread_locals = get_thread_data()

        return getattr(thread_locals, 'log_query', None)

    def execute(self, sql, params=None):
        if SQL_LOG_QUERY:
            log_query_name = self.get_log_option_for_func()
            start = datetime.now()

        try:
            return super().execute(sql, params)

        finally:
            if SQL_LOG_QUERY and log_query_name:
                print_stack_in_log(start, log_query_name)

    def executemany(self, sql, param_list):
        if SQL_LOG_QUERY:
            log_query_name = self.get_log_option_for_func()
            start = datetime.now()

        try:
            return super().executemany(sql, param_list)

        finally:
            if SQL_LOG_QUERY and log_query_name:
                print_stack_in_log(start, log_query_name)


def print_stack_in_project():
    """
    Функция печати трейсбэка в консоль
    """
    stack = traceback.extract_stack()
    for path, linenum, func, line in stack:
        # уберем некоторые неинформативные строки
        # список исключаемых путей можно найти в
        # web_bb.debug_tools.ecxludes.EXCLUDED_PATHS
        if is_path_must_be_excluded(path):
            continue

        print(f'File "{path}", line {linenum}, in {func}')
        print(f'  {line}')

    print('\n\n\n')


def print_stack_in_log(start, log_query_name):
    """
    Функция печати трейсбэка в файл
    """
    end = datetime.now()
    duration_delta = end - start
    duration_s = duration_delta.seconds
    duration_ms = duration_delta.microseconds

    stack = traceback.extract_stack()

    logger.info(f'--- QUERY {log_query_name}, {datetime.strftime(end, "%d.%m.%Y %H:%M:%S")} ---')
    logger.info(f'--- QUERY TIME: {duration_s}.{duration_ms} ---')

    for path, linenum, func, line in stack:
        # уберем некоторые неинформативные строки
        # список исключаемых путей можно найти в
        # web_bb.debug_tools.ecxludes.EXCLUDED_PATHS
        if is_path_must_be_excluded(path):
            continue

        logger.info(f'File "{path}", line {linenum}, in {func}')
        logger.info(f'  {line}')

    logger.info('\n')


def log_production_query():
    """
    Патчинг стандартной обертки
    """
    backutils.CursorWrapper = CursorWrapperWithLogging
