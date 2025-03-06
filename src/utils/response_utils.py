from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse

def success_response(data: Any = None, message: str = "Success") -> Dict:
    return {
        "status": "success",
        "message": message,
        "data": data
    }

def error_response(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "data": None
        }
    ) 