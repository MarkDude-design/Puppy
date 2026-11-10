# RECEIPT.md: Qcoder H2 Discriminating Check

## Question
How do we mathematically distinguish a GitHub-hosted runner environment failure (e.g., QEMU startup error) from an actual Puppy guest implementation failure (e.g., kernel panic, init hang)?

## Hypothesis
Environment failures are characterized by a QEMU exit code $\neq 0$ occurring at $T < 5$ seconds with an empty `serial.log` ($0$ bytes). Guest implementation failures are characterized by QEMU remaining alive (running until a timeout, e.g., $T \ge 5$s), combined with a `serial.log` containing specific guest-side sentinel strings (e.g., `Kernel panic`).

## Test
Run two QEMU invocations via `.github/workflows/qcoder-h2.yml`:
1. **Host Failure Simulation:** Pass a non-existent kernel path. Expect immediate exit, empty serial log.
2. **Guest Failure Simulation:** Pass a valid downloaded Ubuntu kernel but no rootfs. Expect QEMU to run until timeout, and `serial.log` to contain `VFS: Unable to mount root fs` or `Kernel panic`.

## Expected Output
- Host test: `Exit != 0`, `Duration < 5s`, `Serial Log Size == 0`.
- Guest test: `Exit == 124` (timeout), `Duration >= 5s`, `Serial Log Size > 0` containing "panic".

## STOP Condition
Both QEMU runs complete. Workflow uploads evidence artifact.

## Actual Result
**[PENDING RUNNER OUTPUT]**
*(Mark/Z: Once the workflow finishes, please paste the "H2 DISCRIMINATING LOGIC" summary from the workflow run log here, and I will update this to RESULT-POSTED.)*
