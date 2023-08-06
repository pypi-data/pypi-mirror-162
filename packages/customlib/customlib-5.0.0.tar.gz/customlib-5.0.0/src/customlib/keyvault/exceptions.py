# -*- coding: UTF-8 -*-

class BaseVaultError(Exception):
    """Base exception class for backends module."""


class PasswordGetError(BaseVaultError):
    """Exception for password getter."""
