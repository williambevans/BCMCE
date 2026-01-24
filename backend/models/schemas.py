"""
Pydantic Models for Data Validation
Comprehensive schemas for all BCMCE entities
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class MaterialType(str, Enum):
    """Material type codes"""
    ROAD_BASE = "ROAD_BASE"
    CALICHE = "CALICHE"
    LIMESTONE = "LIMESTONE"
    HOT_MIX = "HOT_MIX"
    LIME_SLURRY = "LIME_SLURRY"
    P_GRAVEL = "P_GRAVEL"
    CONCRETE = "CONCRETE"
    CLAY = "CLAY"
    SAND = "SAND"
    TOPSOIL = "TOPSOIL"


class OptionDuration(str, Enum):
    """Option contract durations"""
    DAYS_30 = "30_DAYS"
    DAYS_90 = "90_DAYS"
    DAYS_180 = "180_DAYS"
    ANNUAL = "ANNUAL"


class OptionStatus(str, Enum):
    """Option contract statuses"""
    ACTIVE = "ACTIVE"
    EXERCISED = "EXERCISED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class OrderStatus(str, Enum):
    """Order statuses"""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class BidStatus(str, Enum):
    """Bid statuses"""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


# ============================================================================
# MATERIAL MODELS
# ============================================================================

class MaterialBase(BaseModel):
    """Base material model"""
    name: str = Field(..., min_length=1, max_length=200)
    material_type: MaterialType
    txdot_spec: Optional[str] = Field(None, max_length=100)
    unit: str = Field("ton", max_length=50)
    description: Optional[str] = None


class MaterialCreate(MaterialBase):
    """Create material"""
    pass


class Material(MaterialBase):
    """Material response model"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SUPPLIER MODELS
# ============================================================================

class SupplierBase(BaseModel):
    """Base supplier model"""
    name: str = Field(..., min_length=1, max_length=200)
    contact_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., max_length=20)
    address: str
    city: str = Field(..., max_length=100)
    state: str = Field("TX", max_length=2)
    zip_code: str = Field(..., max_length=10)
    is_active: bool = True


class SupplierCreate(SupplierBase):
    """Create supplier"""
    pass


class SupplierUpdate(BaseModel):
    """Update supplier"""
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class Supplier(SupplierBase):
    """Supplier response model"""
    id: int
    rating: Optional[Decimal] = None
    total_orders: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PRICING MODELS
# ============================================================================

class PricingBase(BaseModel):
    """Base pricing model"""
    supplier_id: int
    material_id: int
    spot_price: Decimal = Field(..., gt=0, decimal_places=2)
    minimum_order: Decimal = Field(..., gt=0)
    delivery_radius_miles: int = Field(..., gt=0)
    is_active: bool = True


class PricingCreate(PricingBase):
    """Create pricing"""
    pass


class PricingUpdate(BaseModel):
    """Update pricing"""
    spot_price: Optional[Decimal] = None
    minimum_order: Optional[Decimal] = None
    delivery_radius_miles: Optional[int] = None
    is_active: Optional[bool] = None


class Pricing(PricingBase):
    """Pricing response model"""
    id: int
    created_at: datetime
    updated_at: datetime
    supplier: Optional[Supplier] = None
    material: Optional[Material] = None

    class Config:
        from_attributes = True


class PricingWithHistory(Pricing):
    """Pricing with historical data"""
    price_change_24h: Optional[Decimal] = None
    price_change_7d: Optional[Decimal] = None
    price_change_30d: Optional[Decimal] = None


# ============================================================================
# OPTION CONTRACT MODELS
# ============================================================================

class OptionPriceBase(BaseModel):
    """Base option price model"""
    supplier_id: int
    material_id: int
    duration: OptionDuration
    strike_price: Decimal = Field(..., gt=0, decimal_places=2)
    premium: Decimal = Field(..., gt=0, decimal_places=2)


class OptionPriceCreate(OptionPriceBase):
    """Create option price"""
    pass


class OptionPrice(OptionPriceBase):
    """Option price response model"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OptionContractBase(BaseModel):
    """Base option contract model"""
    county_id: int
    option_price_id: int
    quantity: Decimal = Field(..., gt=0)
    purchase_date: date
    expiration_date: date
    status: OptionStatus = OptionStatus.ACTIVE


class OptionContractCreate(BaseModel):
    """Create option contract"""
    county_id: int
    supplier_id: int
    material_id: int
    duration: OptionDuration
    quantity: Decimal = Field(..., gt=0)

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v


class OptionContractExercise(BaseModel):
    """Exercise option contract"""
    delivery_date: date
    delivery_location: str
    notes: Optional[str] = None


class OptionContract(OptionContractBase):
    """Option contract response model"""
    id: int
    contract_number: str
    total_value: Decimal
    exercised_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    option_price: Optional[OptionPrice] = None

    class Config:
        from_attributes = True


# ============================================================================
# COUNTY MODELS
# ============================================================================

class CountyBase(BaseModel):
    """Base county model"""
    name: str = Field(..., min_length=1, max_length=200)
    state: str = Field("TX", max_length=2)
    contact_name: str
    contact_email: EmailStr
    contact_phone: str = Field(..., max_length=20)


class CountyCreate(CountyBase):
    """Create county"""
    pass


class County(CountyBase):
    """County response model"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# REQUIREMENT MODELS
# ============================================================================

class RequirementBase(BaseModel):
    """Base requirement model"""
    county_id: int
    material_id: int
    quantity: Decimal = Field(..., gt=0)
    needed_by_date: date
    delivery_location: str
    budget_code: str = Field(..., max_length=100)
    specifications: Optional[str] = None


class RequirementCreate(RequirementBase):
    """Create requirement"""
    project_name: str = Field(..., min_length=1, max_length=200)


class Requirement(RequirementBase):
    """Requirement response model"""
    id: int
    requirement_number: str
    project_name: str
    status: str = "OPEN"
    created_at: datetime
    updated_at: datetime
    material: Optional[Material] = None
    county: Optional[County] = None

    class Config:
        from_attributes = True


# ============================================================================
# BID MODELS
# ============================================================================

class BidBase(BaseModel):
    """Base bid model"""
    requirement_id: int
    supplier_id: int
    quoted_price: Decimal = Field(..., gt=0, decimal_places=2)
    quantity_available: Decimal = Field(..., gt=0)
    delivery_date: date
    notes: Optional[str] = None


class BidCreate(BidBase):
    """Create bid"""
    pass


class BidUpdate(BaseModel):
    """Update bid"""
    quoted_price: Optional[Decimal] = None
    quantity_available: Optional[Decimal] = None
    delivery_date: Optional[date] = None
    notes: Optional[str] = None


class Bid(BidBase):
    """Bid response model"""
    id: int
    bid_number: str
    status: BidStatus = BidStatus.SUBMITTED
    created_at: datetime
    updated_at: datetime
    supplier: Optional[Supplier] = None

    class Config:
        from_attributes = True


# ============================================================================
# ORDER MODELS
# ============================================================================

class OrderBase(BaseModel):
    """Base order model"""
    county_id: int
    supplier_id: int
    material_id: int
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    total_amount: Decimal = Field(..., gt=0, decimal_places=2)
    delivery_location: str
    delivery_date: date


class OrderCreate(BaseModel):
    """Create order"""
    county_id: int
    bid_id: Optional[int] = None
    option_contract_id: Optional[int] = None
    delivery_location: str
    delivery_date: date
    notes: Optional[str] = None


class Order(OrderBase):
    """Order response model"""
    id: int
    order_number: str
    status: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = None
    fulfilled_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    supplier: Optional[Supplier] = None
    material: Optional[Material] = None

    class Config:
        from_attributes = True


# ============================================================================
# BUDGET MODELS
# ============================================================================

class BudgetBase(BaseModel):
    """Base budget model"""
    county_id: int
    fiscal_year: int = Field(..., ge=2020, le=2100)
    quarter: Optional[int] = Field(None, ge=1, le=4)
    category: str = Field(..., max_length=100)
    allocated_amount: Decimal = Field(..., gt=0, decimal_places=2)


class BudgetCreate(BudgetBase):
    """Create budget"""
    pass


class Budget(BudgetBase):
    """Budget response model"""
    id: int
    spent_amount: Decimal = Decimal("0.00")
    committed_amount: Decimal = Decimal("0.00")
    remaining_amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class PriceComparison(BaseModel):
    """Price comparison for a material"""
    material_id: int
    material_name: str
    suppliers: List[dict]  # List of {supplier_id, supplier_name, price, rating}
    lowest_price: Decimal
    highest_price: Decimal
    average_price: Decimal


class MarketOverview(BaseModel):
    """Market overview statistics"""
    total_suppliers: int
    total_materials: int
    active_options: int
    pending_orders: int
    daily_volume: Decimal
    price_trends: dict  # Material-wise price trends


class SupplierPerformance(BaseModel):
    """Supplier performance metrics"""
    supplier_id: int
    supplier_name: str
    total_orders: int
    fulfilled_orders: int
    fulfillment_rate: Decimal
    average_rating: Decimal
    total_revenue: Decimal
    on_time_delivery_rate: Decimal


class CountySpending(BaseModel):
    """County spending analysis"""
    county_id: int
    county_name: str
    fiscal_year: int
    total_budget: Decimal
    total_spent: Decimal
    total_committed: Decimal
    remaining: Decimal
    spending_by_material: dict
    cost_savings: Decimal


# ============================================================================
# NOTIFICATION MODELS
# ============================================================================

class NotificationBase(BaseModel):
    """Base notification model"""
    recipient_email: EmailStr
    subject: str = Field(..., min_length=1, max_length=200)
    message: str
    notification_type: str = Field(..., max_length=50)


class NotificationCreate(NotificationBase):
    """Create notification"""
    pass


class Notification(NotificationBase):
    """Notification response model"""
    id: int
    sent: bool = False
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AUTHENTICATION MODELS
# ============================================================================

class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., max_length=50)  # "supplier", "county", "admin"


class UserCreate(UserBase):
    """Create user"""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login"""
    email: EmailStr
    password: str


class User(UserBase):
    """User response model"""
    id: int
    is_active: bool = True
    supplier_id: Optional[int] = None
    county_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token data for validation"""
    user_id: int
    email: str
    role: str


# ============================================================================
# SCRAPED BID MODELS
# ============================================================================

class ScrapedBidBase(BaseModel):
    """Base scraped bid model"""
    county_name: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=500)
    url: Optional[str] = None
    description: Optional[str] = None
    date_posted: Optional[str] = None
    deadline: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    section: Optional[str] = None


class ScrapedBidCreate(ScrapedBidBase):
    """Create scraped bid"""
    pass


class ScrapedBid(ScrapedBidBase):
    """Scraped bid response model"""
    id: str
    is_processed: bool = False
    scraped_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScrapeSummary(BaseModel):
    """Summary of scraping operation"""
    county_name: str
    total_bids: int
    new_bids: int
    failed: bool = False
    error_message: Optional[str] = None
    scraped_at: datetime


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    details: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """Paginated list response"""
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
