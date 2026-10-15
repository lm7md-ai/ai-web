"""Import and network guards applied inside the isolated runner.

These raise immediately and visibly.  They are a mitigation layer, not a
substitute for OS-level isolation.
"""

from __future__ import annotations

import builtins
import sys
from importlib.abc import MetaPathFinder
from types import ModuleType
from typing import Sequence


class BlockedImportError(ImportError):
    def __init__(self, name: str) -> None:
        super().__init__(
            f"import of '{name}' is blocked in the isolated runner "
            "(network, process and low-level modules are not available)"
        )


# Imports performed by installed libraries are allowed even when the root
# module is on the deny-list: numpy/scipy/sklearn touch ``socket`` and
# ``subprocess`` at import time, and importing them is not the dangerous part.
# Learner code never gets that exemption.
_ALLOWED_IMPORTER_MARKERS = ("site-packages", "dist-packages")
_NEUTRAL_FRAMES = ("importlib._bootstrap", "<frozen importlib", "pfn/runtime/guards.py")


class _BlockingFinder(MetaPathFinder):
    def __init__(self, blocked: Sequence[str]) -> None:
        self._blocked = set(blocked)

    def find_module(self, fullname, path=None):  # legacy API, harmless
        return None

    @staticmethod
    def _importer_is_library() -> bool:
        """True when the import is requested by installed library code.

        Import-machinery frames are skipped so that the decision is made on the
        *caller* of the import statement, not on the interpreter internals.
        """
        frame = sys._getframe(1)
        for _ in range(12):
            if frame is None:
                break
            filename = frame.f_code.co_filename or ""
            if any(marker in filename for marker in _NEUTRAL_FRAMES):
                frame = frame.f_back
                continue
            return any(marker in filename for marker in _ALLOWED_IMPORTER_MARKERS)
        return False

    def find_spec(self, fullname, path=None, target=None):
        root = fullname.split(".")[0]
        if root in self._blocked and not self._importer_is_library():
            raise BlockedImportError(fullname)
        return None


def install_import_guard(blocked: Sequence[str]) -> None:
    sys.meta_path.insert(0, _BlockingFinder(blocked))


class NetworkBlockedError(RuntimeError):
    pass


def install_network_guard() -> None:
    """Disable outbound networking.

    Both ``socket.socket`` and the underlying ``_socket.socket`` constructor are
    replaced by raising stubs, so the block cannot be bypassed by reaching the
    C implementation directly.  Library code that merely imports ``socket``
    still works; any attempt to *create* a socket fails loudly.
    """
    def _deny(*_args, **_kwargs):
        raise NetworkBlockedError("network access is disabled in the isolated runner")

    try:
        import _socket
    except Exception:  # pragma: no cover
        _socket = None  # type: ignore[assignment]
    try:
        import socket
    except Exception:  # pragma: no cover
        return

    if _socket is not None and hasattr(_socket, "socket"):
        try:
            _socket.socket = _deny  # type: ignore[assignment]
        except (AttributeError, TypeError):  # pragma: no cover
            pass
    socket.socket = _deny  # type: ignore[assignment]
    socket.SocketType = _deny  # type: ignore[assignment]
    if hasattr(socket, "socketpair"):
        socket.socketpair = _deny  # type: ignore[assignment]
    for name in ("create_connection", "create_server", "getaddrinfo", "gethostbyname", "gethostbyname_ex"):
        if hasattr(socket, name):
            setattr(socket, name, _deny)


def install_builtin_guard() -> None:
    """Remove interactive/process-control builtins from untrusted code."""
    from pfn.runtime.policy import DANGEROUS_BUILTINS

    for name in DANGEROUS_BUILTINS:
        if hasattr(builtins, name):
            delattr(builtins, name)
    if hasattr(builtins, "open"):
        builtins.__dict__["_real_open"] = builtins.open  # keep an escape hatch for the worker

    import os

    def _no_fork(*_a, **_k):
        raise RuntimeError("process creation is disabled in the isolated runner")

    os.fork = _no_fork  # type: ignore[assignment]
    if hasattr(os, "posix_spawn"):
        os.posix_spawn = _no_fork  # type: ignore[assignment]
    if hasattr(os, "system"):
        os.system = _no_fork  # type: ignore[assignment]


# Files that must never be readable from learner code, even though ordinary
# filesystem reads are permitted (libraries legitimately read their own data).
SENSITIVE_PATTERNS: tuple[str, ...] = (
    "/etc/passwd",
    "/etc/shadow",
    "/proc/self/environ",
    "/proc/self/mem",
    ".ssh/",
    "id_rsa",
    "id_ed25519",
    ".aws/credentials",
    ".netrc",
    ".git-credentials",
    ".npmrc",
    ".pypirc",
)


def sandbox_open(root: str):
    """Return an ``open`` that constrains where learner code may read/write.

    * writes: only inside the sandbox run directory;
    * reads: allowed (libraries read their own data files), except for a
      deny-list of credential and system files.

    This narrows the blast radius; it is not a filesystem jail.  A multi-tenant
    deployment must add OS-level isolation (container, gVisor, seccomp).
    """
    import pathlib

    real_open = builtins.open
    root_path = pathlib.Path(root).resolve()

    def _open(file, mode="r", *args, **kwargs):  # noqa: ANN001, ANN002
        text = str(file)
        lowered = text.lower()
        for pattern in SENSITIVE_PATTERNS:
            if pattern in lowered:
                raise PermissionError(f"access to sensitive path is blocked: {file}")
        if any(ch in str(mode) for ch in ("w", "a", "x", "+")):
            target = pathlib.Path(file)
            resolved = (target if target.is_absolute() else pathlib.Path.cwd() / target).resolve()
            if root_path not in resolved.parents and resolved != root_path:
                raise PermissionError(f"writes outside the sandbox directory are blocked: {file}")
        return real_open(file, mode, *args, **kwargs)

    return _open


def install_pickle_guard() -> None:
    """Block deserialisation of untrusted data inside the isolated runner.

    ``pickle`` must stay importable (numpy, pandas and sklearn import it), so we
    disable the dangerous half: loading.
    """
    import pickle

    def _deny(*_args, **_kwargs):
        raise RuntimeError(
            "pickle.load/loads is disabled in the isolated runner: "
            "deserialising untrusted data is equivalent to running it"
        )

    pickle.loads = _deny  # type: ignore[assignment]
    pickle.load = _deny  # type: ignore[assignment]
    try:
        import pickletools
    except Exception:  # pragma: no cover
        return


def install_process_guard() -> None:
    """Disable process creation while keeping ``subprocess`` importable."""
    import os

    def _deny(*_args, **_kwargs):
        raise RuntimeError("starting new processes is disabled in the isolated runner")

    try:
        import subprocess

        for name in ("Popen", "run", "call", "check_call", "check_output", "getoutput", "getstatusoutput"):
            if hasattr(subprocess, name):
                setattr(subprocess, name, _deny)
    except Exception:  # pragma: no cover
        pass

    for name in ("system", "fork", "forkpty", "execv", "execve", "execvp", "execl", "execlp", "spawnv", "spawnve"):
        if hasattr(os, name):
            try:
                setattr(os, name, _deny)
            except (AttributeError, TypeError):  # pragma: no cover
                pass
    if hasattr(os, "posix_spawn"):
        os.posix_spawn = _deny  # type: ignore[assignment]


def install_native_loading_guard() -> None:
    """Disable loading *new* native libraries, with a library-code exemption.

    ``ctypes.CDLL`` is only callable at run time (never through the import
    machinery), so the caller's frame is reliable here: installed packages such
    as ``threadpoolctl`` legitimately inspect already-loaded BLAS libraries,
    while learner code must not be able to load arbitrary native code.
    """
    try:
        import ctypes
    except Exception:  # pragma: no cover
        return

    real_cdll = ctypes.CDLL
    real_load = ctypes.cdll.LoadLibrary if hasattr(ctypes, "cdll") else None

    def _caller_is_library() -> bool:
        frame = sys._getframe(1)
        for _ in range(8):
            if frame is None:
                break
            filename = frame.f_code.co_filename or ""
            if "pfn/runtime/guards.py" in filename:
                frame = frame.f_back
                continue
            return "site-packages" in filename or "dist-packages" in filename
        return False

    def _guarded_cdll(*args, **kwargs):
        if not _caller_is_library():
            raise RuntimeError("loading native libraries is disabled in the isolated runner")
        return real_cdll(*args, **kwargs)

    def _guarded_load(*args, **kwargs):
        if not _caller_is_library():
            raise RuntimeError("loading native libraries is disabled in the isolated runner")
        return real_load(*args, **kwargs)

    ctypes.CDLL = _guarded_cdll  # type: ignore[assignment]
    ctypes.OleDLL = _guarded_cdll  # type: ignore[assignment]
    ctypes.WinDLL = _guarded_cdll  # type: ignore[assignment]
    ctypes.PyDLL = _guarded_cdll  # type: ignore[assignment]
    if real_load is not None:
        ctypes.cdll.LoadLibrary = _guarded_load  # type: ignore[assignment]
