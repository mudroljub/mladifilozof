"""Serve the project locally and rebuild it when source texts change."""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread


ROOT = Path(__file__).parent
TEXTS = ROOT / "tekstovi"


def source_state() -> dict[Path, int]:
    """Return mtimes for files that can change the generated site."""
    files = [ROOT / "build.py", *TEXTS.rglob("*.txt")]
    return {path: path.stat().st_mtime_ns for path in files if path.exists()}


def rebuild() -> bool:
    result = subprocess.run([sys.executable, "build.py"], cwd=ROOT)
    if result.returncode:
        print("Obnova nije uspela; čekam sledeću izmenu.")
        return False
    return True


def watch(interval: float) -> None:
    previous = source_state()
    while True:
        time.sleep(interval)
        current = source_state()
        changed = sorted(set(previous) ^ set(current) | {p for p in current if previous.get(p) != current[p]})
        if changed:
            names = ", ".join(str(path.relative_to(ROOT)) for path in changed)
            print(f"Promena: {names}")
            rebuild()
            previous = source_state()


def main() -> None:
    # PowerShell/Windows consoles may still expose a legacy code page.
    # Explicit UTF-8 keeps Serbian help and status text reliable.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Lokalni server sa automatskom obnovom sajta.")
    parser.add_argument("--port", type=int, default=8000, help="Port servera (podrazumevano 8000).")
    parser.add_argument("--interval", type=float, default=1.0, help="Učestalost provere u sekundama.")
    args = parser.parse_args()

    rebuild()
    Thread(target=watch, args=(args.interval,), daemon=True).start()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), SimpleHTTPRequestHandler)
    print(f"Sajt je dostupan na http://127.0.0.1:{args.port}/")
    print("Pratim tekstovi/ i build.py. Za prekid pritisni Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer je zaustavljen.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
