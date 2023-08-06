import json
import logging

from py_fastapi_logging.formatters.base import BaseFormatter
from py_fastapi_logging.schemas.base import BaseJsonLogSchema
from py_fastapi_logging.utils.extra import get_env_extra


class JSONLogFormatter(BaseFormatter):
    def _format_log(self, record: logging.LogRecord) -> dict:
        json_log_fields = BaseJsonLogSchema(
            timestamp=self._format_date(record.created),
            level=record.levelname,
        )

        for key in get_env_extra().keys():
            if hasattr(record, key):
                json_log_fields[key] = getattr(record, key)
            elif key == "progname":
                json_log_fields[key] = record.module

        json_log_fields["tags"] = record.tags if hasattr(record, "tags") else []

        if hasattr(record, "payload"):
            json_log_fields["payload"] = record.payload
        elif record.exc_info:
            try:
                json_log_fields["payload"] = {
                    "exception": {
                        "class": record.exc_info[0].__name__,
                        "message": str(record.exc_info[1]),
                        "backtrace": self.formatException(record.exc_info),
                    },
                }
            except Exception:
                json_log_fields["payload"] = {
                    "exception": {
                        "class": None,
                        "message": repr(record.exc_info),
                        "backtrace": None,
                    }
                }
        elif hasattr(record, "message"):
            json_log_fields["payload"] = {"message": record.message}
        elif hasattr(record, "msg"):
            json_log_fields["payload"] = {"message": record.getMessage()}
        return json.dumps(json_log_fields, ensure_ascii=False)
