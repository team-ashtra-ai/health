#!/usr/bin/env python3
"""Capture full-page desktop and mobile homepage screenshots for every concept."""

from __future__ import annotations

import base64
import json
import os
import secrets
import shutil
import socket
import struct
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
FINAL_DIR = ROOT / "final" / "homepage-screenshots"
PORT = 8000
DEBUG_PORT = 9223
BASE_URL = f"http://127.0.0.1:{PORT}"
DEBUG_URL = f"http://127.0.0.1:{DEBUG_PORT}"
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1100, "mobile": False},
    "mobile": {"width": 390, "height": 844, "mobile": True},
}
CONCEPTS = [
    "01-inspire", "02-empower", "03-enhance", "04-renew", "05-elevate",
    "06-refine", "07-glow", "08-balance", "09-radiance", "10-essence",
    "11-bloom", "12-vital", "13-poise", "14-aura", "15-clarity",
    "16-grace", "17-sculpt", "18-lumin", "19-verda", "20-halo",
    "21-calm", "22-precision", "23-ritual", "24-signal", "25-align",
    "26-vivant", "27-form", "28-pure", "29-solace", "30-method",
    "31-evolve", "32-serene", "33-elan", "34-flora", "35-atelier",
    "36-lumina", "37-vellum", "38-origin", "39-kindred", "40-noble",
    "41-vista", "42-softline", "43-meridian", "44-safeguard", "45-silhouette",
    "46-curate", "47-proof", "48-signature", "49-wisdom", "50-sovereign",
]


def server_ready() -> bool:
    try:
        urllib.request.urlopen(BASE_URL, timeout=1).read(64)
        return True
    except (urllib.error.URLError, TimeoutError):
        return False


def ensure_server() -> subprocess.Popen[bytes] | None:
    if server_ready():
        return None
    process = subprocess.Popen(
        ["python3", "-m", "http.server", str(PORT)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(50):
        if server_ready():
            return process
        time.sleep(0.2)
    process.terminate()
    raise RuntimeError(f"Local server did not start on port {PORT}")


def chrome_binary() -> str:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("Could not find Chrome or Chromium for screenshots")


def debug_ready() -> bool:
    try:
        urllib.request.urlopen(f"{DEBUG_URL}/json/version", timeout=1).read(64)
        return True
    except (urllib.error.URLError, TimeoutError):
        return False


def ensure_chrome(chrome: str, profile: Path) -> subprocess.Popen[bytes]:
    process = subprocess.Popen(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--hide-scrollbars",
            "--disable-background-networking",
            f"--remote-debugging-port={DEBUG_PORT}",
            f"--user-data-dir={profile}",
            "about:blank",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(70):
        if debug_ready():
            return process
        time.sleep(0.2)
    process.terminate()
    raise RuntimeError(f"Chrome DevTools did not start on port {DEBUG_PORT}")


class DevToolsSocket:
    def __init__(self, websocket_url: str) -> None:
        parsed = urllib.parse.urlparse(websocket_url)
        if parsed.scheme != "ws":
            raise RuntimeError(f"Unsupported websocket URL: {websocket_url}")
        self.sock = socket.create_connection((parsed.hostname or "127.0.0.1", parsed.port or 80), timeout=20)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {parsed.hostname}:{parsed.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(request.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            response += self.sock.recv(4096)
        if b" 101 " not in response.split(b"\r\n", 1)[0]:
            raise RuntimeError("Chrome DevTools websocket handshake failed")

    def send_text(self, text: str) -> None:
        payload = text.encode("utf-8")
        header = bytearray([0x81])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        mask = secrets.token_bytes(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(bytes(header) + mask + masked)

    def recv_text(self) -> str:
        while True:
            first = self.sock.recv(2)
            if not first:
                raise RuntimeError("DevTools websocket closed")
            opcode = first[0] & 0x0F
            length = first[1] & 0x7F
            masked = bool(first[1] & 0x80)
            if length == 126:
                length = struct.unpack("!H", self.sock.recv(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self.sock.recv(8))[0]
            mask = self.sock.recv(4) if masked else b""
            payload = b""
            while len(payload) < length:
                payload += self.sock.recv(length - len(payload))
            if masked:
                payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
            if opcode == 0x8:
                raise RuntimeError("DevTools websocket closed")
            if opcode == 0x9:
                self.send_pong(payload)
                continue
            if opcode == 0x1:
                return payload.decode("utf-8")

    def send_pong(self, payload: bytes) -> None:
        header = bytearray([0x8A])
        header.append(0x80 | len(payload))
        mask = secrets.token_bytes(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(bytes(header) + mask + masked)

    def close(self) -> None:
        self.sock.close()


class DevToolsClient:
    def __init__(self, websocket_url: str) -> None:
        self.socket = DevToolsSocket(websocket_url)
        self.next_id = 1

    def command(self, method: str, params: dict[str, object] | None = None, timeout: float = 30) -> dict[str, object]:
        message_id = self.next_id
        self.next_id += 1
        self.socket.send_text(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            message = json.loads(self.socket.recv_text())
            if message.get("id") == message_id:
                if "error" in message:
                    raise RuntimeError(f"DevTools error for {method}: {message['error']}")
                return message
        raise TimeoutError(f"Timed out waiting for {method}")

    def wait_for_event(self, method: str, timeout: float = 30) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            message = json.loads(self.socket.recv_text())
            if message.get("method") == method:
                return
        raise TimeoutError(f"Timed out waiting for {method}")

    def close(self) -> None:
        self.socket.close()


def websocket_url() -> str:
    targets = json.loads(urllib.request.urlopen(f"{DEBUG_URL}/json", timeout=2).read().decode("utf-8"))
    for target in targets:
        if target.get("type") == "page" and target.get("webSocketDebuggerUrl"):
            return str(target["webSocketDebuggerUrl"])
    raise RuntimeError("No Chrome page target found")


def pages() -> list[tuple[str, str]]:
    result = [("selector-home", "/")]
    for folder in CONCEPTS:
        result.append((f"concept-{folder}-home", f"/concepts/{folder}/index.html"))
    return result


def capture(client: DevToolsClient, slug: str, url_path: str, viewport: str, config: dict[str, object]) -> Path:
    out_dir = FINAL_DIR / viewport
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"{slug}-{viewport}.png"
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
    client.command("Page.navigate", {"url": f"{BASE_URL}{url_path}"})
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
        raise RuntimeError(f"No screenshot data for {slug} {viewport}")
    output.write_bytes(base64.b64decode(data))
    return output


def maybe_contact_sheets(captured: list[dict[str, str]]) -> list[str]:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return []

    sheets: list[str] = []
    for viewport in VIEWPORTS:
        entries = [entry for entry in captured if entry["viewport"] == viewport and entry["page"].startswith("concept-")]
        if not entries:
            continue
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
                draw.text((x + 8, y + thumb_h + 8), entry["page"].replace("concept-", "").replace("-home", ""), fill="#252321", font=font)
        output = FINAL_DIR / f"{viewport}-contact-sheet.jpg"
        sheet.save(output, quality=88)
        sheets.append(output.relative_to(ROOT).as_posix())
    return sheets


def write_manifest(captured: list[dict[str, str]], sheets: list[str]) -> None:
    manifest = {
        "baseUrl": BASE_URL,
        "fullPage": True,
        "viewports": VIEWPORTS,
        "count": len(captured),
        "screenshots": captured,
        "contactSheets": sheets,
    }
    (FINAL_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (FINAL_DIR / "README.md").write_text(
        "# Homepage Screenshots\n\n"
        "Full-page desktop and mobile screenshots for the selector homepage and all 50 standalone concept homepages.\n\n"
        + "\n".join(f"- `{sheet}`" for sheet in sheets)
        + ("\n" if sheets else ""),
        encoding="utf-8",
    )


def main() -> None:
    missing = [folder for folder in CONCEPTS if not (CONCEPTS_DIR / folder / "index.html").exists()]
    if missing:
        raise SystemExit("Missing concept homepages: " + ", ".join(missing))

    server = ensure_server()
    chrome = chrome_binary()
    captured: list[dict[str, str]] = []
    chrome_process: subprocess.Popen[bytes] | None = None
    client: DevToolsClient | None = None
    try:
        if FINAL_DIR.exists():
            shutil.rmtree(FINAL_DIR)
        FINAL_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="sofiati-screenshots-") as tmp:
            profile = Path(tmp) / "chrome-profile"
            chrome_process = ensure_chrome(chrome, profile)
            client = DevToolsClient(websocket_url())
            client.command("Page.enable")
            all_pages = pages()
            total = len(all_pages) * len(VIEWPORTS)
            done = 0
            for slug, url_path in all_pages:
                for viewport, config in VIEWPORTS.items():
                    output = capture(client, slug, url_path, viewport, config)
                    done += 1
                    rel = output.relative_to(ROOT).as_posix()
                    captured.append({"viewport": viewport, "page": slug, "url": url_path, "file": rel})
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
