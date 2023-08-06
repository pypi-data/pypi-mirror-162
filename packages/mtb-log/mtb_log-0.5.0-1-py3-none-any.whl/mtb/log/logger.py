"""
## MTB Logger

This is a basic custom logger for MTB projects.
It includes colors, a success level, and extra things like titles and lists.

### Usage:

```python
log = mkLogger("log_name")

log.success("A succesful message")
log.error("An error message")
log.warning("An error message")
log.info("An info message")
log.debug("A debug message")
log.critical("A critical message")
log.fatal("A fatal message")

log.debug("A list of things:", list=["Orange", "Apple", "Banana"])
```
"""


import contextlib
import logging

from ast import literal_eval
import threading
from typing import Dict, Union
from .list import showlist

from .title import bigtitle, boxtitle

# - from .nf import NF


# between WARNING and INFO
SUCCESS = 25
_lock = threading.RLock()


def _acquireLock():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    if _lock:
        _lock.acquire()


def _releaseLock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock:
        _lock.release()


# - nf = NF()
# logging_level = logging.DEBUG


class ColoredLogger(logging.Logger):

    _cache = {}

    def __init__(self, name: str, level=logging.WARNING) -> None:
        super().__init__(name, level)

    def info(self, message, *args, **kwargs):
        self._log_it(logging.INFO, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self._log_it(logging.DEBUG, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log_it(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log_it(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._log_it(logging.CRITICAL, message, *args, **kwargs)

    def success(self, message, *args, **kwargs):
        self._log_it(SUCCESS, message, *args, **kwargs)

    supported_args = ["simple", "title", "list", "box"]

    def _log_it(self, level: int, message, *args, **kwargs):
        simple = kwargs.get("simple", False)

        if "title" in kwargs:
            message = bigtitle(kwargs["title"], return_str=True) + message
            simple = True
        if "list" in kwargs:
            message = showlist(
                kwargs["list"], return_str=True, style="line", title=message
            )
            simple = True

        if "box" in kwargs and kwargs["box"]:
            message = boxtitle(message, return_str=True)
            simple = True

        unsuported = [arg for arg in kwargs if arg not in self.supported_args]

        if len(unsuported):
            print(f"\nmtb.log: UNSUPORTED ARG PROVIDED: {unsuported}\n")

        if self.level <= level:
            self._log(level, message, args, extra={"simple": simple})


_loggerClass = ColoredLogger


class Manager(logging.Manager):
    """
    There is [under normal circumstances] just one Manager instance, which
    holds the hierarchy of loggers.
    """

    loggerDict: Dict[str, Union[ColoredLogger, logging.PlaceHolder]] = {}
    loggerClass: Union[type[ColoredLogger], None] = None
    # def __init__(self, rootnode):
    #     """
    #     Initialize the manager with the root node of the logger hierarchy.
    #     """
    #     super().__init__(rootnode)

    def setLoggerClass(self, klass):
        """
        Set the class to be used when instantiating a logger with this Manager.
        """
        if klass != ColoredLogger and not issubclass(klass, ColoredLogger):
            raise TypeError(
                f"logger not derived from mtb.log.ColoredLogger: {klass.__name__}"
            )

        self.loggerClass = klass

    def _fixupChildren(self, ph, alogger):
        """
        Ensure that children of the placeholder ph are connected to the
        specified logger.
        """
        name = alogger.name
        namelen = len(name)
        for c in ph.loggerMap.keys():
            # The if means ... if not c.parent.name.startswith(nm)
            if c.parent.name[:namelen] != name:
                alogger.parent = c.parent
                c.parent = alogger

    def _fixupParents(self, alogger):
        """
        Ensure that there are either loggers or placeholders all the way
        from the specified logger to the root of the logger hierarchy.
        """
        name = alogger.name
        i = name.rfind(".")
        rv = None
        while (i > 0) and not rv:
            substr = name[:i]
            if substr not in self.loggerDict:
                self.loggerDict[substr] = logging.PlaceHolder(alogger)
            else:
                obj = self.loggerDict[substr]
                if isinstance(obj, ColoredLogger):
                    rv = obj
                else:
                    assert isinstance(obj, logging.PlaceHolder)
                    obj.append(alogger)
            i = name.rfind(".", 0, i - 1)
        if not rv:
            rv = self.root
        alogger.parent = rv

    def getLogger(self, name) -> ColoredLogger:
        """
        Get a logger with the specified name (channel name), creating it
        if it doesn't yet exist. This name is a dot-separated hierarchical
        name, such as "a", "a.b", "a.b.c" or similar.

        If a PlaceHolder existed for the specified name [i.e. the logger
        didn't exist but a child of it did], replace it with the created
        logger and fix up the parent/child references which pointed to the
        placeholder to now point to the logger.
        """
        rv = None
        if not isinstance(name, str):
            raise TypeError("A logger name must be a string")
        _acquireLock()
        try:
            if name in self.loggerDict:
                rv = self.loggerDict[name]
                if isinstance(rv, logging.PlaceHolder):
                    ph = rv
                    rv = (self.loggerClass or _loggerClass)(name)
                    rv.manager = self
                    self.loggerDict[name] = rv
                    self._fixupChildren(ph, rv)
                    self._fixupParents(rv)
            else:
                rv = (self.loggerClass or _loggerClass)(name)
                rv.manager = self
                self.loggerDict[name] = rv
                self._fixupParents(rv)
        finally:
            _releaseLock()
        return rv

    def _clear_cache(self):
        """
        Clear the cache for all loggers in loggerDict
        Called when level changes are made
        """

        _acquireLock()
        for logger in self.loggerDict.values():
            if isinstance(logger, ColoredLogger):
                logger._cache.clear()
        self.root._cache.clear()
        _releaseLock()


class ColoredLogRecord(logging.LogRecord):
    simple: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = None


class RootLogger(ColoredLogger):
    """
    A root logger is not that different to any other logger, except that
    it must have a logging level and there is only one instance of it in
    the hierarchy.
    """

    def __init__(self, level):
        """
        Initialize the logger with the name "root".
        """
        ColoredLogger.__init__(self, "root", level)

    def __reduce__(self):
        return getLogger, ()


def getLogger(name=None) -> ColoredLogger:
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    if not name or isinstance(name, str) and name == root.name:
        return root
    return ColoredLogger.manager.getLogger(name)


root = RootLogger(logging.WARNING)
ColoredLogger.root = root
ColoredLogger.manager = Manager(ColoredLogger.root)


class ANSIColor(object):
    """
    Utility to handle ANSI color codes.
    """

    #: Tuple of available colors (most common ones)
    colors = {
        "bggrey": 100,
        "bgred": 41,
        "black": 30,
        "blue": 34,
        "cyan": 36,
        "green": 32,
        "magenta": 35,
        "red": 91,
        "white": 37,
        "yellow": 93,
    }

    _prefix = "\033["
    _suffix = "\033[0m"

    @classmethod
    def colored(cls, text, color: str = ...):
        """
        Returns text with color for terminals.
        """
        if color not in cls.colors:
            color = "white"

        clr = cls.colors[color]
        return f"{cls._prefix}%dm%s{cls._suffix}" % (clr, text)


class _ColoredFormatter(logging.Formatter):
    def __init__(
        self,
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=None,
        style="%",
    ):
        try:
            super().__init__(fmt, datefmt, style)  # type: ignore
        except Exception:
            super(_ColoredFormatter, self).__init__(fmt, datefmt)

    def format(self, record: ColoredLogRecord):
        msg = str(record.msg)
        with contextlib.suppress(Exception):
            print(literal_eval(msg).keys())
        color_mapping = {
            "INFO": "white",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bgred",
            "DEBUG": "yellow",
            "SUCCESS": "green",
        }
        # - icon_mapping = {
        # -     'INFO': 'nf-fa-info_circle',
        # -     'WARNING': 'nf-fa-warning',
        # -     'ERROR': 'nf-oct-x',
        # -     'CRITICAL': 'nf-fa-fire_extinguisher',
        # -     'DEBUG': 'nf-fa-bug',
        # -     'SUCCESS': 'nf-fa-check_circle'
        # - }

        clr = color_mapping.get(record.levelname, "white")

        # - ico = icon_mapping.get(record.levelname, '')
        # - ico = nf.get(ico)
        # - if ico:
        # -     ico += " "
        # - else:
        # -     ico = ""
        ico = ""
        # return colored(ico + record.filename + ': ' + msg , clr)
        if record.levelname in ["CRITICAL", "ERROR"]:
            return ANSIColor.colored(
                f"{ico}{record.name} ({record.lineno}) | {msg}", clr
            )
        if hasattr(record, "simple") and record.simple:
            return ANSIColor.colored(msg, clr)
        else:
            return ANSIColor.colored(
                f"{ico}{record.name}@{record.lineno} | {msg}", clr
            )


def mkLogger(prefix="", default_level=logging.WARNING) -> ColoredLogger:

    """

    **Simple Logger shared across MTB Projects:**

        * Require Patched Icon fonts.
        * Add a SUCCESS level.
        * Add Colors

    ------------

    :param name:    Name of the log
    :param default_level:   Defaults to DEBUG
    :return:    a Logger Object
    """

    logger = getLogger(prefix)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    formatter = _ColoredFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # add success level
    logging.addLevelName(SUCCESS, "SUCCESS")

    # setattr(logger, "success", log_success)
    # setattr(logger, "debug", log_debug)
    # setattr(logger, "warning", log_warning)
    # setattr(logger, "warn", log_warning)
    # setattr(logger, "error", log_error)
    # setattr(logger, "critical", log_critical)
    # setattr(logger, "info", log_info)

    # set current level
    logger.setLevel(default_level)

    return logger


__all__ = ["mkLogger", "ColoredLogger"]
