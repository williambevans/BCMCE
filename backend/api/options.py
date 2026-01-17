"""
BCMCE Options API
Option contract management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


# Enums
class OptionStatus(str, Enum):
    """Option contract status"""
    ACTIVE = "active"
    EXERCISED = "exercised"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class OptionDuration(int, Enum):
    """Standard option durations in days"""
    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_180 = 180
    DAYS_365 = 365


# Pydantic Models
class OptionContract(BaseModel):
    """Option contract data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    material_code: str
    material_name: str
    supplier_id: str
    supplier_name: str
    buyer_id: str
    strike_price: float
    quantity_tons: float
    premium_paid: float
    duration_days: int
    status: OptionStatus = OptionStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    exercised_at: Optional[datetime] = None


class OptionPurchaseRequest(BaseModel):
    """Request to purchase an option contract"""
    material_code: str
    quantity_tons: float = Field(gt=0, description="Quantity in tons")
    duration_days: int = Field(description="Option duration (30, 90, 180, or 365 days)")
    buyer_id: str
    buyer_name: str
    buyer_email: str


class OptionExerciseRequest(BaseModel):
    """Request to exercise an option contract"""
    option_id: str
    delivery_location: str
    delivery_date: datetime
    notes: Optional[str] = None


class AvailableOption(BaseModel):
    """Available option contract offering"""
    material_code: str
    material_name: str
    supplier_id: str
    supplier_name: str
    duration_days: int
    strike_price: float
    premium_percentage: float
    total_price: float
    available_quantity_tons: float
    min_quantity_tons: float = 10.0
    delivery_radius_miles: int = 50


# Mock data
MOCK_OPTIONS = []


@router.get("/available", response_model=List[AvailableOption])
async def get_available_options(
    material_code: Optional[str] = None,
    duration_days: Optional[int] = None
):
    """
    Get available option contracts

    Args:
        material_code: Filter by specific material
        duration_days: Filter by option duration

    Returns:
        List of available option contracts
    """
    logger.info(f"Fetching available options: material={material_code}, duration={duration_days}")

    # Mock available options
    options = [
        AvailableOption(
            material_code="GRVL-RB",
            material_name="Road Base Gravel",
            supplier_id="supp-001",
            supplier_name="Clifton Quarry",
            duration_days=30,
            strike_price=28.50,
            premium_percentage=8.0,
            total_price=30.78,
            available_quantity_tons=500.0,
            min_quantity_tons=10.0,
            delivery_radius_miles=50
        ),
        AvailableOption(
            material_code="GRVL-RB",
            material_name="Road Base Gravel",
            supplier_id="supp-001",
            supplier_name="Clifton Quarry",
            duration_days=90,
            strike_price=28.50,
            premium_percentage=12.0,
            total_price=31.92,
            available_quantity_tons=500.0,
            min_quantity_tons=10.0,
            delivery_radius_miles=50
        ),
        AvailableOption(
            material_code="CALC-STD",
            material_name="Caliche",
            supplier_id="supp-002",
            supplier_name="Bosque River Pit",
            duration_days=30,
            strike_price=45.00,
            premium_percentage=8.0,
            total_price=48.60,
            available_quantity_tons=300.0,
            min_quantity_tons=15.0,
            delivery_radius_miles=40
        ),
    ]

    # Apply filters
    if material_code:
        options = [o for o in options if o.material_code == material_code]
    if duration_days:
        options = [o for o in options if o.duration_days == duration_days]

    return options


@router.post("/purchase", response_model=OptionContract)
async def purchase_option(request: OptionPurchaseRequest):
    """
    Purchase an option contract

    Args:
        request: Option purchase request details

    Returns:
        Created option contract
    """
    logger.info(f"Processing option purchase: {request.material_code}, {request.quantity_tons} tons")

    # Validate duration
    valid_durations = [30, 90, 180, 365]
    if request.duration_days not in valid_durations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid duration. Must be one of: {valid_durations}"
        )

    # Mock pricing calculation
    base_price = 28.50  # This would come from the pricing service
    premium_rates = {30: 1.08, 90: 1.12, 180: 1.15, 365: 1.20}
    strike_price = base_price
    total_price = base_price * premium_rates[request.duration_days]
    premium = (total_price - base_price) * request.quantity_tons

    # Create option contract
    contract = OptionContract(
        material_code=request.material_code,
        material_name="Road Base Gravel",  # Would lookup from DB
        supplier_id="supp-001",
        supplier_name="Clifton Quarry",
        buyer_id=request.buyer_id,
        strike_price=strike_price,
        quantity_tons=request.quantity_tons,
        premium_paid=round(premium, 2),
        duration_days=request.duration_days,
        expires_at=datetime.utcnow() + timedelta(days=request.duration_days)
    )

    MOCK_OPTIONS.append(contract)

    logger.info(f"Option contract created: {contract.id}")
    return contract


@router.get("/holdings", response_model=List[OptionContract])
async def get_option_holdings(buyer_id: str):
    """
    Get all option contracts for a buyer

    Args:
        buyer_id: Buyer identifier

    Returns:
        List of option contracts owned by the buyer
    """
    logger.info(f"Fetching option holdings for buyer: {buyer_id}")

    holdings = [opt for opt in MOCK_OPTIONS if opt.buyer_id == buyer_id]
    return holdings


@router.post("/exercise", response_model=dict)
async def exercise_option(request: OptionExerciseRequest):
    """
    Exercise an option contract

    Args:
        request: Exercise request details

    Returns:
        Exercise confirmation
    """
    logger.info(f"Processing option exercise: {request.option_id}")

    # Find the option
    option = next((opt for opt in MOCK_OPTIONS if opt.id == request.option_id), None)

    if not option:
        raise HTTPException(status_code=404, detail="Option contract not found")

    if option.status != OptionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Option is not active")

    if datetime.utcnow() > option.expires_at:
        raise HTTPException(status_code=400, detail="Option has expired")

    # Update option status
    option.status = OptionStatus.EXERCISED
    option.exercised_at = datetime.utcnow()

    logger.info(f"Option exercised successfully: {option.id}")

    return {
        "status": "success",
        "message": "Option exercised successfully",
        "option_id": option.id,
        "delivery_scheduled": request.delivery_date,
        "total_cost": option.strike_price * option.quantity_tons
    }


@router.get("/{option_id}", response_model=OptionContract)
async def get_option_details(option_id: str):
    """
    Get details of a specific option contract

    Args:
        option_id: Option contract ID

    Returns:
        Option contract details
    """
    logger.info(f"Fetching option details: {option_id}")

    option = next((opt for opt in MOCK_OPTIONS if opt.id == option_id), None)

    if not option:
        raise HTTPException(status_code=404, detail="Option contract not found")

    return option
