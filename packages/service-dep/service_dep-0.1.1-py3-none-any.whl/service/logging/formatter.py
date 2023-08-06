"""Logging factory.

Check your log configuration before wasting time here.
Attention: Do not import any project modules or func here (!!!).

"""

import os
import sys
import logging
import json

from collections.abc import Mapping
from copy import copy

from typing import Dict, List
import traceback
from pathlib import Path

from logging import LogRecord
from logging_json import JSONFormatter
from logging_json._formatter import (  # noqa
    _value as formatter_value,  # noqa
    _extra_attributes as log_extra_attrs,  # noqa
    default_converter,
)

from . import style


def formatter_from_event_type(event_type: int):
    """Map formatter to event."""
    log_styles = {
        logging.NOTSET: style.StyleDefault,
        logging.DEBUG: style.StyleDebug,
        logging.INFO: style.StyleInfo,
        logging.WARNING: style.StyleWarning,
        logging.CRITICAL: style.StyleError,
        logging.ERROR: style.StyleError,
        logging.FATAL: style.StyleError,
    }
    try:
        return log_styles[event_type]
    except (AttributeError, KeyError, IndexError):
        return style.StyleDefault


class ServiceFormatter(JSONFormatter):
    """Service formatter."""

    @classmethod
    def clear_trace(cls, lines: List[str]) -> List[str]:
        """Clear exc trace."""
        trace_buff = []
        for line in lines:
            buff = line.strip('')
            buff = buff.strip('\"')
            buff = buff.replace('\n', '')
            buff = buff.replace("\"/", '/')
            buff = buff.replace('\"', '')
            if buff.startswith('None'):
                continue
            trace_buff.append(buff)
        return trace_buff

    def need_colorize(self) -> bool:  # noqa
        """Need colorize."""
        return not any([
            True if str(_opt).upper().startswith('KUBERNETES') else False
            for _opt in dict(os.environ).keys()
        ])

    def msg_no_specials(self, text: str) -> str:  # noqa
        """Msg without specials."""
        _no_sql = ('\n', '\t')
        for _spec in _no_sql:
            text = str(text).replace(_spec, ' ')
        return text

    def wrap_error(self, message: Dict) -> Dict:
        """Wrap error message."""
        exc_type, exc_val, exc_tb = sys.exc_info()
        if exc_type:
            message['exc_type'] = exc_type.__name__
        if exc_val and str(exc_val) != '':
            message['exc_value'] = exc_val

        exc_lines = traceback.format_exception(exc_type, exc_val, exc_tb)
        exc_lines = self.clear_trace(exc_lines)

        if exc_lines:
            message['msg'] = exc_lines

        return message

    def uvicorn_access_message(self, record) -> str:  # noqa
        """Extract uvicorn access message."""
        recordcopy = copy(record)
        (
            client_addr,
            method,
            full_path,
            http_version,
            status_code,
        ) = recordcopy.args
        return "%s %s HTTP/%s" % (method, full_path, http_version)

    def message_from_record(self, record: LogRecord) -> Dict:
        """Message from record."""
        message = {
            field_name: formatter_value(record, field_value)
            for field_name, field_value in self.fields.items()
        }

        if isinstance(record.msg, Mapping):
            message.update(record.msg)
        else:
            message[self.message_field_name] = super().formatMessage(record)

        message.update(log_extra_attrs(record))

        if record.levelname in ('CRITICAL', 'ERROR'):
            return self.wrap_error(message)

        msg = self.msg_no_specials(record.message or record.msg)

        if record.name == 'uvicorn.access':
            msg = self.uvicorn_access_message(record)

        message['msg'] = msg

        return message

    def path_from_record(self, record: LogRecord) -> str:  # noqa
        """Path from record."""
        caller = Path(record.pathname)

        return '../{parent}/{name}/{script}'.format(
            parent=caller.parent.parent.name,
            name=caller.parent.name,
            script=caller.name,
        )

    def format(self, record: LogRecord):
        """Format."""
        super().format(record)

        message = self.message_from_record(record)
        message['path'] = self.path_from_record(record)

        if len(message) == 1 and self.message_field_name in message:
            return super().formatMessage(record)

        if self.need_colorize():
            return style.highlight(
                json.dumps(
                    message,
                    default=default_converter,
                    indent=4,
                    ensure_ascii=False,
                ),
                lexer=style.JsonLexer(),
                formatter=style.Terminal256Formatter(
                    style=formatter_from_event_type(record.levelno),
                ),
            )

        return json.dumps(message, default=default_converter)


__all__ = ('JSONFormatter', 'ServiceFormatter')
