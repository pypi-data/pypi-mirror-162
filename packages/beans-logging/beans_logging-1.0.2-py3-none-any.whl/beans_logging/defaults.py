# -*- coding: utf-8 -*-

import os
import sys

from box import Box


## Defualt options for logger
_logger_config = {
    "app_name": os.path.splitext(os.path.basename(sys.argv[0]))[0].strip().replace(' ', '_').lower(),
    "level": "INFO",
    "use_color": True,
    "use_icon": False,
    "use_backtrace": True,
    "use_diagnose": False,
    "std_format_str": "[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{lvlname:<5}</level> | <w>{name}:{line}</w>]: <level>{message}</level>",
    "use_log_file": False,
    "logs_dir": os.path.join(os.getcwd(), "logs"),
    "file_format_str": "[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {lvlname:<5} | {file}:{line}]: {message}",
    "rotate_when":
    {
        "each_days": 1,
        "at_hour": 0,
        "at_minute": 0,
        "at_second": 0
    },
    "rotate_file_size": 10000000,
    "backup_file_count": 50,
    "file_encoding": "utf8",
    "all_log_filename": "{app_name}.std.all.log",
    "err_log_filename": "{app_name}.std.err.log",
    "use_log_json": False,
    "use_custom_json": False,
    "json_all_log_filename": "{app_name}.json.all.log",
    "json_err_log_filename": "{app_name}.json.err.log",
    "ignore_modules": [],
    "mute_modules": [],
    "include_modules": [],
    "configs_dir": os.path.join(os.getcwd(), "configs")
}

logger_config = Box(_logger_config)
