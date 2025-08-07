import threading
import uvicorn
import time
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Numeric, and_, or_, func
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime, timedelta, date
import uuid
import logging
from decimal import Decimal
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import io
import base64

# ----------------- Database Setup -----------------
DATABASE_URL = "sqlite:///clinic_inventory.db"  # For simplicity, using SQLite here; replace with PostgreSQL URL if needed

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------- Models -----------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String)
    role = Column(String, default="nurse")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    actions = relationship("InventoryLog", back_populates="user")
    purchase_orders = relationship("PurchaseOrder", back_populates="created_by_user")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("InventoryItem", back_populates="category_rel")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("InventoryItem", back_populates="supplier_rel")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String, index=True)
    generic_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    total_stock = Column(Integer, default=0)
    unit = Column(String)
    reorder_threshold = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=50)
    price = Column(Numeric(10, 2))
    cost_price = Column(Numeric(10, 2), nullable=True)
    type = Column(String, default="drug")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    controlled_substance = Column(Boolean, default=False)
    temperature_sensitive = Column(Boolean, default=False)
    storage_temp_min = Column(Integer, nullable=True)
    storage_temp_max = Column(Integer, nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    usage_rate = Column(Float, default=0.0)
    last_used = Column(DateTime, nullable=True)
    barcode = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_rel = relationship("Category", back_populates="items")
    supplier_rel = relationship("Supplier", back_populates="items")
    batches = relationship("Batch", back_populates="item")
    logs = relationship("InventoryLog", back_populates="item")
    usage_records = relationship("UsageRecord", back_populates="item")

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory.id"))
    batch_number = Column(String, index=True)
    expiry_date = Column(DateTime)
    quantity_received = Column(Integer)
    quantity_remaining = Column(Integer)
    cost_per_unit = Column(Numeric(10, 2))
    supplier_batch_number = Column(String, nullable=True)
    manufacture_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    item = relationship("InventoryItem", back_populates="batches")
    logs = relationship("InventoryLog", back_populates="batch")

class InventoryLog(Base):
    __tablename__ = "inventory_logs"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory.id"))
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    action_type = Column(String)  # ADD, USE, DELETE, ADJUST, EXPIRED
    quantity_change = Column(Integer)
    quantity_before = Column(Integer)
    quantity_after = Column(Integer)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    item = relationship("InventoryItem", back_populates="logs")
    batch = relationship("Batch", back_populates="logs")
    user = relationship("User", back_populates="actions")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="item")

class UsageRecord(Base):
    __tablename__ = "usage_records"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory.id"))
    batch_id = Column(Integer, ForeignKey("batches.id"))
    quantity_used = Column(Integer)
    patient_id = Column(String, nullable=True)
    prescription_number = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    used_by = Column(Integer, ForeignKey("users.id"))
    used_at = Column(DateTime, default=datetime.utcnow)
    item = relationship("InventoryItem", back_populates="usage_records")
    user = relationship("User")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # LOW_STOCK, EXPIRING, EXPIRED, REORDER
    item_id = Column(Integer, ForeignKey("inventory.id"))
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    message = Column(Text)
    severity = Column(String)  # LOW, MEDIUM, HIGH, CRITICAL
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Numeric(10, 2))
    status = Column(String, default="pending")  # pending, approved, ordered, received, cancelled
    notes = Column(Text, nullable=True)
    expected_delivery = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    supplier = relationship("Supplier", back_populates="purchase_orders")
    created_by_user = relationship("User", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="order")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"))
    item_id = Column(Integer, ForeignKey("inventory.id"))
    quantity_ordered = Column(Integer)
    quantity_received = Column(Integer, default=0)
    unit_price = Column(Numeric(10, 2))
    total_price = Column(Numeric(10, 2))
    order = relationship("PurchaseOrder", back_populates="items")
    item = relationship("InventoryItem", back_populates="purchase_order_items")


# ----------------- Pydantic Schemas -----------------
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    role: str = Field(default="nurse", pattern=r'^(admin|pharmacist|nurse|doctor)$')

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class BatchBase(BaseModel):
    batch_number: str = Field(..., min_length=1, max_length=50)
    expiry_date: date
    quantity_received: int = Field(..., gt=0)
    cost_per_unit: Decimal = Field(..., gt=0)
    manufacture_date: Optional[date] = None
    supplier_batch_number: Optional[str] = None

class BatchCreate(BatchBase):
    pass

class BatchResponse(BatchBase):
    id: int
    item_id: int
    quantity_remaining: int
    created_at: datetime
    class Config:
        from_attributes = True

class InventoryItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    brand: str = Field(..., min_length=1, max_length=100)
    generic_name: Optional[str] = None
    description: Optional[str] = None
    unit: str = Field(..., max_length=20)
    reorder_threshold: int = Field(default=10, ge=0)
    reorder_quantity: int = Field(default=50, ge=1)
    price: Decimal = Field(..., gt=0)
    cost_price: Optional[Decimal] = Field(None, gt=0)
    type: str = Field(default="drug", pattern=r'^(drug|medical_supply|equipment|vaccine)$')

    category_id: Optional[int] = None
    controlled_substance: bool = False
    temperature_sensitive: bool = False
    storage_temp_min: Optional[int] = None
    storage_temp_max: Optional[int] = None
    supplier_id: Optional[int] = None
    barcode: Optional[str] = None

class InventoryItemCreate(InventoryItemBase):
    initial_quantity: int = Field(..., gt=0)
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[Decimal] = None
    reorder_threshold: Optional[int] = None
    reorder_quantity: Optional[int] = None
    is_active: Optional[bool] = None

class InventoryItemResponse(InventoryItemBase):
    id: int
    total_stock: int
    usage_rate: float
    last_used: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    supplier: Optional[SupplierResponse] = None
    batches: List[BatchResponse] = []
    class Config:
        from_attributes = True

class UsageRecordCreate(BaseModel):
    item_id: int
    batch_id: Optional[int] = None
    quantity_used: int = Field(..., gt=0)
    patient_id: Optional[str] = None
    prescription_number: Optional[str] = None
    notes: Optional[str] = None

class UsageRecordResponse(UsageRecordCreate):
    id: int
    used_by: int
    used_at: datetime
    class Config:
        from_attributes = True

class InventoryLogCreate(BaseModel):
    item_id: int
    batch_id: Optional[int] = None
    action_type: str = Field(..., pattern=r'^(ADD|USE|DELETE|ADJUST|EXPIRED|DAMAGED)$')
    quantity_change: int
    quantity_before: int
    quantity_after: int
    notes: Optional[str] = None

class InventoryLogResponse(InventoryLogCreate):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    type: str
    item_id: int
    batch_id: Optional[int] = None
    message: str
    severity: str
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class PurchaseOrderItemCreate(BaseModel):
    item_id: int
    quantity_ordered: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)

class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    items: List[PurchaseOrderItemCreate]
    expected_delivery: Optional[date] = None
    notes: Optional[str] = None

class PurchaseOrderResponse(BaseModel):
    id: int
    order_number: str
    supplier: SupplierResponse
    total_amount: Decimal
    status: str
    items: List[PurchaseOrderItemCreate]
    notes: Optional[str] = None
    expected_delivery: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class InventoryReport(BaseModel):
    total_items: int
    total_value: Decimal
    low_stock_count: int
    expiring_count: int
    expired_count: int
    category_breakdown: Dict[str, int]
    supplier_breakdown: Dict[str, int]

class UsageTrend(BaseModel):
    item_name: str
    brand: str
    usage_count: int
    total_used: int
    average_daily_usage: float
    days_until_depletion: Optional[float]

class AIQuery(BaseModel):
    query: str = Field(..., min_length=3)

class AIResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Dict]
    suggested_actions: List[str]

# ----------------- Authentication -----------------
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(lambda: SessionLocal())):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return {"sub": username, "user_id": user.id, "role": user.role}

# ----------------- FastAPI App -----------------
app = FastAPI(title="Clinic Inventory Management System", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# ----------------- API Endpoints -----------------
@app.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(lambda: SessionLocal())):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.email and db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(lambda: SessionLocal())):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not db_user.is_active:
        raise HTTPException(status_code=401, detail="User account is disabled")
    access_token = create_access_token(data={"sub": db_user.username, "user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer", "user": db_user}

# (Other API endpoints would follow here, similar to backend/main.py)

# ----------------- Streamlit Frontend -----------------
import time

API_BASE_URL = "http://localhost:8000"

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
    def set_token(self, token: str):
        self.token = token
    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    def _handle_response(self, response):
        if response.status_code == 401:
            st.error("Authentication required. Please login again.")
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
        elif response.status_code == 422:
            st.error("Validation error. Please check your input.")
        elif not response.ok:
            st.error(f"API Error: {response.status_code} - {response.text}")
        return response
    def login(self, username, password):
        response = requests.post(f"{self.base_url}/auth/login", json={"username": username, "password": password})
        if response.ok:
            data = response.json()
            self.set_token(data["access_token"])
            return data
        return None
    def register(self, username, email, password, role="nurse"):
        response = requests.post(f"{self.base_url}/auth/register", json={"username": username, "email": email, "password": password, "role": role})
        return response
    # Other API client methods would be implemented similarly

api_client = APIClient(API_BASE_URL)

def login_page():
    st.title("🔐 Clinic Inventory Management System")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary"):
            if username and password:
                with st.spinner("Logging in..."):
                    result = api_client.login(username, password)
                    if result:
                        st.session_state.token = result["access_token"]
                        st.session_state.user = result["user"]
                        st.success("✅ Login successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
            else:
                st.warning("Please enter username and password")
    with tab2:
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_role = st.selectbox("Role", ["nurse", "pharmacist", "doctor", "admin"], key="reg_role")
        if st.button("Register", type="primary"):
            if reg_username and reg_password:
                with st.spinner("Registering..."):
                    response = api_client.register(reg_username, reg_email, reg_password, reg_role)
                    if response.ok:
                        st.success("✅ Registration successful! Please login.")
                        st.rerun()
                    else:
                        st.error(f"❌ Registration failed: {response.text}")
            else:
                st.warning("Please fill all required fields")

def main():
    st.set_page_config(page_title="Clinic Inventory Management", page_icon="🏥", layout="wide")
    if not st.session_state.token:
        login_page()
        return
    st.sidebar.title("🏥 Clinic Inventory")
    st.sidebar.write(f"Welcome, {st.session_state.user['username']}!")
    page = st.sidebar.selectbox("Navigate", ["Dashboard", "Inventory", "Alerts", "Reports", "AI Assistant"])
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()
    # Page routing (implement dashboard_page, inventory_page, etc. here)
    st.write(f"You selected {page}. Feature pages to be implemented here.")

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def run_streamlit():
    main()

if __name__ == "__main__":
    # Run FastAPI in a separate thread
    threading.Thread(target=run_fastapi, daemon=True).start()
    # Run Streamlit app
    run_streamlit()
