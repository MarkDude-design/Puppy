#!/bin/bash
# Z-completion v2 2026-11-10 — after H2 run 1 (red, 31s, receipt never spliced).
# Root causes banked in sandbox/reviews/Z-REVIEW-h2-run1-crash-2026-11-10.md:
#   V1. Test-kernel source dead: the Ubuntu jammy legacy-netboot URL 404s
#       (verified live 2026-11-10); wget -O had left an empty file, so the
#       [ -f ] check accepted a zero-byte "kernel" and QEMU errored instantly.
#       Now: Alpine netboot vmlinuz-lts (verified live 2026-11-10), wget -L
#       --tries=2, and a real validation gate (non-empty, > 2 MiB) before the
#       guest leg may run. Throwaway-kernel doctrine unchanged: this lane
#       measures failure signatures, not the pinned route.
#   V2. Curator bug (owned): v1 dropped the seat's original set +e guard
#       around the guest QEMU call, so QEMU's fast error exit hard-killed the
#       script before the receipt splice. Guard restored.
#   V3. Failure-capture trap: any unexpected ERR now splices a failure entry
#       into RECEIPT.md before exiting — no receiptless runs, ever.
# Round-1 design notes preserved: panic=1 with no -no-reboot makes the guest
# panic, reset, and panic again until the timeout — that loop produces exit 124
# + a populated serial log; do not "fix" it. Failure exits red; skip != fail.
# Timeout raised 15 -> 30 s for TCG headroom; still discriminates (host < 5s
# vs guest filling the window; receipt expectation "Duration >= 5s" unchanged).
set -e
EVIDENCE_DIR="${PUPPF_EVIDENCE_DIR:-./evidence}"
RECEIPT_FILE="${PUPPF_RECEIPT_FILE:-./sandbox/qmax-lab-20261110/RECEIPT.md}"
TIMEOUT=30
PANIC_STRING="Kernel panic"
KERNEL_URL="https://dl-cdn.alpinelinux.org/alpine/v3.22/releases/x86_64/netboot/vmlinuz-lts"
mkdir -p "$EVIDENCE_DIR"
HOST_LOG="$EVIDENCE_DIR/host_serial.log"
GUEST_LOG="$EVIDENCE_DIR/guest_serial.log"

echo "=== Qcoder H2 Test: Host vs Guest Failure Discrimination ==="

splice_receipt() {
    # $1 = one-line detail; replaces the PENDING marker if still present.
    if [ -f "$RECEIPT_FILE" ] && grep -q "\[PENDING RUNNER OUTPUT\]" "$RECEIPT_FILE"; then
        python3 - "$RECEIPT_FILE" "$1" <<'PYEOF'
import sys
receipt_path, detail = sys.argv[1], sys.argv[2]
with open(receipt_path) as f:
    receipt = f.read()
marker = "**[PENDING RUNNER OUTPUT]**"
block = ("**ACTUAL RESULT (runner-spliced 2026-11-10):**

```
"
         + detail + "
```

"
         + "*(Published automatically; the seat may refine wording in a follow-up.)*")
receipt = receipt.replace(marker, block)
with open(receipt_path, "w") as f:
    f.write(receipt)
print("Receipt updated.")
PYEOF
    fi
}

on_err() {
    trap - ERR
    echo "SCRIPT ERROR: unexpected failure at line $1 (exit $2) — splicing failure receipt." | tee -a "$EVIDENCE_DIR/h2-summary.log" 2>/dev/null || true
    splice_receipt "UNEXPECTED SCRIPT FAILURE at line $1 (exit $2). Discrimination NOT completed. Evidence in the h2-evidence artifact."
    exit "$2"
}
trap 'on_err $LINENO $?' ERR

# --- TEST 1: Host Environment Failure ---
echo "[TEST 1] Simulating Host Failure (invalid kernel path)..."
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
rm -f "$EVIDENCE_DIR/vmlinuz"
GUEST_OK=0
GUEST_STATUS="SKIPPED"
if ! wget -q -L --tries=2 -O "$EVIDENCE_DIR/vmlinuz" "$KERNEL_URL"; then
    echo "[GUEST] Test-kernel download failed."
fi
KERNEL_SIZE=$(stat -c%s "$EVIDENCE_DIR/vmlinuz" 2>/dev/null || echo 0)
if [ "$KERNEL_SIZE" -gt 2097152 ]; then
    GUEST_STATUS="RUN"
    GUEST_START=$(date +%s)
    set +e
    timeout $TIMEOUT qemu-system-x86_64 -nographic -kernel "$EVIDENCE_DIR/vmlinuz" -append "console=ttyS0 panic=1" -serial file:"$GUEST_LOG" > "$EVIDENCE_DIR/guest_stdout.log" 2>&1
    GUEST_EXIT=$?
    set -e
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
else
    echo "[GUEST] SKIPPED: test kernel missing or too small (${KERNEL_SIZE} bytes)."
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
    if [ "$GUEST_STATUS" = "RUN" ]; then
        echo "FAIL: Guest failure pattern unexpected." | tee -a "$EVIDENCE_DIR/h2-summary.log"
        OVERALL=1
    else
        echo "SKIPPED: Guest test kernel could not be downloaded or failed validation; guest discrimination not exercised." | tee -a "$EVIDENCE_DIR/h2-summary.log"
    fi
fi

# Splice the runner summary into the receipt so RESULT-POSTED lands on-branch.
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
