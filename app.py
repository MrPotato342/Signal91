import os
import logging

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Request
)

from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field

from phone_analyzer import analyze_phone

# ---------------------------------------------------
# Config
# ---------------------------------------------------

ENGINE_VERSION = "0.1.0"

INTERNAL_SECRET = os.getenv("INTERNAL_SECRET")

MAX_BULK_NUMBERS = 100

# ---------------------------------------------------
# Logging
# ---------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("signal91")

# ---------------------------------------------------
# FastAPI App
# ---------------------------------------------------

app = FastAPI(
    title="Signal91 - India Phone Intelligence API",
    version=ENGINE_VERSION,

    # Disable public docs in production
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# ---------------------------------------------------
# Security
# ---------------------------------------------------

def verify_gateway(
    x_internal_secret: str = Header(None)
):

    if not INTERNAL_SECRET:

        logger.error("INTERNAL_SECRET is not configured")

        raise HTTPException(
            status_code=500,
            detail="Server configuration error"
        )

    if x_internal_secret != INTERNAL_SECRET:

        logger.warning("Unauthorized request blocked")

        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

# ---------------------------------------------------
# Request Models
# ---------------------------------------------------

class PhoneRequest(BaseModel):

    phone: str = Field(
        ...,
        min_length=10,
        max_length=20
    )


class BulkRequest(BaseModel):

    numbers: list[str]

# ---------------------------------------------------
# Routes
# ---------------------------------------------------

@app.get("/health")
def health():

    return {
        "success": True,
        "status": "ok"
    }

# ---------------------------------------------------

@app.get("/version")
def version():

    return {
        "success": True,
        "engine_version": ENGINE_VERSION
    }

# ---------------------------------------------------

@app.post("/analyze")
def analyze(
    req: PhoneRequest,
    x_internal_secret: str = Header(None)
):

    verify_gateway(x_internal_secret)

    logger.info(f"Analyze request received")

    result = analyze_phone(req.phone)

    return {
        "success": True,
        "data": result
    }

# ---------------------------------------------------

@app.post("/bulk-analyze")
def bulk_analyze(
    req: BulkRequest,
    x_internal_secret: str = Header(None)
):

    verify_gateway(x_internal_secret)

    count = len(req.numbers)

    if count > MAX_BULK_NUMBERS:

        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_BULK_NUMBERS} numbers allowed"
        )

    logger.info(f"Bulk analyze request: {count} numbers")

    results = []

    for number in req.numbers:

        try:

            results.append({
                "success": True,
                "data": analyze_phone(number)
            })

        except Exception as exc:

            logger.exception(
                f"Failed analyzing number: {number}"
            )

            results.append({
                "success": False,
                "phone": number,
                "error": str(exc)
            })

    return {
        "success": True,
        "count": count,
        "results": results
    }

# ---------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):

    logger.exception(
        f"Unhandled exception: {str(exc)}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error"
        }
    )