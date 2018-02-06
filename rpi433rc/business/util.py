import logging


class LogMixin(object):
    """
    Example:

        >>> class Dummy(LogMixin):
        ...     def do_something_fancy(self):
        ...         self.logger.info("Begin")
        ...         # ...
        ...         self.logger.info("End")
    """
    @property
    def logger(self):
        return logging.getLogger(self.__class__.__name__)