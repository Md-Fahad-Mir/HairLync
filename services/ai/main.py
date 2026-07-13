from __future__ import annotations

import os
import socket
import logging
import tempfile
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from hair_code import analyze, enrich_analysis_with_tutorials


logger = logging.getLogger("main")

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def _log_startup_banner() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    env = os.getenv("APP_ENV", "development")
    local_ip = _get_local_ip()
    docs_url = f"http://localhost:{port}/docs"
    lan_url = f"http://{local_ip}:{port}/docs"
    tailscale_host = os.getenv("TAILSCALE_HOST")
    tailscale_url = os.getenv("TAILSCALE_URL")

    logger.info("🚀 Hair AI API starting | env=%s", env)
    logger.info("%s", "=" * 78)
    logger.info("API Docs: http://%s:%s/docs", host, port)
    logger.info("Local:  http://localhost:%s/ | Docs: %s", port, docs_url)
    logger.info("LAN:    http://%s:%s/ | Docs: %s", local_ip, port, lan_url)
    if tailscale_url:
        logger.info("Tailscale: %s | Docs: %s", tailscale_url, tailscale_url.rstrip("/") + "/docs")
    elif tailscale_host:
        logger.info(
            "Tailscale: http://%s:%s/ | Docs: http://%s:%s/docs",
            tailscale_host,
            port,
            tailscale_host,
            port,
        )
    logger.info("Share the LAN URL with teammates on the same network.")
    logger.info("%s", "=" * 78)


def _parse_csv_env(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def _guess_suffix(upload: UploadFile) -> str:
    filename = upload.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return suffix

    content_type = (upload.content_type or "").lower()
    mapping = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return mapping.get(content_type, "")


app = FastAPI(
    title="Hair AI Analysis API",
    version="1.0.0",
    description=(
        "FastAPI wrapper around the existing hair and face analysis engine. "
        "Use this service to upload a photo, generate AI analysis, and fetch "
        "the OpenAPI spec for backend integration."
    ),
)

allowed_origins = _parse_csv_env("CORS_ORIGINS")
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
def startup_banner() -> None:
    _configure_logging()
    _log_startup_banner()


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "service": "Hair AI Analysis API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "swagger": "/swagger.json",
    }


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/swagger.json", include_in_schema=False)
def swagger_json() -> dict[str, Any]:
    return app.openapi()


@app.post("/analyze", tags=["analysis"])
async def analyze_image(
    image: UploadFile = File(...),
    gender: Literal["male", "female"] = Form(...),
    hair_length: Literal["short", "medium", "long", "extra long"] = Form(...),
    occasion: Literal["casual", "formal", "wedding", "party", "business", "date", "everyday"] = Form(...),
) -> dict[str, Any]:
    suffix = _guess_suffix(image)
    if not suffix:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Use jpg, jpeg, png, webp, or gif.",
        )

    contents = await image.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large. Max size is {MAX_UPLOAD_BYTES // (1024 * 1024)}MB.",
        )
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(contents)

        normalized_hair_length = hair_length.replace(" ", "_")
        # analyze() / enrich_analysis_with_tutorials() are synchronous and do
        # blocking network I/O (OpenAI + YouTube) — run off the event loop so
        # one slow request doesn't stall every other concurrent request.
        result = await run_in_threadpool(
            lambda: enrich_analysis_with_tutorials(
                analyze(temp_path, gender, normalized_hair_length, occasion)
            )
        )
        response: dict[str, Any] = {
            "analysis": result,
            "meta": {
                "filename": image.filename,
                "content_type": image.content_type,
                "gender": gender,
                "hair_length": hair_length,
                "occasion": occasion,
            },
        }

        return response

    except HTTPException:
        raise
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        # Known, expected failure modes (missing key, bad image, invalid model config).
        logger.error("Analysis failed: %s", exc)
        raise HTTPException(status_code=502, detail="AI analysis failed. Please try again shortly.") from exc
    except Exception:
        logger.exception("Unexpected error during image analysis")
        raise HTTPException(status_code=500, detail="Internal server error.") from None
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                logger.warning("Failed to remove temp file %s", temp_path)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=os.getenv("RELOAD", "false").lower() == "true")