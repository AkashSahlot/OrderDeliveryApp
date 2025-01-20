from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.api.home import router as home_router
from app.api.firebase_authentication import router as auth_router
from app.api.user import router as user_router
from app.api.order import router as order_router
from app.api.restaurant import router as restaurant_router
from app.core.firebase import initialize_firebase
from app.middleware.error_middleware import error_handler
from app.middleware.admin_logging import admin_action_logger

# Initialize Firebase at startup
initialize_firebase()

app = FastAPI(
    title="Food Delivery App",
    description="A FastAPI application for food delivery with Firebase authentication",
    version="1.0.0",
    openapi_tags=[
        {"name": "HomePage", "description": "Home endpoint operations"},
        {"name": "Auth", "description": "Authentication operations with Firebase"},
        {"name": "User", "description": "User operations"}
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Auth middleware
app.middleware("http")(AuthMiddleware())

# Add error handling middleware
app.middleware("http")(error_handler)

# Add admin logging middleware
app.middleware("http")(admin_action_logger)

# Include routers
app.include_router(home_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(restaurant_router)
app.include_router(order_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
