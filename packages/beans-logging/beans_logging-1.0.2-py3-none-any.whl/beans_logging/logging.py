# -*- coding: utf-8 -*-

import os
import sys
import json
import errno
import logging
import datetime
import traceback

import yaml
from box import Box
from loguru import logger
from dotenv import load_dotenv

from .defaults import logger_config
from .__version__ import __version__



class InterceptHandler(logging.Handler):
    def emit(self, record) -> None:

        # print(record.name)

        for _module_name in logger_config.ignore_modules:
            if  _module_name in record.name:
                return

        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class Rotator:
    def __init__(self, *, size: int, at: datetime.time):
        _now = datetime.datetime.now()
        self._size_limit = size
        self._time_limit = _now.replace(hour=at.hour, minute=at.minute, second=at.second)

        if self._time_limit <= _now:
            # The current time is already past the target time so it would rotate already.
            # Add one day to prevent an immediate rotation.
            self._time_limit += datetime.timedelta(days=logger_config.rotate_when.each_days)

    def should_rotate(self, message, file) -> bool:
        file.seek(0, 2)
        if self._size_limit < (file.tell() + len(message)):
            return True

        if self._time_limit.timestamp() < message.record["time"].timestamp():
            self._time_limit += datetime.timedelta(days=logger_config.rotate_when.each_days)
            return True
        return False


## Filter for adding short level name:
def _add_lvlname(record: dict) -> dict:
    record["lvlname"] = record["level"].name
    if record["level"].name == "SUCCESS":
        record["lvlname"] = "OK"
    elif record["level"].name == "WARNING":
        record["lvlname"] = "WARN"
    elif record["level"].name == "CRITICAL":
        record["lvlname"] = "CRIT"
    return record


## Printing message based on log level to stdout or stderr:
def _std_sink(message) -> None:
    if message.record["level"].no < 40:
        sys.stdout.write(message)
    else:
        sys.stderr.write(message)


## Custom json formatter:
def _custom_json_formatter(record: dict):
    _error = None
    if record["exception"]:
        _error = {}
        _error_type, _error_value, _error_traceback = record["exception"]
        _error["type"] = _error_type.__name__
        _error["value"] = str(_error_value)
        _error["traceback"] = "".join(traceback.format_tb(_error_traceback))

    _extra = None
    if record["extra"] and (0 < len(record["extra"])):
        _extra = record["extra"]

    _json_format = {
        "timestamp": record["time"].strftime("%Y-%m-%dT%H:%M:%S%z"),
        "level": record["level"].name,
        "level_no": record["level"].no,
        "file": record["file"].name,
        "line": record["line"],
        "name": record["name"],
        "process": {
            "name": record["process"].name,
            "id": record["process"].id
        },
        "thread_name": {
            "name": record["thread"].name,
            "id": record["thread"].id
        },
        "message": record["message"],
        "extra": _extra,
        "error": _error,
        "elapsed": str(record["elapsed"]),
    }

    record["custom_json"] = json.dumps(_json_format)
    return "{custom_json}\n"


def remove_loggers() -> None:
    global _loggers_id_list

    for _ in _loggers_id_list:
        logger.remove()
    _loggers_id_list.clear()


_loggers_id_list = [0]
def init_loggers(**kwargs: dict) -> list:
    global _loggers_id_list
    global logger_config

    ## Loading environment variables from .env file, if it's exits:
    _env_filename = ".env"
    _env_path = os.path.join(os.getcwd(), _env_filename)
    if os.path.isfile(_env_path):
        load_dotenv(dotenv_path=_env_path, override=True)

    logger_config.merge_update(Box(kwargs))

    ## Loading config from file, if it's exits:
    _yaml_config_path = os.path.join(logger_config.configs_dir, "logger.yaml")
    if not os.path.isfile(_yaml_config_path):
        _yaml_config_path = os.path.join(logger_config.configs_dir, "logger.yml")
    _json_config_path = os.path.join(logger_config.configs_dir, "logger.json")

    if os.path.isfile(_yaml_config_path):
        try:
            with open(_yaml_config_path, "r", encoding="utf8") as _yaml_config_file:
                logger_config.merge_update(Box(yaml.safe_load(_yaml_config_file)["logger"]))
        except Exception:
            logger.exception(f"Failed to load '{_yaml_config_path}' yaml config file.")
            exit(2)
    elif os.path.isfile(_json_config_path):
        try:
            with open(_json_config_path, "r", encoding="utf8") as _json_config_file:
                logger_config.merge_update(Box(json.load(_json_config_file)["logger"]))
        except Exception:
            logger.exception(f"Failed to load '{_json_config_path}' json config file.")
            exit(2)


    ## Checking environment for DEBUG option:
    _is_debug = False
    _ENV = str(os.getenv("ENV")).strip().lower()
    _DEBUG = str(os.getenv("DEBUG")).strip().lower()
    if (_DEBUG == "true") or ((_ENV == "development") and ((_DEBUG == "none") or (_DEBUG == ""))):
        _is_debug = True

    if _is_debug and (logger_config.level != "TRACE"):
        logger_config.level = "DEBUG"

    if logger_config.level == "TRACE":
        logger_config.use_diagnose = True

    if logger_config.use_icon:
        logger_config.std_format_str = logger_config.std_format_str.replace("lvlname:<5", "level.icon:<4")

    # if logger_config.use_color:
    #     ## Checking terminal could support xterm colors:
    #     _TERM = str(os.getenv("TERM")).strip()
    #     if (not "xterm" in _TERM):
    #         logger_config.use_color = False


    remove_loggers()

    ## Initializing std stream log handler:
    _loggers_id_list.append(
        logger.add(
            _std_sink,
            level=logger_config.level,
            format=logger_config.std_format_str,
            colorize=logger_config.use_color,
            filter=_add_lvlname,
            backtrace=logger_config.use_backtrace,
            diagnose=logger_config.use_diagnose
        )
    )

    ## Checking log file handlers enabled or not:
    if logger_config.use_log_file or logger_config.use_log_json:

        if os.getenv("APP_NAME") and (os.getenv("APP_NAME").strip()):
            logger_config.app_name = os.getenv("APP_NAME").strip().replace(" ", "_").lower()

        if os.getenv("PY_LOGS_DIR") and os.getenv("PY_LOGS_DIR").strip():
            logger_config.logs_dir = os.getenv("PY_LOGS_DIR").strip()

        if not os.path.isdir(logger_config.logs_dir):
            logger.debug(f"'{logger_config.logs_dir}' directory doesn't exist!")
            try:
                os.makedirs(logger_config.logs_dir)
            except Exception as err:
                if err.errno == errno.EEXIST:
                    logger.debug(f"'{logger_config.logs_dir}' directory already exists.")
                else:
                    logger.exception(f"Failed to create '{logger_config.logs_dir}' directory.")
                    exit(2)
            logger.debug(f"Successfully created '{logger_config.logs_dir}' directory!")

        ## Setting up log file handlers:
        _rotate_when = datetime.time(
            logger_config.rotate_when.at_hour,
            logger_config.rotate_when.at_minute,
            logger_config.rotate_when.at_second
        )

        if logger_config.use_log_file:
            ## Initializing log file handler:
            _out_rotator = Rotator(size=logger_config.rotate_file_size, at=_rotate_when)
            _log_path = os.path.join(
                logger_config.logs_dir,
                logger_config.all_log_filename.format(app_name=logger_config.app_name)
            )

            _loggers_id_list.append(
                logger.add(
                    _log_path,
                    level=logger_config.level,
                    format=logger_config.file_format_str,
                    rotation=_out_rotator.should_rotate,
                    retention=logger_config.backup_file_count,
                    encoding=logger_config.file_encoding,
                    enqueue=True,
                    backtrace=logger_config.use_backtrace,
                    diagnose=logger_config.use_diagnose
                )
            )

            ## Initializing error log file handler:
            _err_rotator = Rotator(size=logger_config.rotate_file_size, at=_rotate_when)
            _log_path = os.path.join(
                logger_config.logs_dir,
                logger_config.err_log_filename.format(app_name=logger_config.app_name)
            )

            _loggers_id_list.append(
                logger.add(
                    _log_path,
                    level="WARNING",
                    format=logger_config.file_format_str,
                    rotation=_err_rotator.should_rotate,
                    retention=logger_config.backup_file_count,
                    encoding=logger_config.file_encoding,
                    enqueue=True,
                    backtrace=logger_config.use_backtrace,
                    diagnose=logger_config.use_diagnose
                )
            )

        if logger_config.use_log_json:
            _json_out_rotator = Rotator(size=logger_config.rotate_file_size, at=_rotate_when)
            _json_err_rotator = Rotator(size=logger_config.rotate_file_size, at=_rotate_when)

            _json_format = ""
            _serialize = True
            if logger_config.use_custom_json:
                _json_format = _custom_json_formatter
                _serialize = False

            ## Initializing json log file handler:
            _log_path = os.path.join(
                logger_config.logs_dir,
                logger_config.json_all_log_filename.format(app_name=logger_config.app_name)
            )

            _loggers_id_list.append(
                logger.add(
                    _log_path,
                    level=logger_config.level,
                    format=_json_format,
                    serialize=_serialize,
                    rotation=_json_out_rotator.should_rotate,
                    retention=logger_config.backup_file_count,
                    encoding=logger_config.file_encoding,
                    enqueue=True,
                    backtrace=logger_config.use_backtrace,
                    diagnose=logger_config.use_diagnose
                )
            )

            ## Initializing json error log file handler:
            _log_path = os.path.join(
                logger_config.logs_dir,
                logger_config.json_err_log_filename.format(app_name=logger_config.app_name)
            )

            _loggers_id_list.append(
                logger.add(
                    _log_path,
                    level="WARNING",
                    format=_json_format,
                    serialize=_serialize,
                    rotation=_json_err_rotator.should_rotate,
                    retention=logger_config.backup_file_count,
                    encoding=logger_config.file_encoding,
                    enqueue=True,
                    backtrace=logger_config.use_backtrace,
                    diagnose=logger_config.use_diagnose
                )
            )

    _intercept_handler = InterceptHandler()
    logging.basicConfig(handlers=[_intercept_handler], level=0, force=True)

    # _seen_mod = set()
    # for _mod_name in list(logging.root.manager.loggerDict.keys()):
    #     if _mod_name not in _seen_mod:
    #         _base_mod = _mod_name.split(".")[0]
    #         _seen_mod.add(_base_mod)
    #         logging.getLogger(_base_mod).handlers = [_intercept_handler]

    for _include_module in logger_config.include_modules:
        logging.getLogger(_include_module).handlers = [_intercept_handler]

    for _mute_module in logger_config.mute_modules:
        _logger = logging.getLogger(_mute_module)
        _logger.handlers = []
        # _logger.propagate = False
        # _logger.disabled = True

    return _loggers_id_list


init_loggers()
