#!/bin/bash
# Z-completion 2026-11-10 — Q 3.8 MAX original preserved in the verbatim bank
# commit; wiring fixes per sandbox/reviews/Z-REVIEW-qmax-h2-2026-11-10.md:
#   Z1. Skip path (test-kernel download failed) now prints SKIPPED, distinct
#       from FAIL, and no longer reports a test that never ran as failed.
#   Z2. A failed discrimination now exits nonzero — a failed discriminator
#       must not render a green checkmark. Red run = data.
#   Z3. The H2 summary is spliced into RECEIPT.md by the runner itself, so the
#       RESULT-POSTED transition lands on-branch without a human paste.
#   Z4. Behavior note (unchanged by design): panic=1 with no -no-reboot makes
#       the guest panic, reset, and panic again until the timeout — this loop
#       is what produces exit 124 + populated serial log. Do not "fix" it.
set -e
EVIDENCE_DIR="${PUPPF_EVIDENCE_DIR:-./evidence}"
RECEIPT_FILE="${PUPPF_RECEIPT_FILE:-./sandbox/qmax-lab-20261110/RECEIPT.md}"
mkdir -p "$EVIDENCE_DIR"

TIMEOUT=15
PANIC_STRING="Kernel panic"

echo "=== Qcoder H2 Test: Host vs Guest Failure Discrimination ==="

# --- TEST 1: Host Environment Failure ---
echo "[TEST 1] Simulating Host Failure (invalid kernel path)..."
HOST_LOG="$EVIDENCE_DIR/host_serial.log"
HOST_START=$(date +%s)

set +e
qemu-system-x86_64 -nographic -kernel /nonexistent/kernel.img -serial file:"$HOST_LOG" > "$EVIDENCE_DIR/host_stdout.log" 2>&1
HOST_EXIT=$?
set -e
HOST_END=$(date +%s)
HOST_DURATION=$((HOST_END - HOST_START))
HOST_LOG_SIZE=$(stat -c%s "$HOST_LOG" 2>/dev/null || echo 0)

echo "Host Test Result: Exit=$HOST_EXIT, Duration=${HOST_DURATION}s, SerialLogSize=$HOST_LOG_SIZE"

# --- TEST 2: Guest Implementation Failure ---
echo "[TEST 2] Simulating Guest Failure (Kernel Panic via no initrd)..."
GUEST_LOG="$EVIDENCE_DIR/guest_serial.log"
GUEST_START=$(date +%s)

wget -q -O "$EVIDENCE_DIR/vmlinuz" "https://archive.ubuntu.com/ubuntu/dists/jammy-updates/main/installer-amd64/current/legacy-images/netboot/ubuntu-installer/amd64/linux" || {
    echo "Failed to download test kernel. Marking Guest test as SKIPPED."
    GUEST_EXIT=125
}

GUEST_OK=0
if [ -f "$EVIDENCE_DIR/vmlinuz" ]; then
    timeout $TIMEOUT qemu-system-x86_64 -nographic -kernel "$EVIDENCE_DIR/vmlinuz" -append "console=ttyS0 panic=1" -serial file:"$GUEST_LOG" > "$EVIDENCE_DIR/guest_stdout.log" 2>&1
    GUEST_EXIT=$?
    GUEST_END=$(date +%s)
    GUEST_DURATION=$((GUEST_END - GUEST_START))
    GUEST_LOG_SIZE=$(stat -c%s "$GUEST_LOG" 2>/dev/null || echo 0)

    echo "Guest Test Result: Exit=$GUEST_EXIT, Duration=${GUEST_DURATION}s, SerialLogSize=$GUEST_LOG_SIZE"
    echo "Guest Serial Log Tail:"
    tail -n 5 "$GUEST_LOG" || true

    if grep -q "$PANIC_STRING" "$GUEST_LOG"; then
        echo "DISCRIMINATING CHECKPOINT: Guest panic string found in serial log."
        GUEST_OK=1
    fi
fi

echo "=== H2 DISCRIMINATING LOGIC ===" | tee "$EVIDENCE_DIR/h2-summary.log"
OVERALL=0
if [ "$HOST_EXIT" -ne 0 ] && [ "$HOST_DURATION" -lt 5 ] && [ "$HOST_LOG_SIZE" -eq 0 ]; then
    echo "PASS: Host failure correctly identified by early exit and empty serial log." | tee -a "$EVIDENCE_DIR/h2-summary.log"
else
    echo "FAIL: Host failure pattern unexpected." | tee -a "$EVIDENCE_DIR/h2-summary.log"
    OVERALL=1
fi

if [ "$GUEST_OK" -eq 1 ] && [ "${GUEST_DURATION:-0}" -ge 5 ] && grep -q "$PANIC_STRING" "$GUEST_LOG"; then
    echo "PASS: Guest failure correctly identified by sustained runtime and panic string in serial log." | tee -a "$EVIDENCE_DIR/h2-summary.log"
else
    if [ ! -f "$EVIDENCE_DIR/vmlinuz" ]; then
        echo "SKIPPED: Guest test kernel could not be downloaded; guest discrimination not exercised." | tee -a "$EVIDENCE_DIR/h2-summary.log"
    else
        echo "FAIL: Guest failure pattern unexpected." | tee -a "$EVIDENCE_DIR/h2-summary.log"
        OVERALL=1
    fi
fi

# Z3: splice the runner summary into the receipt so RESULT-POSTED lands on-branch.
if [ -f "$RECEIPT_FILE" ] && grep -q "\[PENDING RUNNER OUTPUT\]" "$RECEIPT_FILE"; then
    python3 - "$RECEIPT_FILE" "$EVIDENCE_DIR/h2-summary.log" <<'PYEOF'
import sys
receipt_path, summary_path = sys.argv[1], sys.argv[2]
with open(summary_path) as f:
    summary = f.read().strip()
with open(receipt_path) as f:
    receipt = f.read()
marker = "**[PENDING RUNNER OUTPUT]**"
detail = ("**ACTUAL RESULT (runner-spliced 2026-11-10):**

```
"
          + summary + "
```

"
          + "*(The workflow publishes this receipt to the lane automatically; "
          + "the seat may refine wording in a follow-up. Status: RESULT-POSTED pending Z/owner evaluation.)*")
receipt = receipt.replace(marker, detail)
with open(receipt_path, "w") as f:
    f.write(receipt)
print("Receipt updated with runner output.")
PYEOF
fi

echo "=== Evidence preserved in $EVIDENCE_DIR ==="
exit $OVERALL
