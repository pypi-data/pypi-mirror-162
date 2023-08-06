import logging

from py_fastapi_logging.formatters.base import BaseFormatter


class SimpleLogFormatter(BaseFormatter):
    def _format_log(self, record: logging.LogRecord) -> str:
        log_str = f"[{self._format_date(record.created)}] "
        log_str += f"{record.levelname} "
        if hasattr(record, "progname"):
            progname = record.progname
        else:
            progname = record.module
        log_str += f" -- {progname}: "

        if hasattr(record, "request_id"):
            log_str += f"[{record.request_id}] "
        if hasattr(record, "tags"):
            log_str += f"{record.tags} "
        if hasattr(record, "message"):
            msg = record.message % record.args
            log_str += f"{msg}"

        elif hasattr(record, "msg"):
            msg = record.msg % record.args
            log_str += f"{msg}"

        if record.exc_info:
            log_str += f"{record.exc_info[1]}\n{self.formatException(record.exc_info)}"

        if hasattr(record, "payload"):
            log_str += f"{record.payload}"

        return log_str
