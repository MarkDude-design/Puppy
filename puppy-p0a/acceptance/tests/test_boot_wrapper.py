from unittest.mock import Mock

import pytest

from boot_backend import QemuBackend
from no_model_acceptance import AcceptanceError, BootTimeout, StateLog, boot_with_timeout, validate_state_log


class Clock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, duration):
        self.sleeps.append(duration)
        self.now += duration

    def ns(self):
        return round(self.now * 1_000_000_000)


def run(backend, clock, **kwargs):
    return boot_with_timeout(backend, clock=clock, sleep=clock.sleep, **kwargs)


def test_boot_ready_and_cleanup_log(tmp_path):
    clock = Clock()
    backend = Mock()
    backend.poll_ready.side_effect = [False, False, True]
    log = StateLog(tmp_path / "state.jsonl", "mock-boot", clock.ns)
    result = run(backend, clock, timeout_s=1, poll_s=0.25, log=log)
    assert result["ready_at_s"] == 0.5
    assert result["proves_full_p0a_acceptance"] is False
    backend.start.assert_called_once_with()
    backend.stop.assert_called_once_with()
    assert validate_state_log(log.path, require_success=True)["events"] == 4


def test_timeout_is_monotonic_and_stops_backend(tmp_path):
    clock, backend = Clock(), Mock()
    backend.poll_ready.return_value = False
    log = StateLog(tmp_path / "timeout.jsonl", "mock-timeout", clock.ns)
    with pytest.raises(BootTimeout):
        run(backend, clock, timeout_s=1, poll_s=0.3, log=log)
    assert clock.now == 1
    assert clock.sleeps[-1] == pytest.approx(0.1)
    backend.stop.assert_called_once_with()
    assert validate_state_log(log.path)["terminal_state"] == "TIMED_OUT"


def test_exact_deadline_is_allowed_but_late_result_is_not():
    for ready_at, should_pass in [(90, True), (90.001, False)]:
        clock, backend = Clock(), Mock()
        def poll():
            clock.now = ready_at
            return True
        backend.poll_ready.side_effect = poll
        if should_pass:
            assert run(backend, clock)["ready_at_s"] == 90
        else:
            with pytest.raises(BootTimeout):
                run(backend, clock)
        backend.stop.assert_called_once_with()


@pytest.mark.parametrize("stage", ["start", "poll_ready", "stop"])
def test_backend_errors_are_failures_and_cleanup_is_attempted(tmp_path, stage):
    clock, backend = Clock(), Mock()
    backend.poll_ready.return_value = True
    getattr(backend, stage).side_effect = RuntimeError("mock failure")
    log = StateLog(tmp_path / "failed.jsonl", "mock-failure", clock.ns)
    with pytest.raises(AcceptanceError):
        run(backend, clock, log=log)
    backend.stop.assert_called_once_with()
    assert validate_state_log(log.path)["terminal_state"] == "FAILED"


def test_cleanup_error_does_not_hide_timeout():
    clock, backend = Clock(), Mock()
    backend.poll_ready.return_value = False
    backend.stop.side_effect = RuntimeError("mock cleanup")
    with pytest.raises(BootTimeout) as error:
        run(backend, clock, timeout_s=0.1)
    assert "cleanup" in error.value.__notes__[0]


@pytest.mark.parametrize("timeout", [0, -1, 91, True, float("nan"), float("inf")])
def test_invalid_timeout_never_starts_backend(timeout):
    backend = Mock()
    with pytest.raises(AcceptanceError):
        run(backend, Clock(), timeout_s=timeout)
    backend.start.assert_not_called()


def test_bad_readiness_is_not_truthy_success():
    backend = Mock()
    backend.poll_ready.return_value = "ready"
    with pytest.raises(AcceptanceError, match="boolean"):
        run(backend, Clock())
    backend.stop.assert_called_once_with()


def test_clock_cannot_move_backwards():
    clock, backend = Clock(), Mock()
    backend.start.side_effect = lambda: setattr(clock, "now", -1)
    with pytest.raises(AcceptanceError, match="backward"):
        run(backend, clock)
    backend.stop.assert_called_once_with()


def test_qemu_is_an_unimplemented_interface_not_a_subprocess():
    with pytest.raises(AcceptanceError, match="NotImplementedError"):
        run(QemuBackend(), Clock())
