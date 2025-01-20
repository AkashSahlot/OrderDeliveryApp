# app/api/firebase_authentication.py

from fastapi import APIRouter, Depends, HTTPException, status, Header, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from firebase_admin import auth
from app.dto.user import UserRegister, UserLogin, UserResponse, UserRole
from app.core.firebase import initialize_firebase, db
from google.cloud import firestore
from datetime import datetime
import jwt

# Initialize Firebase
initialize_firebase()

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# Create security scheme for Swagger UI
security = HTTPBearer()

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        print(f"Verifying token: {token[:50]}...")  # Debug log
        
        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(token)
            print(f"Decoded token: {decoded_token}")  # Debug log
            
            # Get user data from Firestore
            user_doc = db.collection('users').document(decoded_token['uid']).get()
            if not user_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found in database"
                )
            
            user_data = user_doc.to_dict()
            print(f"User data: {user_data}")  # Debug log
            
            return decoded_token
            
        except auth.InvalidIdTokenError:
            print("Invalid token format")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        except Exception as e:
            print(f"Token verification error: {str(e)}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
    except Exception as e:
        print(f"Authorization error: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )

async def verify_admin(token_data: dict = Depends(verify_firebase_token)):
    try:
        # Get user from Firestore
        user_doc = db.collection('users').document(token_data['uid']).get()
        
        if not user_doc.exists:
            print(f"User not found in Firestore: {token_data['uid']}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        print(f"User data from Firestore: {user_data}")  # Debug log
        
        # Check if user has admin role
        if user_data.get('role') != UserRole.ADMIN:
            print(f"User role is not admin: {user_data.get('role')}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
            
        return user_data  # Return full user data instead of just token_data
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in verify_admin: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error verifying admin privileges"
        )

@router.post("/register",
    response_model=dict,
    summary="Register new user",
    description="Register a new user with Firebase"
)
async def register_user(user: UserRegister):
    try:
        # Create user in Firebase Auth
        user_record = auth.create_user(
            email=user.email,
            password=user.password
        )
        
        # Set custom claims for role
        auth.set_custom_user_claims(user_record.uid, {
            'role': user.role,
            'admin': user.role == UserRole.ADMIN
        })
        
        # Store user data in Firestore
        user_data = user.dict(exclude={'password'})
        user_data['uid'] = user_record.uid
        
        db.collection('users').document(user_record.uid).set(user_data)
        
        return {
            "message": "User registered successfully",
            "uid": user_record.uid
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login",
    response_model=dict,
    summary="Login user",
    description="Login with email and password to get Firebase token"
)
async def login_user(user: UserLogin):
    try:
        # Get user by email
        user_record = auth.get_user_by_email(user.email)
        
        # Create custom token
        custom_token = auth.create_custom_token(user_record.uid)
        
        # Get user data from Firestore
        user_doc = db.collection('users').document(user_record.uid).get()
        user_data = user_doc.to_dict()
        
        return {
            "message": "Login successful",
            "uid": user_record.uid,
            "email": user_record.email,
            "role": user_data.get('role'),
            "token": custom_token.decode('utf-8')
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get details of currently authenticated user"
)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        # Verify token
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        
        # Get user from Firestore
        user_doc = db.collection('users').document(decoded_token['uid']).get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        return UserResponse(**user_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.get("/verify-token",
    response_model=dict,
    summary="Verify token",
    description="Verify if the provided token is valid"
)
async def verify_token(token: str = Query(..., description="Firebase token to verify")):
    try:
        decoded_token = auth.verify_id_token(token)
        return {
            "message": "Token is valid",
            "decoded": decoded_token
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/logout",
    response_model=dict,
    summary="Logout user",
    description="Invalidate the current user's session"
)
async def logout_user(email: str):
    try:
        # Get user by email
        user_record = auth.get_user_by_email(email)
        
        # Revoke refresh tokens
        auth.revoke_refresh_tokens(user_record.uid)
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/refresh-token",
    response_model=dict,
    summary="Refresh token",
    description="Get a new token using the refresh token"
)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        # Verify current token and generate new one
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        new_token = auth.create_custom_token(decoded_token['uid'])
        
        return {
            "message": "Token refreshed successfully",
            "token": new_token.decode('utf-8')
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/change-password",
    response_model=dict,
    summary="Change password",
    description="Change the user's password"
)
async def change_password(
    old_password: str,
    new_password: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        
        # Update password
        auth.update_user(
            decoded_token['uid'],
            password=new_password
        )
        
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/debug-token",
    summary="Debug token",
    description="Debug the provided token"
)
async def debug_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        print("Received token:", token)  # Debug print
        
        # Try to decode without verification first
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            print("Decoded token (without verification):", decoded)
        except Exception as e:
            print("JWT decode error:", str(e))
        
        # Now try Firebase verification
        try:
            decoded_token = auth.verify_id_token(token)
            print("Firebase decoded token:", decoded_token)
            return {"message": "Token is valid", "decoded": decoded_token}
        except Exception as e:
            print("Firebase verification error:", str(e))
            return {"message": "Token verification failed", "error": str(e)}
            
    except Exception as e:
        print("General error:", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Debug error: {str(e)}"
        )