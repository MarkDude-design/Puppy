# No-model acceptance scripts and mock tests

This suite adds host-side nonce, readiness-deadline, payload-size, state-log and
P0b ACK checks. Runtime code uses Python 3.11+ standard library only. Pytest is a
test dependency. No module calls a model API, downloads a build, or runs QEMU.

The existing Buildroot/CI implementation and frozen P0a packet remain unchanged.
This suite neither selects a Puppy/Fedora base nor claims that a Linux guest
boots. P0b correlation checks here are a **minimal version-1 mock contract** for
future integration, not a change to P0a's shell proof or a guest/MCP wire protocol.

## Run the tests

From the repository root, create a test environment outside the checkout:

```sh
python3 -m venv /tmp/puppf-acceptance-venv
/tmp/puppf-acceptance-venv/bin/python -m pip install -r puppy-p0a/acceptance/requirements-test.txt
/tmp/puppf-acceptance-venv/bin/python -B -m pytest -p no:cacheprovider puppy-p0a/acceptance/tests puppy-p0a/tests -q
```

The second test directory reuses the existing HELLO timing/serial checker
fixtures. QEMU-launch failure is mocked in those tests. Passing tests validate
scripts against synthetic inputs; they do not pass hosted build acceptance.

## Command-line checks

All validation commands emit JSON and return 0 for a valid input or 1 for a failed
check, missing file, malformed JSON or invalid format. Argument-usage errors
return argparse's exit 2. These commands only read the supplied files.

```sh
python3 puppy-p0a/acceptance/no_model_acceptance.py new-nonce
python3 puppy-p0a/acceptance/no_model_acceptance.py nonce EXPECTED_NONCE serial.log
python3 puppy-p0a/acceptance/no_model_acceptance.py size bzImage rootfs.cpio.gz
python3 puppy-p0a/acceptance/no_model_acceptance.py log state.jsonl
python3 puppy-p0a/acceptance/no_model_acceptance.py log state.jsonl --require-success
python3 puppy-p0a/acceptance/no_model_acceptance.py acks requests.json acks.json
```

### Nonce and output

`new_nonce()` generates 128 random bits as 32 hex characters. Nonces supplied by
adapters are opaque ASCII tokens (`A–Z a–z 0–9 _ -`, 1–128 characters). This
syntax limit does not attest entropy; use the fresh generator for real probes.

`check_nonce()` checks exact equality. `check_nonce_output()` requires exactly
one complete LF/CRLF-delimited output line equal to the expected nonce. Prefixes,
whitespace, duplicates, partial lines and command echo do not count. Use
`nonce_probe()` when constructing a shell probe: it splits the nonce between two
`printf` arguments, so the full expected value is absent from command input.
The caller must capture actual output, not synthesize an output file. This is
shell receipt evidence, not a P0b ACK.

### Payload cap

`check_image_sizes()` checks nonempty regular files, rejects duplicate files or
aliases, records individual byte sizes and SHA-256s, and requires their **sum
strictly below 100,000,000 bytes**. Equality fails. It measures supplied payload
files, not a complete ISO, minimum RAM, resident memory or executable validity.
Supply finalized artifacts; the size/hash read is not a filesystem snapshot.

### Boot timeout and adapter boundary

`boot_backend.py` defines `BootBackend.start()`, `poll_ready() -> bool`, and
`stop()`. All methods must be nonblocking. `boot_with_timeout()` uses a
host-monotonic clock, a maximum 90-second readiness deadline and bounded polling.
It rejects late readiness, nonboolean responses, backward clocks and backend
exceptions. It always attempts cleanup, including partial startup and timeout.
Cleanup failure cannot turn a failed boot into success.

The returned result explicitly says it is not full P0a acceptance. Readiness
alone does not prove shell nonce output or HELLO timing. This wrapper ends the
backend session after its readiness check; an eventual full-run adapter needs a
separately reviewed lifecycle if it must continue collecting guest output.

`QemuBackend` is an explicit `NotImplementedError` stub. A future adapter must
provide real nonblocking process/serial handling and process-group termination.
This polling wrapper cannot forcibly interrupt an arbitrary blocking callback;
it detects a late return and rejects it. The pytest clock/sleep/backend fixtures
are deterministic and do not wait for real deadlines or start an emulator.

### State-change JSONL format: `puppf-state-log/1`

Example successful **mock readiness** lifecycle:

```jsonl
{"schema_version":"puppf-state-log/1","run_id":"mock-1","seq":1,"monotonic_ns":0,"state":"CREATED"}
{"schema_version":"puppf-state-log/1","run_id":"mock-1","seq":2,"monotonic_ns":1,"state":"BOOTING"}
{"schema_version":"puppf-state-log/1","run_id":"mock-1","seq":3,"monotonic_ns":2,"state":"READY"}
{"schema_version":"puppf-state-log/1","run_id":"mock-1","seq":4,"monotonic_ns":3,"state":"STOPPED"}
```

Required fields are exactly `schema_version`, `run_id`, `seq`, `monotonic_ns`,
and `state`, plus optional `reason`. Run IDs are 1–64 ASCII letters, digits,
underscore, dot or hyphen. Sequence starts at 1 and increases by exactly one.
Timestamps are nonnegative integer host-monotonic nanoseconds and never decrease;
equal readings are allowed. They are not UTC or comparable across separate runs.

Transitions:

| From | Allowed next state |
| --- | --- |
| Start | CREATED |
| CREATED | BOOTING, FAILED |
| BOOTING | READY, TIMED_OUT, FAILED |
| READY | STOPPED, FAILED |
| STOPPED, TIMED_OUT, FAILED | None |

FAILED/TIMED_OUT require a 1–512 character reason. The validator rejects mixed
run IDs, version/field drift, sequence gaps, invalid transitions, trailing records
after termination, duplicate JSON keys, non-finite numbers and truncated lines.
An empty or unterminated run is invalid. `StateLog` is a single-writer helper that
creates a new file exclusively; it refuses to overwrite an earlier attempt.

A well-formed timeout/failure log is **valid data about a failed run**. Normal
`log` validation therefore returns `valid: true, successful: false` for it;
`--require-success` rejects that outcome. STOPPED only describes this readiness
lifecycle, not acceptance of an OS build. This is not a forensic flight recorder,
hash chain, containment mechanism or migration of existing CI serial-event logs.

### Correlated ACK contract for P0b mock tests

Request batch (`requests.json`):

```json
[{"request_id":"r1","nonce":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
 {"request_id":"r2","nonce":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}]
```

ACK batch (`acks.json`):

```json
[{"type":"ACK","request_id":"r2","nonce":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
 {"type":"ACK","request_id":"r1","nonce":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}]
```

Every request must get exactly one ACK matching **both request ID and nonce**.
Order is immaterial. Missing, duplicate, unsolicited/stale IDs, wrong nonces,
crossed correlations, extra fields and unconditional ACK text fail. Empty batches
cannot pass. Request IDs and nonces cannot be reused within a batch. Fresh host
nonces are needed to prevent replay between batches; there is no persistent
anti-replay database. Request IDs use the same lexical rules as log run IDs.

This schema is local mock-test vocabulary. It does not import the networked
Castle/MCP HELLO/ACK schema or authorize a P0b guest implementation. No new packet
hash, real guest nonce input or QEMU transport is asserted by these tests.
