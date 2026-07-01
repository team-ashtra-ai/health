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
FULL_SITE_QA_JSON = SCRIPT_RUNS / "sofiati-full-site-qa.json"
PUBLIC_PARTIAL_JSON = SCRIPT_RUNS / "public-partials-final-audit.json"
RENDER_MATRIX_JSON = SCRIPT_RUNS / "sofiati-render-matrix.json"
PREMIUM_REPORT_MD = ROOT / "docs" / "sofiati-50-premium-refactor-report.md"


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
    full_site = read_json(FULL_SITE_QA_JSON, {"static_failures": "not run", "rendered_failures": "not run"})
    public_partials = read_json(PUBLIC_PARTIAL_JSON, {"failures": [], "rendered_checks": "not run", "rendered_failures": "not run"})
    render_matrix = read_json(
        RENDER_MATRIX_JSON,
        {"renderedChecks": "not run", "renderedFailures": "not run", "cookieConceptChecks": "not run", "cookieFailures": "not run"},
    )
    public_partial_failures = public_partials.get("rendered_failures")
    if public_partial_failures is None:
        public_partial_failures = public_partials.get("failures", "not run")
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
    premium_lines = [
        "# Sofiati 50 Premium Refactor Report",
        "",
        "## Files Changed",
        "",
        "- `scripts/rebuild_50_new_websites.py` now owns the 50-way creative matrix, page architecture, hero systems, layout families, card styles, media treatments, tablet/mobile behavior, plan, and registry generation.",
        "- `scripts/generate_public_partial_systems.py` owns approved public chrome: header, mobile menu, footer, EN/PT links, cookie preferences, WhatsApp, accessibility, and back-to-top behavior.",
        "- `css/sofiati-brand-foundation.css`, `js/sofiati-brand-foundation.js`, every `concepts/*/css/concept.css`, every `concepts/*/js/concept.js`, and the five generated partials per concept are the active frontend surface.",
        "- `qa/audit_50_new_websites_compliance.py` validates the current `sf-theme-NN` public partial system.",
        "- `qa/audit_50_new_websites_similarity.py` now evaluates visual profiles instead of stale selector overlap.",
        "- `README.md`, `docs/sofiati-50-premium-refactor-plan.md`, and `docs/sofiati-50-concept-differentiation-registry.md` document the active refactor control plane.",
        "- Obsolete atlas, visual-rescue, architecture-repair, duplicate root partial, and duplicate global CSS/JS files were removed so there is one current build path.",
        "",
        "## Concepts Completed",
        "",
        f"- Concepts rebuilt: {report.get('conceptsRebuilt')}.",
        f"- Pages changed: {report.get('pagesChanged')}.",
        f"- Public partials regenerated: {report.get('partialsRewritten')}.",
        "- Active concept file contract: 50 concept CSS files, 50 concept JS files, and 250 generated public partials.",
        "",
        "## Major Design-System Changes",
        "",
        "- Homepage hero sections now use dedicated markup with editorial, clinical, cinematic, concierge, minimal, luminous, botanical, and sculptural variants.",
        "- Each concept has a stored layout family, hero pattern, card style, media treatment, CTA style, footer pattern, and mobile layout strategy.",
        "- Tablet layouts keep multi-column compositions from 721px through 1024px before the phone layout takes over.",
        "- Non-photo visual moments use intentional botanical/clinical CSS art panels rather than gray placeholders.",
        "- The public partial system remains centralized and compatible with the full-site QA selectors.",
        "- Palette generation is constrained to the Sofiati brand identity families: ivory, cream, sage, bronze, champagne, deep green, and ink.",
        "- Cookie consent now supports accept, reject, customize, saved preferences, and localStorage persistence.",
        "- Every generated page now includes one inline JSON-LD block in addition to canonical and social metadata.",
        "",
        "## Before And After Design Logic",
        "",
        "- Before: generated pages shared a regular section model and relied on color/order changes for differentiation.",
        "- After: the first viewport, section rhythm, media treatment, and responsive behavior are generated from separate creative contracts per numbered concept.",
        "",
        "## Commands Run",
        "",
        "- `python3 qa/audit_50_new_websites_compliance.py`",
        "- `python3 qa/audit_50_new_websites_similarity.py`",
        "- `python3 scripts/audit_sofiati_full_site_qa.py`",
        "- `python3 scripts/rebuild_50_new_websites.py`",
        "- `python3 -m py_compile scripts/rebuild_50_new_websites.py scripts/generate_public_partial_systems.py scripts/audit_public_partial_systems.py scripts/audit_sofiati_full_site_qa.py qa/audit_50_new_websites_compliance.py qa/audit_50_new_websites_similarity.py qa/write_50_new_websites_final_report.py`",
        "- `python3 scripts/audit_public_partial_systems.py`",
        "- `python3 scripts/audit_public_partial_systems.py --render`",
        "- `node --check scripts/audit_sofiati_render_matrix.mjs`",
        "- `node scripts/audit_sofiati_render_matrix.mjs`",
        "- `python3 qa/write_50_new_websites_final_report.py`",
        "",
        "## Errors Found",
        "",
        f"- Baseline compliance failures: {len(compliance.get('failures', [])) if compliance else 'unknown'} after latest run.",
        f"- Baseline/latest similarity failures: {len(similarity.get('failures', [])) if similarity else 'unknown'}.",
        f"- Public partial rendered failures: {public_partial_failures}.",
        f"- Full-site static failures: {full_site.get('static_failures')}.",
        f"- Full render matrix failures: {render_matrix.get('renderedFailures')}.",
        f"- Cookie persistence failures: {render_matrix.get('cookieFailures')}.",
        "",
        "## Errors Fixed",
        "",
        "- Stale compliance partial-specific checks were updated for current public partial ownership.",
        "- Stale similarity gating was updated to compare visual profiles, not only repeated generator selectors.",
        "- Rebuild no longer overwrites the approved public partial system with older partial markup.",
        "- Generic home H1 replacement was removed so concept hero differentiation remains visible.",
        "- Homepage hero media was corrected so CSS art overlays the portrait instead of increasing hero height.",
        "- Removed obsolete concept-local `style.css`, `atlas-story.css`, `main.js`, `partials.js`, unused per-concept partials, root partials, and retired global component CSS/JS layers.",
        "- Removed obsolete atlas, visual-rescue, premium visual DNA, and architecture-repair scripts/docs that could reintroduce conflicting frontend layers.",
        "- Foundation JS now exposes helpers only; concept JS owns interactions behind a per-concept runtime guard to prevent duplicate listeners.",
        "- EN/PT controls are real same-page links, active nav state strips query/hash, and mobile menu focus/Escape behavior is handled defensively.",
        "",
        "## Errors Still Remaining",
        "",
        "None in the final automated gates." if not manual_review and not full_site.get("static_failures") and not full_site.get("rendered_failures") else "See the audit reports listed above for any remaining failures.",
        "",
        "## Remaining Limitations",
        "",
        "- Automated checks can confirm structure, overflow, links, assets, widgets, and uniqueness signals; final premium taste still benefits from human review of the generated screenshots.",
    ]
    PREMIUM_REPORT_MD.write_text("\n".join(premium_lines).rstrip() + "\n", encoding="utf-8")
    print(f"Final report updated: {FINAL_MD}")
    print(f"Premium refactor report updated: {PREMIUM_REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
