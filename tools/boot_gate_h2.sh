#!/bin/bash
set -e
EVIDENCE_DIR="${PUPPF_EVIDENCE_DIR:-./evidence}"
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
echo "[TEST 2] Simulating Guest Failure (Kernel Panic via empty initrd)..."
GUEST_LOG="$EVIDENCE_DIR/guest_serial.log"
GUEST_START=$(date +%s)

wget -q -O "$EVIDENCE_DIR/vmlinuz" "https://archive.ubuntu.com/ubuntu/dists/jammy-updates/main/installer-amd64/current/legacy-images/netboot/ubuntu-installer/amd64/linux" || {
    echo "Failed to download test kernel. Marking Guest test as SKIPPED."
    GUEST_EXIT=125
}

set +e
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
    fi
fi
set -e

echo "=== H2 DISCRIMINATING LOGIC ==="
if [ "$HOST_EXIT" -ne 0 ] && [ "$HOST_DURATION" -lt 5 ] && [ "$HOST_LOG_SIZE" -eq 0 ]; then
    echo "PASS: Host failure correctly identified by early exit and empty serial log."
else
    echo "FAIL: Host failure pattern unexpected."
fi

if [ -f "$EVIDENCE_DIR/vmlinuz" ] && [ "$GUEST_DURATION" -ge 5 ] && grep -q "$PANIC_STRING" "$GUEST_LOG"; then
    echo "PASS: Guest failure correctly identified by sustained runtime and panic string in serial log."
else
    echo "FAIL: Guest failure pattern unexpected."
fi
