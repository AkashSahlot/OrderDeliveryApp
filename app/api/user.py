from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from firebase_admin import firestore
from app.dto.user import UserResponse, UserBase
from app.dto.order import Order
from app.api.firebase_authentication import verify_firebase_token
from typing import List
from datetime import datetime
from app.core.firebase import db  # Import the Firestore client

router = APIRouter(
    prefix="/users",
    tags=["User"]
)

security = HTTPBearer()


@router.get("/profile",
    response_model=UserResponse,
    summary="Get user profile",
    description="Get the profile information for the authenticated user"
)
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        is_custom_token = 'uid' in decoded and 'claims' in decoded

        if is_custom_token:
                # For custom tokens, we need to exchange it for an ID token first
                # Return the decoded info since we can't verify custom tokens server-side

                uid = decoded['uid']
        else:
            uid = decoded['uid']


        user_doc = db.collection('users').document(uid).get()
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user_doc.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@router.put("/profile",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update the profile information for the authenticated user"
)
async def update_user_profile(
    user_update: UserBase,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        is_custom_token = 'uid' in decoded and 'claims' in decoded

        if is_custom_token:
                # For custom tokens, we need to exchange it for an ID token first
                # Return the decoded info since we can't verify custom tokens server-side

                uid = decoded['uid']
        else:
            uid = decoded['uid']

        user_ref = db.collection('users').document(uid)
        if not user_ref.get().exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = user_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        user_ref.update(update_data)
        
        updated_user = user_ref.get().to_dict()
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
