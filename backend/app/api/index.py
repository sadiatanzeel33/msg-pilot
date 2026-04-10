"""Vercel serverless entry point — exposes the FastAPI app."""

import sys
import os
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Ensure the backend root is on sys.path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

app = FastAPI()
_import_error = None

try:
    from app.main import app  # noqa: F811
except Exception as e:
    _import_error = str(e)
    _import_tb = traceback.format_exc()

    @app.get("/{path:path}")
    async def debug_error(path: str):
        return JSONResponse(
            status_code=500,
            content={"error": _import_error, "traceback": _import_tb},
        )
