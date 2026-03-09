from pathlib import Path
import sys

API_APP_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
if str(API_APP_DIR) not in sys.path:
    sys.path.insert(0, str(API_APP_DIR))
