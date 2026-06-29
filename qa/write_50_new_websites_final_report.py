#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_RUNS = ROOT / "docs" / "script-runs"
FINAL_JSON = SCRIPT_RUNS / "50-new-websites-final-rebuild-report.json"
FINAL_MD = SCRIPT_RUNS / "50-new-websites-final-rebuild-report.md"
COMPLIANCE_JSON = SCRIPT_RUNS / "50-new-websites-compliance-audit.json"
SIMILARITY_JSON = SCRIPT_RUNS / "50-new-websites-similarity-audit.json"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def latest_capture_report() -> tuple[str, dict | None]:
    root = ROOT / "final" / "homepage-screenshots"
    if not root.exists():
        return "not captured", None
    reports = sorted(root.glob("full-*/capture-report.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        return "not captured", None
    report = read_json(reports[0], None)
    return str(reports[0].parent.relative_to(ROOT)), report


def main() -> int:
    report = read_json(FINAL_JSON, {})
    compliance = read_json(COMPLIANCE_JSON, {"passed": False, "failures": [], "concepts": {}})
    similarity = read_json(SIMILARITY_JSON, {"passed": False, "failures": []})
    screenshot_folder, screenshot_report = latest_capture_report()
    manual_review = sorted(
        set(item["concept"] for item in compliance.get("failures", []))
        | set(pair for failure in similarity.get("failures", []) for pair in failure.get("pair", []))
    )

    report.update(
        {
            "finalizedAt": datetime.now(UTC).isoformat(),
            "screenshotFolder": screenshot_folder,
            "complianceAuditResult": "passed" if compliance.get("passed") else "failed",
            "similarityAuditResult": "passed" if similarity.get("passed") else "failed",
            "sectionCountResult": "passed" if compliance.get("passed") else "see compliance failures",
            "noCropResult": "passed" if compliance.get("passed") else "see compliance failures",
            "blankFrameResult": "passed" if compliance.get("passed") else "see compliance failures",
            "fakeLabelResult": "passed" if compliance.get("passed") else "see compliance failures",
            "photoCountResult": "passed" if compliance.get("passed") else "see compliance failures",
            "colourRhythmResult": "passed" if not any("colour" in item.get("issue", "") for item in compliance.get("failures", [])) else "failed",
            "remainingConflictBlockers": compliance.get("failures", []),
            "conceptsThatStillNeedManualReview": manual_review,
            "screenshotCaptureResult": screenshot_report,
        }
    )

    for concept_id, concept_result in compliance.get("concepts", {}).items():
        if concept_id in report.get("finalStatusPerConcept", {}):
            status = report["finalStatusPerConcept"][concept_id]
            passed = concept_result.get("passed", False)
            status["allRealPagesTenSections"] = passed
            status["photosFullAndUncropped"] = passed
            status["blankFramesGone"] = passed
            status["oldAtlasClassesGone"] = passed
            status["conflictingReferencesGone"] = passed
            status["manualReviewNeeded"] = concept_id in manual_review

    FINAL_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# 50 New Websites Final Rebuild Report",
        "",
        f"- Branch name: `{report.get('branchName', '')}`",
        f"- Number of concepts rebuilt: {report.get('conceptsRebuilt')}",
        f"- Number of pages changed: {report.get('pagesChanged')}",
        f"- Number of partials rewritten: {report.get('partialsRewritten')}",
        f"- Number of local CSS files rewritten: {report.get('localCssFilesRewritten')}",
        f"- Number of local JS files rewritten: {report.get('localJsFilesRewritten')}",
        f"- Screenshot folder: `{screenshot_folder}`",
        f"- Compliance audit result: {report['complianceAuditResult']}",
        f"- Similarity audit result: {report['similarityAuditResult']}",
        f"- Section count result: {report['sectionCountResult']}",
        f"- No-crop result: {report['noCropResult']}",
        f"- Blank frame result: {report['blankFrameResult']}",
        f"- Fake label result: {report['fakeLabelResult']}",
        f"- Photo count result: {report['photoCountResult']}",
        f"- Colour rhythm result: {report['colourRhythmResult']}",
        "",
        "## Old Conflict Files Removed From Active References",
        "",
        *[f"- `{item}`" for item in report.get("oldConflictFilesRemovedFromActiveReferences", [])],
        "",
        "## Manual Review",
        "",
        "None required by automated gates." if not manual_review else "\n".join(f"- `{item}`" for item in manual_review),
        "",
        "## Per Concept Status",
        "",
    ]
    for concept_id, status in report.get("finalStatusPerConcept", {}).items():
        lines.append(
            f"- `{concept_id}`: different website={status['differentWebsite']}; header={status['headerDiffers']}; hero={status['heroDiffers']}; section rhythm={status['sectionRhythmDiffers']}; colour rhythm={status['colourRhythmDiffers']}; footer={status['footerDiffers']}; mobile={status['mobileDiffers']}; 10 sections={status['allRealPagesTenSections']}; partials excluded={status['partialsExcluded']}; uncropped photos={status['photosFullAndUncropped']}; selective photos={status['photosSelective']}; blank frames gone={status['blankFramesGone']}; old Atlas gone={status['oldAtlasClassesGone']}; conflict refs gone={status['conflictingReferencesGone']}; CTA rhythm={status['ctaRhythmIntentional']}; Sofiati feel={status['stillFeelsSofiati']}."
        )
    FINAL_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Final report updated: {FINAL_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
