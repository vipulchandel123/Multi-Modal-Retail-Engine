from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional

router = APIRouter()

# Pydantic Schemas
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class OrderItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int

class CreateOrderRequest(BaseModel):
    username: str
    items: List[OrderItem]
    total_amount: float

# Mock In-Memory Databases
users_db = {
    "admin": {"email": "admin@example.com", "password": "secretrootpass"}
}

# Pre-populated Product Catalog
products_db = [
    {
        "id": 1,
        "name": "Wireless AI Headphones",
        "category": "Electronics",
        "price": 2999.0,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        "description": "Noise cancelling smart headphones with spatial audio."
    },
    {
        "id": 2,
        "name": "Smart Fitness Watch",
        "category": "Electronics",
        "price": 4499.0,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        "description": "Real-time health monitoring & heart rate tracker."
    },
    {
        "id": 3,
        "name": "Ergonomic Office Chair",
        "category": "Furniture",
        "price": 8999.0,
        "image": "https://images.unsplash.com/photo-1580481072645-022f9a6d1273?w=500",
        "description": "Mesh lumbar support chair for long work/coding sessions."
    },
    {
        "id": 4,
        "name": "Minimalist Ceramic Mug",
        "category": "Home & Kitchen",
        "price": 499.0,
        "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500",
        "description": "Matte finish ceramic coffee mug for desktop setups."
    }
]

orders_db = []

# --- AUTH ENDPOINTS ---
@router.post("/auth/signup")
def signup(user: UserSignup):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    users_db[user.username] = {"email": user.email, "password": user.password}
    return {"status": "success", "message": f"User '{user.username}' created!"}

@router.post("/auth/login")
def login(user: UserLogin):
    stored_user = users_db.get(user.username)
    if not stored_user or stored_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {
        "status": "success",
        "access_token": f"token_{user.username}",
        "username": user.username
    }

# --- PRODUCT ENDPOINTS ---
@router.get("/products")
def get_products():
    return {"status": "success", "products": products_db}

# --- ORDER ENDPOINTS ---
@router.post("/orders/create")
def create_order(order: CreateOrderRequest):
    order_id = f"ORD-{1000 + len(orders_db) + 1}"
    new_order = {
        "order_id": order_id,
        "username": order.username,
        "items": [item.dict() for item in order.items],
        "total_amount": order.total_amount,
        "status": "CONFIRMED"
    }
    orders_db.append(new_order)
    return {"status": "success", "message": "Order placed successfully!", "order": new_order}

@router.get("/orders/{username}")
def get_user_orders(username: str):
    user_orders = [o for o in orders_db if o["username"] == username]
    return {"status": "success", "orders": user_orders}