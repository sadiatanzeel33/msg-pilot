"""Vercel serverless entry point — exposes the FastAPI app."""

import sys
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

from app.main import app
