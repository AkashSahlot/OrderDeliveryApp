from fastapi import APIRouter

router = APIRouter(
    tags=["HomePage"]
)

@router.get("/",
    summary="Home endpoint",
    description="Hello world route to make sure the app is working correctly",
    response_model=dict
)
def home():
    return {"msg": "Hello To The Food Delivery APP"}

# app/api/firebase_authentication.py
