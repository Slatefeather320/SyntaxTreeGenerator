import shutil
import subprocess
from pathlib import Path
import sys
import time

PROJECT_DIR = Path(__file__).parent.resolve()
BUILD_DIR = PROJECT_DIR / "build" / "web"
CUSTOM_HTML = PROJECT_DIR / "custom.html"

process = subprocess.Popen([sys.executable, "-m", "pygbag", "main.py"])
time.sleep(1)

if CUSTOM_HTML.exists():
    shutil.copy(CUSTOM_HTML, BUILD_DIR / "index.html")
else:
    print(f"Could not find custom HTML at {CUSTOM_HTML}")

try:
    process.wait()
except KeyboardInterrupt:
    print("Server stopped")
    process.terminate()
