#!/usr/bin/env bash
set -euo pipefail

message="${1:-Sofiati website update - $(date +%F)}"

git add -A
git commit -m "$message"
git push origin HEAD
