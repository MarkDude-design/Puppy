#!/bin/bash
set -e
EVIDENCE_DIR="./evidence"
mkdir -p "$EVIDENCE_DIR"
HOST_LOG="$EVIDENCE_DIR/host_serial.log"
GUEST_LOG="$EVIDENCE_DIR/guest_serial.log"

echo "=== Qmax H2 Boundary Probe ==="

# --- HOST FAILURE ---
echo "[HOST] Simulating Host Failure..."
START=$(date +%s.%N)
set +e
qemu-system-x86_64 -nographic -kernel /nonexistent/path -no-reboot -serial file:"$HOST_LOG" > "$EVIDENCE_DIR/host_stdout.log" 2>&1
HOST_EXIT=$?
END=$(date +%s.%N)
set -e
HOST_TIME=$(echo "$END - $START" | bc)
HOST_LOG_SIZE=$(stat -c%s "$HOST_LOG" 2>/dev/null || echo 0)

echo "$HOST_TIME" > "$EVIDENCE_DIR/host_time.txt"
echo "$HOST_EXIT" > "$EVIDENCE_DIR/host_exit.txt"
echo "$HOST_LOG_SIZE" > "$EVIDENCE_DIR/host_log_size.txt"

# --- FAST GUEST FAILURE ---
echo "[GUEST] Simulating Fast Guest Failure..."
if [ ! -f "$KERNEL_PATH" ]; then
    echo "[GUEST] SKIPPED: Kernel missing."
    echo "SKIPPED" > "$EVIDENCE_DIR/guest_status.txt"
    echo "0" > "$EVIDENCE_DIR/guest_time.txt"
    echo "0" > "$EVIDENCE_DIR/guest_exit.txt"
    echo "0" > "$EVIDENCE_DIR/guest_log_size.txt"
    echo "SKIPPED" > "$EVIDENCE_DIR/guest_has_decomp.txt"
    exit 0
fi

START=$(date +%s.%N)
set +e
# Note: We intentionally use -no-reboot here to override the load-bearing 
# timeout loop from Round 1, allowing us to measure the FAST exit boundary.
qemu-system-x86_64 -nographic -kernel "$KERNEL_PATH" -append "console=ttyS0 panic=1" -no-reboot -serial file:"$GUEST_LOG" > "$EVIDENCE_DIR/guest_stdout.log" 2>&1
GUEST_EXIT=$?
END=$(date +%s.%N)
set -e
GUEST_TIME=$(echo "$END - $START" | bc)
GUEST_LOG_SIZE=$(stat -c%s "$GUEST_LOG" 2>/dev/null || echo 0)

echo "RUN" > "$EVIDENCE_DIR/guest_status.txt"
echo "$GUEST_TIME" > "$EVIDENCE_DIR/guest_time.txt"
echo "$GUEST_EXIT" > "$EVIDENCE_DIR/guest_exit.txt"
echo "$GUEST_LOG_SIZE" > "$EVIDENCE_DIR/guest_log_size.txt"

# Check for the load-bearing decompression string
if grep -q "Decompressing Linux" "$GUEST_LOG" 2>/dev/null; then
    echo "YES" > "$EVIDENCE_DIR/guest_has_decomp.txt"
else
    echo "NO" > "$EVIDENCE_DIR/guest_has_decomp.txt"
fi

echo "Probe complete."
