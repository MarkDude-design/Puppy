#!/bin/bash
# Z-completion 2026-11-10 — QC's original design preserved; wiring fixes per
# sandbox/reviews/Z-REVIEW-qcoder-repro-2026-11-10.md:
#   Z1. PUPPF_EXPECTED_PACKET_SHA256 exported — driver.py blocks without it.
#   Z2. Run-1 scratch build tree removed after run-1 evidence is complete
#       (build trees are not evidence; run 2 would otherwise fail the
#       driver's 10 GiB disk floor). Guarded to RUNNER_TEMP/puppf-p0a-* only.
#   Z3. Failure paths now write the actual result to RECEIPT.md — negative
#       results preserved on-branch, per this lane's own receipt doctrine.
#   Z4. Divergent digests report CONFIRMED (hypothesis supported), not FAIL.
set -euo pipefail

echo "=== Qcoder Lab: P0a Reproducibility Test ==="

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

RECEIPT_FILE="$REPO_ROOT/sandbox/qcoder-lab-20261110/RECEIPT.md"

write_receipt_failure() {
    # Z3: a BLOCKED or failed run still leaves the branch receipt truthful.
    if [[ -f "$RECEIPT_FILE" ]] && grep -q "PENDING EXECUTION" "$RECEIPT_FILE"; then
        sed -i "s/\*PENDING EXECUTION\*/ACTUAL RESULT:\n- Outcome: $1\n- Detail: $2\n- Digest comparison NOT performed.\n\nConclusion: run halted before comparison; driver status and logs live in the qcoder-reproducibility-evidence artifact./" "$RECEIPT_FILE"
        echo "Receipt updated with failure outcome."
    fi
}

# Create isolated evidence directories for each run
EVIDENCE_DIR_1=$(mktemp -d -t puppf-repro-1.XXXXXX)
EVIDENCE_DIR_2=$(mktemp -d -t puppf-repro-2.XXXXXX)

echo "Run 1 Evidence Dir: $EVIDENCE_DIR_1"
echo "Run 2 Evidence Dir: $EVIDENCE_DIR_2"

# Function to execute the build
run_build() {
    local evidence_dir=$1
    local run_name=$2

    echo "--- Starting $run_name ---"
    export GITHUB_ACTIONS=true
    export PUPPF_MODE=build
    # Z1: pinned dispatch digest required by driver.py's packet gate.
    export PUPPF_EXPECTED_PACKET_SHA256=b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b
    export PUPPF_EVIDENCE_DIR="$evidence_dir"
    export RUNNER_TEMP="${RUNNER_TEMP:-/tmp}"

    # Invoke the actual P0a CI script (full route: build + two TCG boots)
    if ! bash puppy-p0a/ci/run-ci.sh; then
        echo "$run_name did not complete (driver BLOCKED or FAIL; see evidence artifact)."
        write_receipt_failure "$run_name did not complete" "driver exited non-zero; status in evidence artifact receipt.json"
        exit 1
    fi

    echo "--- $run_name Complete ---"
}

# Execute Run 1
run_build "$EVIDENCE_DIR_1" "Build Run 1"

# Z2: remove run 1's scratch build tree (recorded in its build-manifest.json).
# Build trees are not evidence per puppy-p0a/README.md; run 2 needs the disk
# headroom for the driver's 10 GiB floor check. Guarded removal.
SCRATCH_1=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("scratch_directory",""))' "$EVIDENCE_DIR_1/build-manifest.json" 2>/dev/null || true)
if [[ -n "${SCRATCH_1:-}" ]]; then
    case "$SCRATCH_1" in
        "$RUNNER_TEMP"/puppf-p0a-*) rm -rf "$SCRATCH_1" && echo "Removed run 1 scratch: $SCRATCH_1" ;;
        *) echo "Scratch path outside guard, not removed: $SCRATCH_1" ;;
    esac
fi

# Execute Run 2
run_build "$EVIDENCE_DIR_2" "Build Run 2"

echo "=== Comparing Artifacts ==="

ARTIFACTS_1="$EVIDENCE_DIR_1/artifacts"
ARTIFACTS_2="$EVIDENCE_DIR_2/artifacts"

if [[ -f "$ARTIFACTS_1/bzImage" && -f "$ARTIFACTS_2/bzImage" && -f "$ARTIFACTS_1/rootfs.cpio.gz" && -f "$ARTIFACTS_2/rootfs.cpio.gz" ]]; then
    HASH1_BZ=$(sha256sum "$ARTIFACTS_1/bzImage" | awk '{print $1}')
    HASH2_BZ=$(sha256sum "$ARTIFACTS_2/bzImage" | awk '{print $1}')

    HASH1_RF=$(sha256sum "$ARTIFACTS_1/rootfs.cpio.gz" | awk '{print $1}')
    HASH2_RF=$(sha256sum "$ARTIFACTS_2/rootfs.cpio.gz" | awk '{print $1}')

    echo "Run 1 bzImage:    $HASH1_BZ"
    echo "Run 2 bzImage:    $HASH2_BZ"
    echo "Run 1 rootfs:     $HASH1_RF"
    echo "Run 2 rootfs:     $HASH2_RF"

    # Z4: divergence is the stated hypothesis, not a malfunction.
    if [[ "$HASH1_BZ" == "$HASH2_BZ" && "$HASH1_RF" == "$HASH2_RF" ]]; then
        REPRO_RESULT="REFUTED: digests are bit-identical across clean builds; the non-determinism hypothesis is not supported."
    else
        REPRO_RESULT="CONFIRMED: divergent digests detected across clean builds; the non-determinism hypothesis is supported."
    fi

    # Append actual result to RECEIPT.md
    if [[ -f "$RECEIPT_FILE" ]]; then
        sed -i "s/\*PENDING EXECUTION\*/ACTUAL RESULT:\n- bzImage Match: $([[ "$HASH1_BZ" == "$HASH2_BZ" ]] && echo 'YES' || echo 'NO')\n- rootfs Match: $([[ "$HASH1_RF" == "$HASH2_RF" ]] && echo 'YES' || echo 'NO')\n- Run 1 bzImage: \`$HASH1_BZ\`\n- Run 2 bzImage: \`$HASH2_BZ\`\n- Run 1 rootfs: \`$HASH1_RF\`\n- Run 2 rootfs: \`$HASH2_RF\`\n\nConclusion: $REPRO_RESULT/" "$RECEIPT_FILE"
        echo "Updated $RECEIPT_FILE with actual results."
    fi
else
    echo "ERROR: Artifacts not found. Check build logs."
    write_receipt_failure "one or more artifacts missing after runs" "bzImage or rootfs.cpio.gz absent from an evidence artifacts dir; see evidence artifact"
    exit 1
fi

# Note: We do NOT clean up the evidence directories here so they can be
# uploaded by the GitHub Actions workflow as artifacts for Z/Mark review.
echo "=== Test Complete. Evidence preserved for upload ==="
