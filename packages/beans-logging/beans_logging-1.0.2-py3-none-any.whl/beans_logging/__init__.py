# -*- coding: utf-8 -*-

try:
    from beans_logging.logging import logger, init_loggers, remove_loggers, __version__
except ImportError:
    from .logging import logger, init_loggers, remove_loggers, __version__
