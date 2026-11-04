# Serial harness audit — November 3, 2026 (Pacific)

SEAT: Meraki | VIA: ChatGPT Work execution tools | KIND: local test development.

Mark requested useful Puppy work while fresh hosted-build dispatch was blocked.
This pass adds nine local process integration tests to the existing serial
harness. It found a coverage gap; it did not reproduce a production harness
defect or establish a guest configuration failure. No production-code fix is
claimed.

## Source and scope

Base: merged PR #19, commit `e0b5e0e4b206c30ca3bcbfcf08c764a2acf19808`.
Before editing, all 108 cached repository blobs matched their GitHub Git-blob
SHA1s at that commit. The tree contains no AGENTS.md or CONTRIBUTING.md.
The guest `/init` is executable in the repository (`100755`). Static inspection
covered the Buildroot/kernel/BusyBox configs, init script, CPIO assembly,
serial reader, acceptance checker and existing test coverage. This is not
resolution of the kernel/BusyBox configs or inspection of a compiled image.

The frozen packet remains byte-identical, SHA256
`b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b`.
Production code, guest configuration, source pins and workflow triggers are
unchanged. This work does not dispatch the still-pending hosted build.

## What the new tests exercise

`puppy-p0a/tests/test_serial_process.py` launches a local Python fixture child
with real OS stdin/stdout pipes. A separate control pipe releases one fragment
at a time; a scripted monotonic clock drives deadlines without long sleeps.
The token probe runs an actual local `/bin/sh` printf. That is host execution,
not execution in a guest. The production selector loop, line parser, checker,
receipt writing and process-group cleanup execute against those fixtures.

The nine cases cover fragmented prompt/token success, echo-only rejection,
missing prompt, prompt crossing the deadline, serial-reader exception, process
exit after valid output, duplicate HELLO during the grace interval, an
unterminated panic record and watchdog termination. Every case checks that its
fixture child is reaped and that its pipe handles are closed.

The harness retains its normal result field names inside temporary fixture
directories. Even a fixture result carrying the harness's existing
`actual_qemu_serial_observation` label is synthetic: its launcher was replaced
with the Python fixture. Those temporary observations are not published as boot
evidence; the test report is the receipt for this pass.

## Validation

Full suite: **191 passed** (182 existing + 9 new), Python 3.12.14.
The first pytest invocation found no pytest in the active interpreter's default
path. The successful run used a preexisting local pytest distribution through
PYTHONPATH, with plugin autoload disabled. No package was downloaded/installed.
See `validation.json` for the exact command, environment note, UTC timestamp,
exit code and captured output. `sh -n` on guest init and `bash -n` on the runner
script also exited zero.

No kernel or BusyBox compilation, QEMU execution, real guest timing measurement,
hosted dispatch, merge or boot acceptance occurred. The next runtime evidence
still comes from the authorized fresh main/build workflow.
