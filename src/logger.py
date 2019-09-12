"""
Custom JSON log format.
"""
import logging
import json
import traceback
import json_logging
from pytz import timezone
from datetime import datetime


TIMEZONE = timezone('Europe/Rome')

json_logging.ENABLE_JSON_LOGGING = True


def extra(**kw):
    '''Add the required nested props layer'''
    return {'extra': {'props': kw}}


class CustomJSONLog(logging.Formatter):
    """
    Customized logger
    """
    def get_exc_fields(self, record):
        if record.exc_info:
            exc_info = self.format_exception(record.exc_info)
        else:
            exc_info = record.exc_text
        return {'exc_info': exc_info}

    @classmethod
    def format_exception(cls, exc_info):
        return ''.join(traceback.format_exception(*exc_info)) if exc_info else ''

    def format(self, record):
        json_log_object = {"datetime": datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                           "level": record.levelname,
                           "message": record.getMessage()
                           }
        json_log_object['data'] = {
            'logger_name': record.name,
            'module': record.module,
            'funcName': record.funcName,
            'filename': record.filename,
            'lineno': record.lineno,
            'thread': f'{record.threadName}[{record.thread}]'
        }
        if hasattr(record, 'props'):
            json_log_object['data'].update(record.props)

        if record.exc_info or record.exc_text:
            json_log_object['data'].update(self.get_exc_fields(record))

        return json.dumps(json_log_object)


def logger_init():
    json_logging.__init(custom_formatter=CustomJSONLog)
