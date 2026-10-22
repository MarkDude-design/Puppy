"""Nonblocking adapter boundary for a future real QEMU implementation."""
from typing import Protocol


class BootBackend(Protocol):
    """All methods must return promptly; poll_ready performs no blocking read.

    The wrapper enforces a host-monotonic readiness deadline, but cannot interrupt
    arbitrary blocking Python code. A real adapter must own/terminate its process
    group in stop(), including when start() only partially succeeds.
    """

    def start(self) -> None: ...

    def poll_ready(self) -> bool: ...

    def stop(self) -> None: ...


class QemuBackend:
    """Explicit stub: this suite never launches a real emulator."""

    def start(self):
        raise NotImplementedError("QEMU adapter is deferred; use an injected mock backend")

    def poll_ready(self):
        raise NotImplementedError("QEMU adapter is deferred")

    def stop(self):
        # No process can have been created by this stub.
        pass
