from datetime import datetime
import os

HEALTH_FILE = "data/health.txt"

def update_health():
    os.makedirs("data", exist_ok=True)
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        f.write(f"OK {datetime.now().isoformat()}")