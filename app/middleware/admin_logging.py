from fastapi import Request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def admin_action_logger(request: Request, call_next):
    if request.url.path.startswith("/restaurants"):
        user = getattr(request.state, "user", None)
        logger.info(f"Admin action: {request.method} {request.url.path} by user {user['uid'] if user else 'unknown'}")
    
    response = await call_next(request)
    return response 