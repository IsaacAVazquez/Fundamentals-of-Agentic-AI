# Vercel's Python runtime looks for an ASGI `app` here. The real app lives in dashboard/app.py.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import app  # noqa: E402,F401
