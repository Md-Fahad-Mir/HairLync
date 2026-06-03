from __future__ import annotations

import os
import socket
import logging
import tempfile
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from hair_code import analyze, enrich_analysis_with_tutorials, save_results


logger = logging.getLogger("main")


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
    hair_length: Literal["short", "medium", "long"] = Form(...),
    save_report: bool = Form(False),
) -> dict[str, Any]:
    suffix = _guess_suffix(image)
    if not suffix:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Use jpg, jpeg, png, webp, or gif.",
        )

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(await image.read())

        result = enrich_analysis_with_tutorials(analyze(temp_path, gender, hair_length))
        response: dict[str, Any] = {
            "analysis": result,
            "meta": {
                "filename": image.filename,
                "content_type": image.content_type,
                "gender": gender,
                "hair_length": hair_length,
                "saved_report": False,
            },
        }

        if save_report:
            report_name = Path(image.filename or "upload").stem or "upload"
            json_path, md_path = save_results(result, report_name)
            response["meta"]["saved_report"] = True
            response["meta"]["json_report"] = str(json_path)
            response["meta"]["markdown_report"] = str(md_path)

        return response

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=os.getenv("RELOAD", "false").lower() == "true")