#!/bin/bash
set -euo pipefail

echo "=== Qcoder Lab: P0a Reproducibility Test ==="

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

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
    export PUPPF_EVIDENCE_DIR="$evidence_dir"
    export RUNNER_TEMP="${RUNNER_TEMP:-/tmp}"
    
    # Invoke the actual P0a CI script
    bash puppy-p0a/ci/run-ci.sh
    
    echo "--- $run_name Complete ---"
}

# Execute Run 1
run_build "$EVIDENCE_DIR_1" "Build Run 1"

# Execute Run 2
run_build "$EVIDENCE_DIR_2" "Build Run 2"

echo "=== Comparing Artifacts ==="

ARTIFACTS_1="$EVIDENCE_DIR_1/artifacts"
ARTIFACTS_2="$EVIDENCE_DIR_2/artifacts"

if [[ -f "$ARTIFACTS_1/bzImage" && -f "$ARTIFACTS_2/bzImage" ]]; then
    HASH1_BZ=$(sha256sum "$ARTIFACTS_1/bzImage" | awk '{print $1}')
    HASH2_BZ=$(sha256sum "$ARTIFACTS_2/bzImage" | awk '{print $1}')
    
    HASH1_RF=$(sha256sum "$ARTIFACTS_1/rootfs.cpio.gz" | awk '{print $1}')
    HASH2_RF=$(sha256sum "$ARTIFACTS_2/rootfs.cpio.gz" | awk '{print $1}')
    
    echo "Run 1 bzImage:    $HASH1_BZ"
    echo "Run 2 bzImage:    $HASH2_BZ"
    echo "Run 1 rootfs:     $HASH1_RF"
    echo "Run 2 rootfs:     $HASH2_RF"
    
    if [[ "$HASH1_BZ" == "$HASH2_BZ" && "$HASH1_RF" == "$HASH2_RF" ]]; then
        REPRO_RESULT="PASS: Identical digests across clean builds."
    else
        REPRO_RESULT="FAIL: Divergent digests detected."
    fi
    
    # Append actual result to RECEIPT.md
    RECEIPT_FILE="$REPO_ROOT/sandbox/qcoder-lab-20261110/RECEIPT.md"
    if [[ -f "$RECEIPT_FILE" ]]; then
        sed -i "s/\*PENDING EXECUTION\*/ACTUAL RESULT:\n- bzImage Match: $([[ "$HASH1_BZ" == "$HASH2_BZ" ]] && echo 'YES' || echo 'NO')\n- rootfs Match: $([[ "$HASH1_RF" == "$HASH2_RF" ]] && echo 'YES' || echo 'NO')\n- Run 1 bzImage: \`$HASH1_BZ\`\n- Run 2 bzImage: \`$HASH2_BZ\`\n- Run 1 rootfs: \`$HASH1_RF\`\n- Run 2 rootfs: \`$HASH2_RF\`\n\nConclusion: $REPRO_RESULT/" "$RECEIPT_FILE"
        echo "Updated $RECEIPT_FILE with actual results."
    fi
else
    echo "ERROR: Artifacts not found. Check build logs."
    echo "RESULT: BUILD FAILURE"
fi

# Note: We do NOT clean up the evidence directories here so they can be 
# uploaded by the GitHub Actions workflow as artifacts for Z/Mark review.
echo "=== Test Complete. Evidence preserved for upload ==="
