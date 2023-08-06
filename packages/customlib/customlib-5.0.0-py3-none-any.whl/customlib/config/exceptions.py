# -*- coding: UTF-8 -*-

class BaseConfigError(Exception):
    """Base exception for all configuration errors."""


class BadParameterError(BaseConfigError):
    """Exception class used to signal parameters parsing errors."""
