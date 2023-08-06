# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod

from .constants import SYSTEM, ES


class AbstractOsHandler(ABC):
    """Base abstract handler for all classes in this module."""

    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs

    def __enter__(self):
        self.acquire(*self._args, **self._kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __delete__(self, instance):
        instance.release()

    @abstractmethod
    def acquire(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def release(self, *args, **kwargs):
        raise NotImplementedError


class OsSleepInhibitor(AbstractOsHandler):
    """
    Prevent OS from sleep/hibernate.
    """

    if SYSTEM.upper() == "WINDOWS":
        from ctypes import windll

        def __init__(self, keep_screen_awake: bool = False):
            """
            Documentation:
            https://msdn.microsoft.com/en-us/library/windows/desktop/aa373208(v=vs.85).aspx

            :param keep_screen_awake: Keep the monitor active?
            """
            super(OsSleepInhibitor, self).__init__(keep_screen_awake)

        def acquire(self, keep_screen_awake: bool = False):
            """Prevents windows from entering sleep mode."""
            flags: int = ES.CONTINUOUS | ES.SYSTEM_REQUIRED

            if keep_screen_awake:
                flags |= ES.DISPLAY_REQUIRED

            self.windll.kernel32.SetThreadExecutionState(flags)

        def release(self):
            """Resets the flags and allows windows to enter sleep mode."""
            self.windll.kernel32.SetThreadExecutionState(ES.CONTINUOUS)

    elif SYSTEM.upper() == "LINUX":
        from subprocess import run

        def __init__(self):
            super(OsSleepInhibitor, self).__init__()

            self._command: str = "systemctl"
            self._args: tuple = ("sleep.target", "suspend.target", "hibernate.target", "hybrid-sleep.target")

        def __enter__(self):
            self.acquire()
            return self

        def acquire(self):
            """Prevents linux from entering sleep mode."""
            self.run([self._command, "mask", *self._args])

        def release(self):
            """Resets the flags and allows linux to enter sleep mode."""
            self.run([self._command, "unmask", *self._args])

    elif SYSTEM.upper() == "DARWIN":
        from subprocess import Popen, PIPE

        def __init__(self):
            super(OsSleepInhibitor, self).__init__()

            self._command: str = "caffeinate"
            self._break: bytes = b"\003"

        def __enter__(self):
            self.acquire()
            return self

        @property
        def process(self):
            return getattr(self, "_process")

        @process.setter
        def process(self, value):
            setattr(self, "_process", value)

        def acquire(self):
            """Prevents darwin from entering sleep mode."""
            self.process = self.Popen([self._command], stdin=self.PIPE, stdout=self.PIPE)

        def release(self):
            """Resets the flags and allows darwin to enter sleep mode."""
            self.process.stdin.write(self._break)
            self.process.stdin.flush()
            self.process.stdin.close()
            self.process.wait()

    else:  # pragma: no cover
        raise RuntimeError('Sleep inhibitor only defined for Windows, Linux and Darwin systems.')
