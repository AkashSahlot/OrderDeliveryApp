from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore
from app.dto.order import Order, OrderStatus
from app.api.firebase_authentication import verify_firebase_token, verify_admin
from datetime import datetime
from typing import List

router = APIRouter(
    prefix="/orders",
    tags=["Order"]
)
db = firestore.client()

@router.post("/",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="Create a new food order for a specific restaurant."
)
async def create_order(
    order: Order,
    # token_data: dict = Depends(verify_firebase_token)
):
    # Validate restaurant exists
    restaurant_ref = db.collection('restaurants').document(order.restaurant_id)
    if not restaurant_ref.get().exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )

    # Create order
    order_dict = order.dict()
    order_dict['user_id'] = token_data['uid']
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
    token_data: dict = Depends(verify_firebase_token)
):
    try:
        orders = []
        query = (db.collection('orders')
                .where('user_id', '==', token_data['uid'])
                .order_by('created_at', direction=firestore.Query.DESCENDING))
        
        for doc in query.stream():
            orders.append(doc.to_dict())
            
        return orders
    except Exception as e:
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
    token_data: dict = Depends(verify_admin)
):
    try:
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