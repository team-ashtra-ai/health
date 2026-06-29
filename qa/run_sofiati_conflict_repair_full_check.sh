#!/usr/bin/env bash
set -u

ROOT="/run/media/code/Storage/GitHub/ashtra/health"
cd "$ROOT" || exit 1

mkdir -p docs/script-runs

MASTER_REPORT="docs/script-runs/conflict-repair-full-terminal-run.txt"
: > "$MASTER_REPORT"

log() {
  echo -e "\n========== $1 ==========" | tee -a "$MASTER_REPORT"
}

run_cmd() {
  echo -e "\n$ $*" | tee -a "$MASTER_REPORT"
  "$@" 2>&1 | tee -a "$MASTER_REPORT"
}

log "START"
date | tee -a "$MASTER_REPORT"

log "GIT STATE BEFORE"
run_cmd git branch --show-current
run_cmd git status --short
run_cmd git diff --stat

log "PYTHON SCRIPT SYNTAX CHECK"
run_cmd python3 -m py_compile qa/fix_sofiati_architecture_conflicts.py

log "RUN ARCHITECTURE CONFLICT AUDIT"
run_cmd python3 qa/fix_sofiati_architecture_conflicts.py --audit

log "RUN SAFE FIX ON REPAIR BRANCH"
run_cmd python3 qa/fix_sofiati_architecture_conflicts.py --fix --branch

log "GIT STATE AFTER FIX"
run_cmd git branch --show-current
run_cmd git status --short
run_cmd git diff --stat

log "SECTION COUNT VALIDATION — REAL PAGES ONLY"
find concepts -name "*.html" -not -path "*/partials/*" | while read -r f; do
  count=$(grep -c "<section" "$f" || true)
  if [ "$count" -ne 10 ]; then
    echo "$count sections: $f"
  fi
done | tee docs/script-runs/pages-not-10-sections-after-conflict-repair.txt | tee -a "$MASTER_REPORT"

log "BAD GENERATED ASSET TEXT CHECK"
grep -RIn "pattern decoration\|home background\|section background\|decorative asset\|texture decoration\|CONCEPT-SPECIFIC\|concept-specific\|section asset\|background asset" concepts --exclude-dir=partials \
  | tee docs/script-runs/remaining-bad-asset-text-after-conflict-repair.txt \
  | tee -a "$MASTER_REPORT" || true

log "OBJECT-FIT COVER CHECK"
grep -RIn "object-fit: cover" concepts css --include="*.css" --include="*.html" \
  | tee docs/script-runs/remaining-object-fit-cover-after-conflict-repair.txt \
  | tee -a "$MASTER_REPORT" || true

log "DUPLICATE CONFLICT REPAIR CSS/JS LINK CHECK"
grep -RIn "sofiati-architecture-conflict-repair.css" concepts --include="*.html" \
  | tee docs/script-runs/conflict-repair-css-links.txt \
  | tee -a "$MASTER_REPORT" || true

grep -RIn "sofiati-architecture-conflict-repair.js" concepts --include="*.html" \
  | tee docs/script-runs/conflict-repair-js-links.txt \
  | tee -a "$MASTER_REPORT" || true

log "NODE SYNTAX CHECK"
find scripts qa -name "*.mjs" -print0 | xargs -0 -I{} sh -c 'echo "checking {}"; node --check "{}"' \
  | tee docs/script-runs/conflict-repair-node-check.txt \
  | tee -a "$MASTER_REPORT"

log "REPORT SUMMARY"
sed -n '1,260p' docs/script-runs/architecture-conflict-repair-report.md | tee -a "$MASTER_REPORT"

log "IMPORTANT WARNINGS"
grep -n "duplicate\|mobile\|menu\|warning\|photo overuse\|section\|contrast\|partial" docs/script-runs/architecture-conflict-repair-report.md \
  | head -120 \
  | tee docs/script-runs/conflict-repair-important-warnings.txt \
  | tee -a "$MASTER_REPORT" || true

log "VALIDATION RESULT SUMMARY"

SECTION_ISSUES=$(wc -l < docs/script-runs/pages-not-10-sections-after-conflict-repair.txt | tr -d ' ')
BAD_TEXT_ISSUES=$(wc -l < docs/script-runs/remaining-bad-asset-text-after-conflict-repair.txt | tr -d ' ')
COVER_ISSUES=$(wc -l < docs/script-runs/remaining-object-fit-cover-after-conflict-repair.txt | tr -d ' ')

echo "Real-page section-count issues: $SECTION_ISSUES" | tee -a "$MASTER_REPORT"
echo "Bad generated asset text hits: $BAD_TEXT_ISSUES" | tee -a "$MASTER_REPORT"
echo "object-fit: cover hits: $COVER_ISSUES" | tee -a "$MASTER_REPORT"

if [ "$SECTION_ISSUES" = "0" ]; then
  echo "PASS: all real pages still have 10 sections." | tee -a "$MASTER_REPORT"
else
  echo "CHECK: some real pages do not have 10 sections." | tee -a "$MASTER_REPORT"
fi

if [ "$BAD_TEXT_ISSUES" = "0" ]; then
  echo "PASS: no bad generated asset text found in real visitor-facing pages." | tee -a "$MASTER_REPORT"
else
  echo "CHECK: bad generated asset text remains." | tee -a "$MASTER_REPORT"
fi

log "START LOCAL PREVIEW SERVER"

PORT=8080

python3 - <<'PY' > docs/script-runs/port-8080-status.txt
import socket
s = socket.socket()
try:
    s.bind(("127.0.0.1", 8080))
    print("free")
except OSError:
    print("busy")
finally:
    s.close()
PY

PORT_STATUS=$(cat docs/script-runs/port-8080-status.txt)

if [ "$PORT_STATUS" = "free" ]; then
  nohup python3 -m http.server "$PORT" > docs/script-runs/http-server-8080.log 2>&1 &
  echo $! > docs/script-runs/http-server-8080.pid
  echo "Preview server started on port $PORT" | tee -a "$MASTER_REPORT"
  echo "PID: $(cat docs/script-runs/http-server-8080.pid)" | tee -a "$MASTER_REPORT"
else
  echo "Port $PORT is already in use. Existing preview server may already be running." | tee -a "$MASTER_REPORT"
fi

log "OPEN THIS"
echo "http://localhost:8080/select.html" | tee -a "$MASTER_REPORT"

log "MANUAL VISUAL CHECKLIST"
cat <<'EOF' | tee -a "$MASTER_REPORT"
Desktop:
- only one nav menu appears
- no duplicated left/right nav inside the same header
- hero text is readable
- hero photo stays full-image
- floating consultation button does not cover hero CTAs

Mobile:
- menu links are hidden by default
- tapping Menu opens the menu
- menu closes after tapping a link or pressing Escape
- hero title is not hidden behind the menu
- Consultation/WhatsApp does not cover the main buttons
EOF

log "DONE"
echo "Full terminal report saved to: $MASTER_REPORT"
