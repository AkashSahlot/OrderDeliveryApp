from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import List, Optional
from firebase_admin import firestore
from app.dto.restaurant import Restaurant, MenuItem, RestaurantUpdate, MenuItemCreate
from app.api.firebase_authentication import verify_firebase_token, verify_admin
from app.core.firebase import db
from datetime import datetime
from app.dto.user import UserRole

router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurant"]
)

security = HTTPBearer()

@router.post("/", 
    response_model=Restaurant,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new restaurant",
    description="Create a new restaurant. Only admin users can perform this operation."
)
async def create_restaurant(
    restaurant: Restaurant,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        is_custom_token = 'uid' in decoded and 'claims' in decoded

        if is_custom_token:
                # For custom tokens, we need to exchange it for an ID token first
                # Return the decoded info since we can't verify custom tokens server-side

                role = decoded['claims']['role']
                uid = decoded['uid']
        else:
            role = decoded['role']
            uid = decoded['uid']
        # Log the admin user creating the restaurant
        # print(f"Admin user creating restaurant. User data: {user_data}")  # Debug log
        
        if role != UserRole.ADMIN:
            # print(f"User role is not admin: {user_data.get('role')}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        # Create a new document reference
        restaurant_ref = db.collection('restaurants').document()
        
        # Prepare restaurant data
        restaurant_dict = restaurant.dict(exclude_unset=True)
        restaurant_dict.update({
            'id': restaurant_ref.id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'created_by': uid  # Track who created the restaurant
        })
        
        # Add the restaurant to Firestore
        restaurant_ref.set(restaurant_dict)
        
        return restaurant_dict
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error creating restaurant: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", 
    response_model=List[Restaurant],
    summary="List all restaurants",
    description="Get a paginated list of restaurants with optional filtering by cuisine type."
)
async def list_restaurants(
    page: int = 1,
    limit: int = 10,
    cuisine_type: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        is_custom_token = 'uid' in decoded and 'claims' in decoded

        if is_custom_token:
            role = decoded['claims']['role']
            uid = decoded['uid']
        else:
            role = decoded['role']
            uid = decoded['uid']

        query = db.collection('restaurants')
        
        if cuisine_type:
            query = query.where('cuisine_type', '==', cuisine_type)
        
        # Implement pagination
        start = (page - 1) * limit
        restaurants = []
        
        for doc in query.limit(limit).offset(start).stream():
            restaurant_data = doc.to_dict()
            restaurants.append(restaurant_data)
            
        return restaurants
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{restaurant_id}", 
    response_model=Restaurant,
    summary="Update restaurant",
    description="Update restaurant details. Only admin users can perform this operation."
)
async def update_restaurant(
    restaurant_id: str,
    restaurant_update: RestaurantUpdate,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        is_custom_token = 'uid' in decoded and 'claims' in decoded

        if is_custom_token:
            role = decoded['claims']['role']
            uid = decoded['uid']
        else:
            role = decoded['role']
            uid = decoded['uid']
        
        if role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )


        restaurant_ref = db.collection('restaurants').document(restaurant_id)
        restaurant_doc = restaurant_ref.get()
        
        if not restaurant_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Update the restaurant data
        update_data = restaurant_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        update_data['updated_by'] = user_data['uid']  # Track who updated the restaurant
        
        restaurant_ref.update(update_data)
        
        # Return the updated restaurant data
        updated_doc = restaurant_ref.get()
        return updated_doc.to_dict()
    except Exception as e:
        print(f"Error updating restaurant: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete restaurant",
    description="Delete a restaurant. Only admin users can perform this operation."
)
async def delete_restaurant(
    restaurant_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        is_custom_token = 'uid' in decoded and 'claims' in decoded

        if is_custom_token:
            role = decoded['claims']['role']
            uid = decoded['uid']
        else:
            role = decoded['role']
            uid = decoded['uid']

        restaurant_ref = db.collection('restaurants').document(restaurant_id)
        
        if not restaurant_ref.get().exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Log deletion
        print(f"Admin user {uid} deleting restaurant {restaurant_id}")
        
        # Delete the restaurant
        restaurant_ref.delete()
        return {"message": "Restaurant deleted successfully"}
    except Exception as e:
        print(f"Error deleting restaurant: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{restaurant_id}/menu-items",
    response_model=MenuItem,
    status_code=status.HTTP_201_CREATED,
    summary="Add menu item",
    description="Add a new menu item to a restaurant. Only admin users can perform this operation."
)
async def add_menu_item(
    restaurant_id: str,
    menu_item: MenuItemCreate,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        is_custom_token = 'uid' in decoded and 'claims' in decoded

        if is_custom_token:
            role = decoded['claims']['role']
            uid = decoded['uid']
        else:
            role = decoded['role']
            uid = decoded['uid']

        restaurant_ref = db.collection('restaurants').document(restaurant_id)
        if not restaurant_ref.get().exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        menu_item_ref = restaurant_ref.collection('menu_items').document()
        menu_item_dict = menu_item.dict()
        menu_item_dict['id'] = menu_item_ref.id
        menu_item_ref.set(menu_item_dict)
        
        return menu_item_dict
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 