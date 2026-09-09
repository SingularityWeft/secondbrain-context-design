#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

privacy_args=()
if [[ -n "${CLIEF_PRIVATE_DENYLIST:-}" ]]; then
  privacy_args=(--private-denylist "$CLIEF_PRIVATE_DENYLIST")
fi

python3 scripts/check_repository.py "${privacy_args[@]}"
python3 scripts/check_public_history.py "${privacy_args[@]}"
python3 scripts/check_skills.py
python3 scripts/check_pilot.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/run_e2e.py >/dev/null
git diff --check
git diff --cached --check

echo "VERIFY_REPO_PASS"
