#!/usr/bin/env bash
# Only Mark dispatches the manual workflow; this entrypoint never dispatches it.
set -euo pipefail
task_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$task_dir/ci/driver.py"
