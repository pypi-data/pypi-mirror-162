from dataclasses import dataclass
from enum import IntEnum
from datetime import datetime
from boltons.tbutils import ExceptionInfo # type: ignore # pylint: disable=import-error
from dataclasses_json import dataclass_json # type: ignore # pylint: disable=import-error
from types import TracebackType
from typing import Optional, Dict, Any


class Logger(IntEnum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    EXCEPTION = 60


@dataclass_json
@dataclass
class MSGException:
    exc_type: Optional[BaseException] = None
    value: str = ""
    traceback: Optional[TracebackType] = None

    @property
    def check(self) -> bool:
        return self.traceback is None

    @property
    def info(self) -> Dict[str, Any]:
        if self.check:
            einfo = ExceptionInfo.from_exc_info(
                self.exc_type,
                self.value,
                self.traceback)
            return einfo.to_dict()
        return {}

    def __str__(self):
        return f"{self.exc_type} : {self.value}"


@dataclass_json
@dataclass
class MessageLog:
    timestamp: datetime
    func_name: str
    level: Logger
    message: str
    error: MSGException

    @property
    def msg(self):
        return f"{self.timestamp} :: {self.func_name} :: {self.message}"

    @property
    def exception(self):
        return not self.error.check()

    @property
    def exc(self):
        return self.error.info

    @property
    def log(self):
        return (self.level, self.msg)

    def __str__(self):
        return f"""{self.func_name} :: {self.message}
        :> {self.exception}"""


    @property
    def rdb(self):
        data =  {
            "function": self.func_name,
            "DT_GEN": self.timestamp,
            "level": self.level,
            "message": self.message,
        }
        if self.exception:
            data["error"] = self.exc

        return data
