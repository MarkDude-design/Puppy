#!/usr/bin/env python3
"""Single-process host-file mock. No network, model calls or security boundary."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import stat


class Rejected(RuntimeError):
    pass


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Rejected("duplicate JSON field")
        result[key] = value
    return result


def validate(wire):
    if not isinstance(wire, bytes) or not 1 <= len(wire) <= 256:
        raise Rejected("wire must be 1..256 bytes, including newline")
    if not wire.endswith(b"\n") or b"\n" in wire[:-1] or b"\r" in wire:
        raise Rejected("wire must have exactly one terminating LF")
    try:
        value = json.loads(wire.decode("utf-8"), object_pairs_hook=unique_pairs)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Rejected("invalid UTF-8 JSON") from exc
    if not isinstance(value, dict) or set(value) != {"v", "round", "kind", "text"}:
        raise Rejected("schema fields differ")
    if type(value["v"]) is not int or value["v"] != 0:
        raise Rejected("v must be integer zero")
    if type(value["round"]) is not int or not 1 <= value["round"] <= 6:
        raise Rejected("round must be integer 1..6")
    if value["kind"] != "MESSAGE" or not isinstance(value["text"], str):
        raise Rejected("kind/text type differs")
    if "\n" in value["text"] or "\r" in value["text"]:
        raise Rejected("embedded text newline")
    try:
        canonical(value)
    except UnicodeError as exc:
        raise Rejected("invalid Unicode scalar") from exc
    return value


def message(round_number, text):
    wire = canonical({"v": 0, "round": round_number, "kind": "MESSAGE", "text": text})
    validate(wire)
    return wire


def write_all(fd, content):
    view = memoryview(content)
    while view:
        count = os.write(fd, view)
        if count <= 0:
            raise OSError("short write")
        view = view[count:]


def exclusive_file(path, content):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        os.fchmod(fd, 0o600)
        write_all(fd, content)
        os.fsync(fd)
    finally:
        os.close(fd)


def check_regular(fd):
    info = os.fstat(fd)
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
            or stat.S_IMODE(info.st_mode) != 0o600 or info.st_uid != os.geteuid()):
        raise Rejected("file must be owned 0600 regular file with one link")
    return info


class Relay:
    directions = ("a_to_b", "b_to_a")

    def __init__(self, root):
        self.root = Path(root)
        self.turn = 0
        self.pending = None
        self.halted = False
        self.transcript_bytes = 0
        old_umask = os.umask(0o077)
        try:
            self.root.mkdir(mode=0o700)  # Existing roots, including symlinks, are refused.
            os.chmod(self.root, 0o700)
            for direction in self.directions:
                (self.root / direction).mkdir(mode=0o700)
                os.chmod(self.root / direction, 0o700)
            self.transcript = self.root / "transcript.log"
            exclusive_file(self.transcript, b"")
            info = self.transcript.stat()
            self.transcript_identity = (info.st_dev, info.st_ino)
            self.directory_identities = {}
            for path in [self.root] + [self.root / d for d in self.directions]:
                info = path.lstat()
                self.directory_identities[path] = (info.st_dev, info.st_ino)
        finally:
            os.umask(old_umask)

    def _directories(self):
        for path, identity in self.directory_identities.items():
            info = path.lstat()
            if (not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o700
                    or (info.st_dev, info.st_ino) != identity or info.st_uid != os.geteuid()):
                raise Rejected("spool/root directory changed")

    def _check(self):
        self._directories()
        if self.halted or os.path.lexists(self.root / "STOP"):
            raise Rejected("STOP present or relay halted")

    def _expected(self):
        if self.turn >= 12:
            raise Rejected("six-round maximum reached")
        return self.directions[self.turn % 2], self.turn // 2 + 1

    def send(self, direction, wire):
        self._check()
        value = validate(wire)
        expected_direction, expected_round = self._expected()
        if direction != expected_direction or value["round"] != expected_round or self.pending:
            raise Rejected("wrong direction/round or pending message")
        # Leftovers in either spool stop the exchange; never overwrite or silently drain.
        if any(any((self.root / d).iterdir()) for d in self.directions):
            raise Rejected("leftover/stalled spool")
        path = self.root / direction / (str(expected_round) + ".json")
        self._check()
        exclusive_file(path, wire)
        self.pending = (direction, expected_round, path)

    def _append(self, record):
        self._check()
        fd = os.open(self.transcript, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW)
        try:
            info = check_regular(fd)
            if ((info.st_dev, info.st_ino) != self.transcript_identity
                    or info.st_size != self.transcript_bytes):
                raise Rejected("transcript replaced or changed")
            write_all(fd, record)
            os.fsync(fd)
            self.transcript_bytes += len(record)
        finally:
            os.close(fd)

    def receive(self, direction):
        self._check()
        if self.pending is None or self.pending[0] != direction:
            raise Rejected("no pending message for direction")
        _, expected_round, path = self.pending
        if sorted((self.root / direction).iterdir()) != [path]:
            raise Rejected("unexpected spool contents")
        other = self.directions[1 - self.directions.index(direction)]
        if any((self.root / other).iterdir()):
            raise Rejected("leftover opposite spool")
        # NONBLOCK prevents a substituted FIFO from hanging this mock.
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            info = check_regular(fd)
            wire = os.read(fd, 257)
        finally:
            os.close(fd)
        value = validate(wire)
        if value["round"] != expected_round:
            raise Rejected("spooled round differs")
        self._append(canonical({"direction": direction, "message": value}))
        # A failed unlink leaves a blocked relay; no retry can append a duplicate.
        self.halted = True
        if (path.lstat().st_dev, path.lstat().st_ino) != (info.st_dev, info.st_ino):
            raise Rejected("spooled file replaced during read")
        path.unlink()
        self.turn += 1
        self.pending = None
        self.halted = False
        if self.turn == 12:
            self.stop()
        return value

    def stop(self):
        self._directories()
        if not os.path.lexists(self.root / "STOP"):
            exclusive_file(self.root / "STOP", b"STOP\n")
        self.halted = True


def run_mock(root, seed=41):
    relay = Relay(root)
    rng = random.Random(seed)
    for round_number in range(1, 7):
        text = "A:" + format(rng.getrandbits(32), "08x")
        relay.send("a_to_b", message(round_number, text))
        received = relay.receive("a_to_b")
        relay.send("b_to_a", message(round_number, "B:" + received["text"][::-1]))
        relay.receive("b_to_a")
    transcript = relay.transcript.read_bytes()
    return {"status": "PASS", "seed": seed, "rounds": 6, "messages": relay.turn,
            "transcript_bytes": len(transcript),
            "transcript_sha256": hashlib.sha256(transcript).hexdigest(),
            "stop_present": (relay.root / "STOP").is_file(),
            "evidence_kind": "deterministic_host_mock", "guest_boot_proved": False,
            "model_calls": 0, "network_calls": 0, "security_containment_proved": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True, help="Fresh root; parent must exist")
    parser.add_argument("--seed", type=int, default=41)
    args = parser.parse_args(argv)
    try:
        result = run_mock(args.run_dir, args.seed)
        exclusive_file(args.run_dir / "result.json", canonical(result))
        print(json.dumps(result, sort_keys=True))
        return 0
    except (Rejected, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
