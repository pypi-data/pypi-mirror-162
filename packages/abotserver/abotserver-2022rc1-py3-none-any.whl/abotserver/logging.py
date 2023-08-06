import traceback
import logging

from gunicorn import glogging

logging.basicConfig()

__all__ = ("Logger", )


class Logger(glogging.Logger):

    access_fmt = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"

    def access(self, resp, req, environ, request_time):
        """ See http://httpd.apache.org/docs/2.0/logs.html#combined
        for format details
        """

        if not (self.cfg.accesslog or self.cfg.logconfig or
           self.cfg.logconfig_dict or
           (self.cfg.syslog and not self.cfg.disable_redirect_access_to_syslog)):
            return

        # wrap atoms:
        # - make sure atoms will be test case insensitively
        # - if atom doesn't exist replace it by '-'
        safe_atoms = self.atoms_wrapper_class(self.atoms(resp, req, environ,
            request_time))

        try:
            self.access_log.info(self.cfg.access_log_format, safe_atoms)
        except:
            self.error(traceback.format_exc())


class LoggingMixin:
    """Convenience super-class to have a logger configured with the class name"""

    def __init__(self, context=None):
        self._set_context(context)

    @property
    def log(self) -> Logger:
        """Returns a logger."""
        try:
            # FIXME: LoggingMixin should have a default _log field.
            return self._log  # type: ignore
        except AttributeError:
            self._log = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)
            return self._log

    def _set_context(self, context):
        if context is not None:
            set_context(self.log, context)


def set_context(logger, value):
    """
    Walks the tree of loggers and tries to set the context for each handler

    :param logger: logger
    :param value: value to set
    """
    _logger = logger
    while _logger:
        for handler in _logger.handlers:
            try:
                handler.set_context(value)
            except AttributeError:
                # Not all handlers need to have context passed in so we ignore
                # the error when handlers do not have set_context defined.
                pass
        if _logger.propagate is True:
            _logger = _logger.parent
        else:
            _logger = None


