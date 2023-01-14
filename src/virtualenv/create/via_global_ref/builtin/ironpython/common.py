from abc import ABCMeta
from collections import OrderedDict
from pathlib import Path

from virtualenv.create.describe import PosixSupports, WindowsSupports
from virtualenv.create.via_global_ref.builtin.ref import RefMust, RefWhen

from ..via_global_self_do import ViaGlobalRefVirtualenvBuiltin


class IronPython(ViaGlobalRefVirtualenvBuiltin, metaclass=ABCMeta):
    @classmethod
    def can_describe(cls, interpreter):
        return interpreter.implementation == "IronPython" and super().can_describe(interpreter)

    @classmethod
    def exe_stem(cls):
        return "ipy"


class CPythonPosix(IronPython, PosixSupports, metaclass=ABCMeta):
    """Create a CPython virtual environment on POSIX platforms"""

    @classmethod
    def _executables(cls, interpreter):
        host_exe = Path(interpreter.system_executable)
        major, minor = interpreter.version_info.major, interpreter.version_info.minor
        targets = OrderedDict((i, None) for i in ["python", f"python{major}", f"python{major}.{minor}", host_exe.name])
        must = RefMust.COPY if interpreter.version_info.major == 2 else RefMust.NA
        yield host_exe, list(targets.keys()), must, RefWhen.ANY


class IronPythonWindows(IronPython, WindowsSupports, metaclass=ABCMeta):
    @classmethod
    def _executables(cls, interpreter):
        # symlink of the python executables does not work reliably, copy always instead
        # - https://bugs.python.org/issue42013
        # - venv
        host = cls.host_python(interpreter)
        for path in (host.parent / n for n in {"ipy.exe", host.name}):
            yield host, [path.name], RefMust.COPY, RefWhen.ANY
        # for more info on pythonw.exe see https://stackoverflow.com/a/30313091
        python_w = host.parent / "ipyw.exe"
        yield python_w, [python_w.name], RefMust.COPY, RefWhen.ANY

    @classmethod
    def host_python(cls, interpreter):
        return Path(interpreter.system_executable)


__all__ = ["IronPython", "IronPythonWindows"]
