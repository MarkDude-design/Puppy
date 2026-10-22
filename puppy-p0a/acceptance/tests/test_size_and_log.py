import hashlib
import json

import pytest

from no_model_acceptance import (
    AcceptanceError, LOG_VERSION, StateLog, check_image_sizes, validate_state_log,
)


def test_combined_image_measurements(tmp_path):
    kernel, initrd = tmp_path / "kernel", tmp_path / "initramfs"
    kernel.write_bytes(b"mock-kernel")
    initrd.write_bytes(b"mock-initramfs")
    result = check_image_sizes([kernel, initrd])
    assert result["cap_bytes"] == 100_000_000
    assert result["combined_payload_bytes"] == len(b"mock-kernelmock-initramfs")
    assert result["artifacts"][0]["sha256"] == hashlib.sha256(b"mock-kernel").hexdigest()


@pytest.mark.parametrize("size", [100, 101])
def test_cap_is_strict_combined_not_per_file(tmp_path, size):
    first, second = tmp_path / "first", tmp_path / "second"
    first.write_bytes(b"x" * 60)
    second.write_bytes(b"x" * (size - 60))
    with pytest.raises(AcceptanceError, match="strictly below"):
        check_image_sizes([first, second], cap_bytes=100)


def test_default_cap_rejects_exactly_100_megabytes(tmp_path):
    # Sparse file: exercise the real default boundary without allocating/reading 100 MB.
    artifact = tmp_path / "sparse"
    with artifact.open("wb") as stream:
        stream.truncate(100_000_000)
    with pytest.raises(AcceptanceError, match="strictly below 100000000"):
        check_image_sizes([artifact])


@pytest.mark.parametrize("cap", [0, -1, True, 100.0])
def test_bad_cap(tmp_path, cap):
    with pytest.raises(AcceptanceError):
        check_image_sizes([], cap)


def test_empty_missing_directory_or_duplicate_artifacts(tmp_path):
    artifact = tmp_path / "artifact"
    artifact.write_bytes(b"x")
    alias = tmp_path / "alias"
    alias.symlink_to(artifact)
    for paths in [[], [tmp_path], [artifact, alias]]:
        with pytest.raises(AcceptanceError):
            check_image_sizes(paths)
    with pytest.raises(FileNotFoundError):
        check_image_sizes([tmp_path / "missing"])
    artifact.write_bytes(b"")
    with pytest.raises(AcceptanceError):
        check_image_sizes([artifact])


def log_records(terminal="STOPPED"):
    states = ["CREATED", "BOOTING", "READY", terminal] if terminal == "STOPPED" else ["CREATED", "BOOTING", terminal]
    records = []
    for seq, state in enumerate(states, 1):
        record = {"schema_version": LOG_VERSION, "run_id": "mock-1", "seq": seq,
                  "monotonic_ns": seq * 1_000_000, "state": state}
        if state in {"FAILED", "TIMED_OUT"}:
            record["reason"] = "mock failure"
        records.append(record)
    return records


def write_records(path, records):
    path.write_text("".join(json.dumps(record) + "\n" for record in records))


def test_writer_and_validator(tmp_path):
    path = tmp_path / "state.jsonl"
    times = iter([0, 0, 1, 2])
    log = StateLog(path, "mock-1", clock_ns=lambda: next(times))
    for state in ["BOOTING", "READY", "STOPPED"]:
        log.emit(state)
    result = validate_state_log(path, require_success=True)
    assert result == {"valid": True, "schema_version": LOG_VERSION, "run_id": "mock-1",
                      "events": 4, "terminal_state": "STOPPED", "successful": True}
    with pytest.raises(FileExistsError):
        StateLog(path, "new-attempt")


@pytest.mark.parametrize("terminal", ["FAILED", "TIMED_OUT"])
def test_valid_failure_log_does_not_mean_success(tmp_path, terminal):
    path = tmp_path / "failed.jsonl"
    write_records(path, log_records(terminal))
    assert validate_state_log(path)["successful"] is False
    with pytest.raises(AcceptanceError, match="unsuccessful"):
        validate_state_log(path, require_success=True)


@pytest.mark.parametrize("problem", [
    "version", "run-id", "seq-start", "seq-gap", "seq-bool", "clock-backward",
    "clock-negative", "clock-float", "clock-bool", "skipped-boot", "unknown-state",
    "extra-field", "after-terminal", "missing-terminal", "missing-reason", "long-reason",
])
def test_invalid_state_logs(tmp_path, problem):
    records = log_records()
    if problem == "version": records[0]["schema_version"] = "future"
    elif problem == "run-id": records[1]["run_id"] = "other-run"
    elif problem == "seq-start": records[0]["seq"] = 0
    elif problem == "seq-gap": records[1]["seq"] = 3
    elif problem == "seq-bool": records[0]["seq"] = True
    elif problem == "clock-backward": records[2]["monotonic_ns"] = 0
    elif problem == "clock-negative": records[0]["monotonic_ns"] = -1
    elif problem == "clock-float": records[0]["monotonic_ns"] = 1.5
    elif problem == "clock-bool": records[0]["monotonic_ns"] = True
    elif problem == "skipped-boot": records[1]["state"] = "READY"
    elif problem == "unknown-state": records[1]["state"] = "ACKED"
    elif problem == "extra-field": records[1]["model_said_ok"] = True
    elif problem == "after-terminal": records.append({**records[-1], "seq": 5})
    elif problem == "missing-terminal": records.pop()
    elif problem == "missing-reason": records = log_records("FAILED"); records[-1].pop("reason")
    elif problem == "long-reason": records = log_records("FAILED"); records[-1]["reason"] = "x" * 513
    path = tmp_path / "invalid.jsonl"
    write_records(path, records)
    with pytest.raises(AcceptanceError):
        validate_state_log(path)


@pytest.mark.parametrize("text", ["", "\n", "not JSON\n", "{}", "NaN\n", '{"state":"CREATED","state":"STOPPED"}\n'])
def test_truncated_malformed_and_duplicate_json(tmp_path, text):
    path = tmp_path / "bad.jsonl"
    path.write_text(text)
    with pytest.raises(AcceptanceError):
        validate_state_log(path)


def test_writer_does_not_append_invalid_transition(tmp_path):
    path = tmp_path / "state.jsonl"
    log = StateLog(path, "mock-1")
    before = path.read_bytes()
    with pytest.raises(AcceptanceError):
        log.emit("STOPPED")
    assert path.read_bytes() == before
