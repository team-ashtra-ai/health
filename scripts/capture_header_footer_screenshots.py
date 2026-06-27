#!/usr/bin/env python3
"""Capture combined header and footer screenshots for the public partial audit."""

from __future__ import annotations

import base64
import json
import shutil
import tempfile
import time
from io import BytesIO
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


def top_clip(client: DevToolsClient, width: int) -> dict[str, float]:
    expression = """
(() => {
  const selectors = [
    '.public-utility.status-banner',
    '.public-utility',
    '.public-utility-rule',
    '.public-header.site-header',
    '.public-header',
    '.site-header'
  ];
  let bottom = 0;
  let found = false;
  const scrollY = window.scrollY || document.documentElement.scrollTop || 0;
  for (const selector of selectors) {
    document.querySelectorAll(selector).forEach((node) => {
      const rect = node.getBoundingClientRect();
      const style = window.getComputedStyle(node);
      if (style.display === 'none' || style.visibility === 'hidden' || rect.height <= 0) return;
      found = true;
      bottom = Math.max(bottom, rect.bottom + scrollY);
    });
  }
  if (!found) bottom = Math.min(window.innerHeight, 160);
  return {
    x: 0,
    y: 0,
    width: __WIDTH__,
    height: Math.ceil(Math.min(bottom + 24, document.documentElement.scrollHeight)),
    scale: 1,
    topHeight: Math.ceil(bottom)
  };
})()
""".replace("__WIDTH__", str(width))
    result = client.command("Runtime.evaluate", {"expression": expression, "returnByValue": True}, timeout=30)
    value = result.get("result", {}).get("result", {}).get("value")
    if not isinstance(value, dict):
        raise RuntimeError("Could not evaluate top-system clip")
    return {
        "x": float(value["x"]),
        "y": float(value["y"]),
        "width": float(value["width"]),
        "height": float(value["height"]),
        "scale": float(value["scale"]),
        "topHeight": float(value["topHeight"]),
    }


def footer_clip(client: DevToolsClient, width: int) -> dict[str, float]:
    expression = """
(() => {
  const footer = document.querySelector('.public-footer');
  if (!footer) throw new Error('Missing .public-footer');
  const rect = footer.getBoundingClientRect();
  const scrollY = window.scrollY || document.documentElement.scrollTop || 0;
  return {
    x: 0,
    y: Math.max(0, Math.floor(rect.top + scrollY - 24)),
    width: __WIDTH__,
    height: Math.ceil(rect.height + 48),
    scale: 1,
    footerHeight: Math.ceil(rect.height)
  };
})()
""".replace("__WIDTH__", str(width))
    result = client.command("Runtime.evaluate", {"expression": expression, "returnByValue": True}, timeout=30)
    value = result.get("result", {}).get("result", {}).get("value")
    if not isinstance(value, dict):
        raise RuntimeError("Could not evaluate footer clip")
    return {
        "x": float(value["x"]),
        "y": float(value["y"]),
        "width": float(value["width"]),
        "height": float(value["height"]),
        "scale": float(value["scale"]),
        "footerHeight": float(value["footerHeight"]),
    }


def prepare_footer_for_capture(client: DevToolsClient) -> None:
    expression = """
(() => {
  const footer = document.querySelector('.public-footer');
  const dock = document.querySelector('[data-floating-tools]');
  if (!footer) throw new Error('Missing .public-footer');
  const scrollY = window.scrollY || document.documentElement.scrollTop || 0;
  const rect = footer.getBoundingClientRect();
  const target = Math.max(0, rect.top + scrollY + rect.height - window.innerHeight + 20);
  window.scrollTo(0, target);
  if (dock) {
    footer.style.position = 'relative';
    dock.classList.add('is-loaded', 'public-audit-footer-dock');
    dock.style.setProperty('position', 'absolute', 'important');
    dock.style.setProperty('right', '18px', 'important');
    dock.style.setProperty('bottom', '18px', 'important');
    dock.style.setProperty('top', 'auto', 'important');
    dock.style.setProperty('left', 'auto', 'important');
    dock.style.setProperty('opacity', '1', 'important');
    dock.style.setProperty('transform', 'none', 'important');
    dock.style.setProperty('pointer-events', 'auto', 'important');
    footer.appendChild(dock);
  }
  const topButton = document.querySelector('[data-back-to-top]');
  if (topButton) {
    topButton.classList.add('is-visible');
    topButton.setAttribute('aria-hidden', 'false');
    topButton.setAttribute('tabindex', '0');
  }
})()
"""
    client.command("Runtime.evaluate", {"expression": expression}, timeout=30)
    time.sleep(1.4)


def capture_mobile_menu(client: DevToolsClient, width: int, height: int) -> tuple[bytes | None, int]:
    expression = """
(() => {
  const menu = document.querySelector('#mobile-menu');
  const openButton = document.querySelector('[data-menu-toggle]');
  if (!menu) return false;
  window.scrollTo(0, 0);
  menu.classList.add('is-open');
  menu.setAttribute('aria-hidden', 'false');
  openButton?.setAttribute('aria-expanded', 'true');
  document.body.classList.add('public-menu-locked');
  return true;
})()
"""
    result = client.command("Runtime.evaluate", {"expression": expression, "returnByValue": True}, timeout=30)
    value = result.get("result", {}).get("result", {}).get("value")
    if value is not True:
        return None, 0
    time.sleep(0.5)
    png = capture_clip(
        client,
        {"x": 0, "y": 0, "width": float(width), "height": float(height), "scale": 1},
        capture_beyond_viewport=False,
    )
    close_expression = """
(() => {
  const menu = document.querySelector('#mobile-menu');
  const openButton = document.querySelector('[data-menu-toggle]');
  if (menu) {
    menu.classList.remove('is-open');
    menu.setAttribute('aria-hidden', 'true');
  }
  openButton?.setAttribute('aria-expanded', 'false');
  document.body.classList.remove('public-menu-locked');
  window.scrollTo(0, 0);
})()
"""
    client.command("Runtime.evaluate", {"expression": close_expression}, timeout=30)
    time.sleep(0.3)
    return png, height


def capture_clip(client: DevToolsClient, clip: dict[str, float], capture_beyond_viewport: bool = True) -> bytes:
    screenshot = client.command(
        "Page.captureScreenshot",
        {
            "format": "png",
            "fromSurface": True,
            "captureBeyondViewport": capture_beyond_viewport,
            "clip": clip,
        },
        timeout=60,
    )
    data = screenshot.get("result", {}).get("data")
    if not isinstance(data, str):
        raise RuntimeError("No screenshot data returned")
    return base64.b64decode(data)


def write_combined_image(top_png: bytes, menu_png: bytes | None, footer_png: bytes, output: Path, viewport: str) -> int:
    try:
        from PIL import Image
    except Exception as exc:
        raise RuntimeError("Pillow is required to compose header/footer audit screenshots") from exc

    with Image.open(BytesIO(top_png)) as top_image, Image.open(BytesIO(footer_png)) as footer_image:
        top_rgb = top_image.convert("RGB")
        footer_rgb = footer_image.convert("RGB")
        menu_rgb = None
        if menu_png:
            with Image.open(BytesIO(menu_png)) as menu_image:
                menu_rgb = menu_image.convert("RGB")
        gutter = 18 if viewport == "desktop" else 14
        width = max(top_rgb.width, footer_rgb.width)
        if menu_rgb:
            width = max(width, menu_rgb.width)
        height = top_rgb.height + gutter + footer_rgb.height
        if menu_rgb:
            height += menu_rgb.height + gutter
        canvas = Image.new("RGB", (width, height), "#F3EFE5")
        y = 0
        canvas.paste(top_rgb, ((width - top_rgb.width) // 2, y))
        y += top_rgb.height + gutter
        if menu_rgb:
            canvas.paste(menu_rgb, ((width - menu_rgb.width) // 2, y))
            y += menu_rgb.height + gutter
        canvas.paste(footer_rgb, ((width - footer_rgb.width) // 2, y))
        canvas.save(output)
        return height


def capture(client: DevToolsClient, folder: str, viewport: str, config: dict[str, object]) -> tuple[Path, int, int, int]:
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
    header_clip = top_clip(client, width)
    top_height = int(header_clip.pop("topHeight"))
    top_png = capture_clip(client, header_clip)
    menu_png, menu_height = capture_mobile_menu(client, width, height) if mobile else (None, 0)
    prepare_footer_for_capture(client)
    footer = footer_clip(client, width)
    footer_height = int(footer.pop("footerHeight"))
    footer_png = capture_clip(client, footer)
    image_height = write_combined_image(top_png, menu_png, footer_png, output, viewport)
    return output, top_height, menu_height, footer_height, image_height


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
                    output, top_height, menu_height, footer_height, image_height = capture(client, folder, viewport, config)
                    done += 1
                    rel = output.relative_to(ROOT).as_posix()
                    captured.append(
                        {
                            "viewport": viewport,
                            "concept": folder,
                            "url": f"/concepts/{folder}/index.html",
                            "file": rel,
                            "topHeight": str(top_height),
                            "menuHeight": str(menu_height),
                            "footerHeight": str(footer_height),
                            "imageHeight": str(image_height),
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
