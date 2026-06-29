#!/usr/bin/env python3
"""Capture full-page homepage screenshots for all 50 Sofiati concepts."""

from __future__ import annotations

import argparse
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
DEFAULT_PORT = 8000

CONCEPTS = [
    "01-inspire",
    "02-empower",
    "03-enhance",
    "04-renew",
    "05-elevate",
    "06-refine",
    "07-glow",
    "08-balance",
    "09-radiance",
    "10-essence",
    "11-bloom",
    "12-vital",
    "13-poise",
    "14-aura",
    "15-clarity",
    "16-grace",
    "17-sculpt",
    "18-lumin",
    "19-verda",
    "20-halo",
    "21-calm",
    "22-precision",
    "23-ritual",
    "24-signal",
    "25-align",
    "26-vivant",
    "27-form",
    "28-pure",
    "29-solace",
    "30-method",
    "31-evolve",
    "32-serene",
    "33-elan",
    "34-flora",
    "35-atelier",
    "36-lumina",
    "37-vellum",
    "38-origin",
    "39-kindred",
    "40-noble",
    "41-vista",
    "42-softline",
    "43-meridian",
    "44-safeguard",
    "45-silhouette",
    "46-curate",
    "47-proof",
    "48-signature",
    "49-wisdom",
    "50-sovereign",
]


def concept_index_path(concept_id: str) -> Path:
    return CONCEPTS_DIR / concept_id / "index.html"


def build_url(port: int, concept_id: str) -> str:
    return f"http://localhost:{port}/concepts/{quote(concept_id)}/index.html"


def ensure_server_reachable(port: int) -> None:
    concept = CONCEPTS[0]
    index_path = concept_index_path(concept)
    if not index_path.exists():
        raise SystemExit(f"Missing concept page: {index_path}")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def output_dir() -> Path:
    return ROOT / "final" / "homepage-screenshots" / f"full-{timestamp()}"


def iter_concepts() -> Iterable[str]:
    return CONCEPTS


def run_node_capture(port: int, out_dir: Path, headed: bool) -> None:
    node_script = textwrap.dedent(
        f"""
        const {{ chromium }} = require('playwright');
        const path = require('path');

        const port = {port};
        const headed = {str(headed).lower()};
        const outDir = {out_dir.as_posix()!r};
        const concepts = {CONCEPTS!r};

        const buildUrl = (conceptId) => `http://localhost:${{port}}/concepts/${{encodeURIComponent(conceptId)}}/index.html`;

        (async () => {{
          const browser = await chromium.launch({{ headless: !headed }});
          const context = await browser.newContext({{
            viewport: {{ width: 1440, height: 1800 }},
            deviceScaleFactor: 1,
          }});
          const page = await context.newPage();

          for (const conceptId of concepts) {{
            await page.goto(buildUrl(conceptId), {{ waitUntil: 'networkidle' }});
            await page.screenshot({{
              path: path.join(outDir, `${{conceptId}}-home-full.png`),
              fullPage: true,
            }});
          }}

          await context.close();
          await browser.close();
        }})().catch((error) => {{
          console.error(error);
          process.exit(1);
        }});
        """
    )
    subprocess.run(["node", "-e", node_script], cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture full-page homepage screenshots for all 50 concepts."
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run the browser in headed mode for debugging.",
    )
    args = parser.parse_args()

    ensure_server_reachable(args.port)
    out_dir = output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    run_node_capture(args.port, out_dir, args.headed)

    print(f"Saved full-page homepage screenshots to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
