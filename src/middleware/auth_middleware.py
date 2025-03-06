from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.auth.jwt_handler import verify_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "authorization" in request.headers:
            token = request.headers["authorization"].split(" ")[1]
            payload = verify_token(token)
            if payload:
                request.state.user = payload
        
        response = await call_next(request)
        return response 