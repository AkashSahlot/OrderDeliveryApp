from fastapi import Request, HTTPException, status
from firebase_admin import auth
from typing import List

class AuthMiddleware:
    def __init__(self, public_paths: List[str] = None):
        self.public_paths = public_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/register",
            "/auth/login",
            "/auth/me",
            "/"
        ]

    async def __call__(self, request: Request, call_next):
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)

        try:
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header"
                )

            token = authorization.split(" ")[1]
            try:
                decoded_token = auth.verify_id_token(token)
                request.state.user = decoded_token
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

            return await call_next(request)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            ) 