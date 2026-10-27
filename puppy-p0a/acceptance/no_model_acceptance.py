#!/usr/bin/env python3
"""Standard-library acceptance primitives; no model, network or QEMU calls."""
import argparse
import hashlib
import hmac
import json
import math
from pathlib import Path
import re
import secrets
import stat
import sys
import time

from boot_backend import BootBackend


PAYLOAD_CAP = 100_000_000
LOG_VERSION = "puppf-state-log/1"
NONCE = re.compile(r"[A-Za-z0-9_-]{1,128}")
IDENTIFIER = re.compile(r"[A-Za-z0-9_.-]{1,64}")
TRANSITIONS = {
    None: {"CREATED"},
    "CREATED": {"BOOTING", "FAILED"},
    "BOOTING": {"READY", "TIMED_OUT", "FAILED"},
    "READY": {"STOPPED", "FAILED"},
    "STOPPED": set(), "TIMED_OUT": set(), "FAILED": set(),
}
TERMINAL = {"STOPPED", "TIMED_OUT", "FAILED"}


class AcceptanceError(ValueError):
    pass


class BootTimeout(AcceptanceError):
    pass


def _text(value, pattern, label):
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise AcceptanceError(f"invalid {label}")
    return value


def new_nonce():
    return secrets.token_hex(16)


def check_nonce(expected, received):
    _text(expected, NONCE, "expected nonce")
    _text(received, NONCE, "received nonce")
    if not hmac.compare_digest(expected, received):
        raise AcceptanceError("nonce mismatch")


def nonce_probe(nonce):
    """Input omits the full nonce, so a terminal command echo cannot prove output."""
    _text(nonce, NONCE, "nonce")
    if len(nonce) < 2:
        raise AcceptanceError("probe nonce must contain at least two characters")
    middle = len(nonce) // 2
    return f"printf '\\n%s%s\\n' '{nonce[:middle]}' '{nonce[middle:]}'\n"


def check_nonce_output(expected, output):
    _text(expected, NONCE, "expected nonce")
    if not isinstance(output, str) or not output.endswith("\n"):
        raise AcceptanceError("nonce output must contain complete newline-terminated lines")
    # Serial records end in LF or CRLF, not arbitrary Unicode/control separators.
    if sum(line.removesuffix("\r") == expected for line in output.split("\n")) != 1:
        raise AcceptanceError("expected exactly one separate nonce output line")
    return {"valid": True, "nonce_output_lines": 1}


def check_image_sizes(paths, cap_bytes=PAYLOAD_CAP):
    """Measure the combined payload, not ISO size or resident memory."""
    if type(cap_bytes) is not int or cap_bytes <= 0:
        raise AcceptanceError("image cap must be a positive integer byte count")
    paths = list(map(Path, paths))
    if not paths:
        raise AcceptanceError("no image artifacts supplied")
    total, identities, artifacts = 0, set(), []
    for path in paths:
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_size == 0:
            raise AcceptanceError("artifact must be a nonempty regular file: " + str(path))
        identity = (info.st_dev, info.st_ino)
        if identity in identities:
            raise AcceptanceError("duplicate image artifact: " + str(path))
        identities.add(identity)
        total += info.st_size
        artifacts.append({"path": str(path), "bytes": info.st_size})
    if total >= cap_bytes:
        raise AcceptanceError(f"combined payload {total} must be strictly below {cap_bytes} bytes")
    for artifact in artifacts:
        with Path(artifact["path"]).open("rb") as stream:
            artifact["sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"valid": True, "combined_payload_bytes": total,
            "cap_bytes": cap_bytes, "artifacts": artifacts}


def check_correlated_acks(requests, acknowledgements):
    """P0b mock contract, independent of MCP and of a successful P0a shell probe."""
    if not isinstance(requests, list) or not requests or not isinstance(acknowledgements, list):
        raise AcceptanceError("require a nonempty request list and an ACK list")
    expected, nonces = {}, set()
    for request in requests:
        if not isinstance(request, dict) or set(request) != {"request_id", "nonce"}:
            raise AcceptanceError("request fields must be request_id and nonce")
        identifier = _text(request["request_id"], IDENTIFIER, "request ID")
        nonce = _text(request["nonce"], NONCE, "request nonce")
        if identifier in expected or nonce in nonces:
            raise AcceptanceError("duplicate request ID or reused nonce")
        expected[identifier] = nonce
        nonces.add(nonce)
    seen = set()
    for ack in acknowledgements:
        if not isinstance(ack, dict) or set(ack) != {"type", "request_id", "nonce"} or ack["type"] != "ACK":
            raise AcceptanceError("ACK fields/type do not match the P0b mock contract")
        identifier = _text(ack["request_id"], IDENTIFIER, "ACK request ID")
        if identifier not in expected:
            raise AcceptanceError("unsolicited or stale ACK request ID")
        if identifier in seen:
            raise AcceptanceError("duplicate ACK")
        check_nonce(expected[identifier], ack["nonce"])
        seen.add(identifier)
    if seen != set(expected):
        raise AcceptanceError("missing ACK for request IDs: " + ",".join(sorted(set(expected) - seen)))
    return {"valid": True, "requests": len(expected), "acknowledgements": len(seen),
            "request_ids": sorted(seen)}


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise AcceptanceError("duplicate JSON key: " + key)
        value[key] = item
    return value


def read_json(text):
    def invalid_constant(value):
        raise AcceptanceError("non-finite JSON constant: " + value)
    return json.loads(text, object_pairs_hook=_object, parse_constant=invalid_constant)


def _event(record, previous=None):
    required = {"schema_version", "run_id", "seq", "monotonic_ns", "state"}
    if not isinstance(record, dict) or not required <= set(record) <= required | {"reason"}:
        raise AcceptanceError("invalid state-log fields")
    if record["schema_version"] != LOG_VERSION:
        raise AcceptanceError("unsupported state-log version")
    _text(record["run_id"], IDENTIFIER, "log run ID")
    if type(record["seq"]) is not int or record["seq"] != (previous["seq"] + 1 if previous else 1):
        raise AcceptanceError("state-log sequence must start at 1 and be contiguous")
    stamp = record["monotonic_ns"]
    if type(stamp) is not int or stamp < 0 or (previous and stamp < previous["monotonic_ns"]):
        raise AcceptanceError("invalid or backward state-log monotonic timestamp")
    if previous and record["run_id"] != previous["run_id"]:
        raise AcceptanceError("mixed state-log run IDs")
    before = previous["state"] if previous else None
    if not isinstance(record["state"], str) or record["state"] not in TRANSITIONS[before]:
        raise AcceptanceError("invalid state transition")
    if "reason" in record and (not isinstance(record["reason"], str) or not 1 <= len(record["reason"]) <= 512):
        raise AcceptanceError("reason must be a nonempty string of at most 512 characters")
    if record["state"] in {"FAILED", "TIMED_OUT"} and "reason" not in record:
        raise AcceptanceError("failure/timeout requires a reason")


class StateLog:
    """One writer, exclusive new file. Not a hash chain or a durable flight recorder."""

    def __init__(self, path, run_id, clock_ns=time.monotonic_ns):
        self.path = Path(path)
        self.run_id = _text(run_id, IDENTIFIER, "run ID")
        self.clock_ns = clock_ns
        self.previous = None
        # Refuse overwrite/resume: a different attempt needs a different log.
        with self.path.open("x", encoding="utf-8"):
            pass
        self.emit("CREATED")

    def emit(self, state, reason=None):
        record = {"schema_version": LOG_VERSION, "run_id": self.run_id,
                  "seq": self.previous["seq"] + 1 if self.previous else 1,
                  "monotonic_ns": self.clock_ns(), "state": state}
        if reason is not None:
            record["reason"] = reason
        _event(record, self.previous)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, separators=(",", ":"), allow_nan=False) + "\n")
        self.previous = record


def validate_state_log(path, require_success=False):
    previous, count = None, 0
    with Path(path).open(encoding="utf-8") as stream:
        for count, line in enumerate(stream, 1):
            if not line.endswith("\n"):
                raise AcceptanceError(f"truncated state-log line {count}")
            try:
                record = read_json(line)
                _event(record, previous)
            except (ValueError, TypeError) as exc:
                raise AcceptanceError(f"state-log line {count}: {exc}") from exc
            previous = record
    if previous is None or previous["state"] not in TERMINAL:
        raise AcceptanceError("state log is empty or incomplete")
    successful = previous["state"] == "STOPPED"
    if require_success and not successful:
        raise AcceptanceError("valid log records an unsuccessful boot")
    return {"valid": True, "schema_version": LOG_VERSION, "run_id": previous["run_id"],
            "events": count, "terminal_state": previous["state"], "successful": successful}


def boot_with_timeout(backend: BootBackend, timeout_s=90, poll_s=0.1,
                      clock=time.monotonic, sleep=time.sleep, log=None):
    """Readiness test with cleanup. Backend calls must be nonblocking by contract."""
    def duration(value, label, ceiling=None):
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value <= 0 or (ceiling and value > ceiling)):
            raise AcceptanceError("invalid " + label)
    duration(timeout_s, "boot timeout (maximum P0a value is 90 seconds)", 90)
    duration(poll_s, "poll interval")
    start = previous = clock()
    if isinstance(start, bool) or not isinstance(start, (int, float)) or not math.isfinite(start):
        raise AcceptanceError("invalid host monotonic clock")

    def elapsed():
        nonlocal previous
        now = clock()
        if (isinstance(now, bool) or not isinstance(now, (int, float))
                or not math.isfinite(now) or now < previous):
            raise AcceptanceError("invalid or backward host monotonic clock")
        previous = now
        return now - start

    error, ready_at = None, None
    try:
        if log:
            log.emit("BOOTING")
        backend.start()
        while True:
            if elapsed() > timeout_s:
                raise BootTimeout("boot readiness deadline exceeded")
            ready = backend.poll_ready()
            at = elapsed()
            if at > timeout_s:
                raise BootTimeout("backend returned after boot readiness deadline")
            if type(ready) is not bool:
                raise AcceptanceError("backend readiness must be boolean")
            if ready:
                ready_at = at
                if log:
                    log.emit("READY")
                break
            if at >= timeout_s:
                raise BootTimeout("boot readiness deadline exceeded")
            sleep(min(poll_s, timeout_s - at))
    except BaseException as exc:
        error = exc
    finally:
        try:
            backend.stop()
        except Exception as cleanup:
            if error is None:
                error = AcceptanceError("backend cleanup failed: " + type(cleanup).__name__)
            else:
                error.add_note("Backend cleanup also failed: " + type(cleanup).__name__)
    if error:
        if log:
            state = "TIMED_OUT" if isinstance(error, BootTimeout) else "FAILED"
            try:
                log.emit(state, (type(error).__name__ + ": " + str(error))[:512])
            except Exception as logging_error:
                error.add_note("State-log write failed: " + type(logging_error).__name__)
        if isinstance(error, (AcceptanceError, KeyboardInterrupt, SystemExit)):
            raise error
        raise AcceptanceError("backend failed: " + type(error).__name__) from error
    if log:
        log.emit("STOPPED")
    return {"ready": True, "ready_at_s": ready_at, "timeout_s": timeout_s,
            "backend_stopped": True, "proves_full_p0a_acceptance": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("new-nonce")
    nonce = sub.add_parser("nonce")
    nonce.add_argument("expected")
    nonce.add_argument("output", type=Path)
    images = sub.add_parser("size")
    images.add_argument("artifacts", type=Path, nargs="+")
    log = sub.add_parser("log")
    log.add_argument("path", type=Path)
    log.add_argument("--require-success", action="store_true")
    acks = sub.add_parser("acks")
    acks.add_argument("requests", type=Path)
    acks.add_argument("acknowledgements", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "new-nonce":
            result = {"nonce": new_nonce()}
        elif args.command == "nonce":
            result = check_nonce_output(args.expected, args.output.read_text())
        elif args.command == "size":
            result = check_image_sizes(args.artifacts)
        elif args.command == "log":
            result = validate_state_log(args.path, args.require_success)
        else:
            result = check_correlated_acks(read_json(args.requests.read_text()),
                                           read_json(args.acknowledgements.read_text()))
        print(json.dumps(result, sort_keys=True))
        return 0
    except (AcceptanceError, OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
