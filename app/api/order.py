from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import firestore
from app.dto.order import Order, OrderStatus
from app.api.firebase_authentication import verify_firebase_token, verify_admin
from datetime import datetime
from typing import List
import jwt

router = APIRouter(
    prefix="/orders",
    tags=["Order"]
)
db = firestore.client()

security = HTTPBearer()

@router.post("/",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="Create a new food order for a specific restaurant."
)
async def create_order(
    order: Order,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    decoded = jwt.decode(token, options={"verify_signature": False})
    is_custom_token = 'uid' in decoded and 'claims' in decoded

    if is_custom_token:
            role = decoded['claims']['role']
            uid = decoded['uid']
    else:
            role = decoded['role']
            uid = decoded['uid']


    # Validate restaurant exists
    restaurant_ref = db.collection('restaurants').document(order.restaurant_id)
    if not restaurant_ref.get().exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    # Create order
    order_dict = order.dict()
    order_dict['user_id'] = uid
    order_dict['total'] = sum(item['price'] * item['quantity'] for item in order_dict['items'])
    order_dict['created_at'] = datetime.utcnow()
    order_dict['updated_at'] = datetime.utcnow()

    doc_ref = db.collection('orders').document()
    order_dict['id'] = doc_ref.id
    doc_ref.set(order_dict)

    return order_dict

@router.get("/history",
    response_model=List[Order],
    summary="Get order history",
    description="Get the authenticated user's order history."
)
async def get_order_history(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, options={"verify_signature": False})
        is_custom_token = 'uid' in decoded and 'claims' in decoded

        if is_custom_token:
            uid = decoded['uid']
        else:
            uid = decoded['uid']

        orders = []
        query = (db.collection('orders')
                .where('user_id', '==', uid))
                # .order_by('created_at', direction=firestore.Query.DESCENDING))
        
        for doc in query.stream():
            orders.append(doc.to_dict())
            
        return orders
    except Exception as e:
        if "requires an index" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The query requires an index. Please create it in the Firebase console."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

@router.put("/{order_id}/status",
    response_model=dict,
    summary="Update order status",
    description="Update the status of an order. Only admin users can perform this operation."
)
async def update_order_status(
    order_id: str,
    status: OrderStatus,
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

        doc_ref = db.collection('orders').document(order_id)
        if not doc_ref.get().exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        doc_ref.update({
            'status': status,
            'updated_at': datetime.utcnow()
        })
        
        return {"message": "Order status updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )