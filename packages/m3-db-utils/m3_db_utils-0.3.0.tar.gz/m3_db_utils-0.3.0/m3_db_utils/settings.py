from django.conf import (
    settings,
)


# Абсолютный путь до директории хранения логов
LOG_PATH = getattr(settings, 'LOG_PATH', '/tmp')
# Включение логирования SQL-запросов
SQL_LOG = getattr(settings, 'SQL_LOG', False)
# Включение дополнительного вывода трейса с местом отправки запроса
SQL_LOG_WITH_STACK_TRACE = getattr(settings, 'SQL_LOG_WITH_STACK_TRACE', False)
# Запрос форматируется со значением полей
SQL_LOG_WITH_PARAMETERS = getattr(settings, 'SQL_LOG_WITH_PARAMETERS', False)
# Максимальная длина запроса для обработки
SQL_LOG_MAX_SIZE = getattr(settings, 'SQL_LOG_MAX_SIZE', 25_000)
# Включает форматирование выводимых SQL-запросов
SQL_LOG_REINDENT = getattr(settings, 'SQL_LOG_REINDENT', False)

# Включение логирования запросов экшенов, помеченных декоратором log_query. Не требует включенного DEBUG-режима и
# включенного SQL_LOG
SQL_LOG_QUERY = getattr(settings, 'SQL_LOG_QUERY', False)
