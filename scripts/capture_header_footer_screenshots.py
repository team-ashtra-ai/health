#!/usr/bin/env python3
"""Capture desktop and mobile screenshots for the public partial audit."""

from __future__ import annotations

import base64
import json
import shutil
import tempfile
import time
from pathlib import Path

from capture_homepage_screenshots import (
    BASE_URL,
    CONCEPTS,
    DevToolsClient,
    ROOT,
    VIEWPORTS,
    chrome_binary,
    ensure_chrome,
    ensure_server,
    websocket_url,
)


AUDIT_DIR = ROOT / "audit"
SCREENSHOT_DIR = AUDIT_DIR / "screenshots"


def capture(client: DevToolsClient, folder: str, viewport: str, config: dict[str, object]) -> Path:
    out_dir = SCREENSHOT_DIR / viewport
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"{folder}-{viewport}.png"
    width = int(config["width"])
    height = int(config["height"])
    mobile = bool(config["mobile"])
    client.command(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile,
        },
    )
    client.command("Page.navigate", {"url": f"{BASE_URL}/concepts/{folder}/index.html"})
    client.wait_for_event("Page.loadEventFired", timeout=30)
    time.sleep(2.2)
    screenshot = client.command(
        "Page.captureScreenshot",
        {
            "format": "png",
            "fromSurface": True,
            "captureBeyondViewport": True,
        },
        timeout=60,
    )
    data = screenshot.get("result", {}).get("data")
    if not isinstance(data, str):
        raise RuntimeError(f"No screenshot data for {folder} {viewport}")
    output.write_bytes(base64.b64decode(data))
    return output


def maybe_contact_sheets(captured: list[dict[str, str]]) -> list[str]:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return []

    sheets: list[str] = []
    for viewport in VIEWPORTS:
        entries = [entry for entry in captured if entry["viewport"] == viewport]
        thumb_w = 260 if viewport == "desktop" else 150
        thumb_h = 260 if viewport == "desktop" else 360
        label_h = 30
        cols = 5 if viewport == "desktop" else 10
        rows = (len(entries) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "#F3EFE5")
        draw = ImageDraw.Draw(sheet)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 12)
        except Exception:
            font = None
        for index, entry in enumerate(entries):
            src = ROOT / entry["file"]
            with Image.open(src) as image:
                image = image.convert("RGB")
                image.thumbnail((thumb_w, thumb_h))
                x = (index % cols) * thumb_w
                y = (index // cols) * (thumb_h + label_h)
                bg = Image.new("RGB", (thumb_w, thumb_h), "#F8F7F2")
                bg.paste(image, ((thumb_w - image.width) // 2, 0))
                sheet.paste(bg, (x, y))
                draw.text((x + 8, y + thumb_h + 8), entry["concept"], fill="#252321", font=font)
        output = SCREENSHOT_DIR / f"{viewport}-contact-sheet.jpg"
        sheet.save(output, quality=88)
        sheets.append(output.relative_to(ROOT).as_posix())
    return sheets


def write_manifest(captured: list[dict[str, str]], sheets: list[str]) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "baseUrl": BASE_URL,
        "fullPage": True,
        "viewports": VIEWPORTS,
        "count": len(captured),
        "screenshots": captured,
        "contactSheets": sheets,
    }
    (SCREENSHOT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    server = ensure_server()
    chrome = chrome_binary()
    captured: list[dict[str, str]] = []
    chrome_process = None
    client = None
    try:
        if SCREENSHOT_DIR.exists():
            shutil.rmtree(SCREENSHOT_DIR)
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="sofiati-public-audit-") as tmp:
            chrome_process = ensure_chrome(chrome, Path(tmp) / "chrome-profile")
            client = DevToolsClient(websocket_url())
            client.command("Page.enable")
            total = len(CONCEPTS) * len(VIEWPORTS)
            done = 0
            for folder in CONCEPTS:
                for viewport, config in VIEWPORTS.items():
                    output = capture(client, folder, viewport, config)
                    done += 1
                    rel = output.relative_to(ROOT).as_posix()
                    captured.append(
                        {
                            "viewport": viewport,
                            "concept": folder,
                            "url": f"/concepts/{folder}/index.html",
                            "file": rel,
                        }
                    )
                    print(f"[{done:03d}/{total:03d}] {rel}")
        sheets = maybe_contact_sheets(captured)
        write_manifest(captured, sheets)
    finally:
        if client:
            client.close()
        if chrome_process:
            chrome_process.terminate()
        if server:
            server.terminate()


if __name__ == "__main__":
    main()
