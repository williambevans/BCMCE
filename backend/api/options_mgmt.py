"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██╗  ██╗    ██╗  ██╗          ██╗  ██╗ ██████╗ ██╗     ██████╗ ██╗███╗   ██╗ ██████╗ ███████╗  ║
║   ██║  ██║    ██║  ██║          ██║  ██║██╔═══██╗██║     ██╔══██╗██║████╗  ██║██╔════╝ ██╔════╝  ║
║   ███████║    ███████║          ███████║██║   ██║██║     ██║  ██║██║██╔██╗ ██║██║  ███╗███████╗  ║
║   ██╔══██║    ██╔══██║          ██╔══██║██║   ██║██║     ██║  ██║██║██║╚██╗██║██║   ██║╚════██║  ║
║   ██║  ██║    ██║  ██║          ██║  ██║╚██████╔╝███████╗██████╔╝██║██║ ╚████║╚██████╔╝███████║  ║
║   ╚═╝  ╚═╝    ╚═╝  ╚═╝          ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝  ║
║                                                                           ║
║                 BOSQUE COUNTY MINERAL & COMMODITIES EXCHANGE             ║
║                     Options Management API Endpoints                     ║
║                                                                           ║
║   Operator:    HH Holdings LLC / Bevans Real Estate                      ║
║   Location:    397 Highway 22, Clifton, TX 76634                         ║
║   Broker:      Biri Bevans, Designated Broker                            ║
║   Module:      Options Contract Management API                           ║
║                                                                           ║
║   Copyright:   © 2026 HH Holdings LLC. All rights reserved.              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

BCMCE Platform - Options Management API
H.H. Holdings internal options portfolio management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db, OptionContract as OptionContractModel, Material, Supplier
from auth import get_current_user
from database import User as UserModel

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# Pydantic Models
class OptionContractCreate(BaseModel):
    """Create new option contract (after phone deal with supplier)"""
    material_id: str
    supplier_id: str
    strike_price: float = Field(gt=0, description="Locked price per ton")
    quantity: float = Field(gt=0, description="Quantity in tons")
    premium: float = Field(ge=0, description="Premium paid upfront")
    duration_days: int = Field(gt=0, le=365, description="Days until expiry")
    notes: Optional[str] = None


class OptionContractResponse(BaseModel):
    """Option contract response"""
    id: str
    material_name: str
    supplier_name: str
    strike_price: float
    quantity: float
    premium: float
    cost_basis: float  # strike_price + (premium / quantity)
    days_until_expiry: int
    expires_at: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


class PortfolioStats(BaseModel):
    """Portfolio statistics"""
    active_options: int
    total_locked_value: float
    total_capacity: float
    expiring_soon: int  # Expiring in 7 days
    total_premium_paid: float


class BidCalculation(BaseModel):
    """Bid calculation request"""
    option_id: str
    quantity_needed: float
    target_margin: float = Field(default=3.0, description="Target profit margin per ton")


class BidCalculationResponse(BaseModel):
    """Bid calculation result"""
    option_id: str
    material_name: str
    strike_price: float
    premium_per_ton: float
    cost_basis: float
    quantity_needed: float
    target_margin: float
    calculated_bid: float
    total_bid_amount: float
    potential_profit: float


@router.get("/portfolio", response_model=List[OptionContractResponse])
async def get_portfolio(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get H.H. Holdings option portfolio

    Returns all active options owned by H.H. Holdings.
    Includes calculated cost basis and days until expiry.
    """
    try:
        # Get all option contracts
        options = db.query(OptionContractModel).filter(
            OptionContractModel.status == 'ACTIVE'
        ).all()

        response_options = []
        for option in options:
            # Get material and supplier names
            material = db.query(Material).filter(Material.id == option.material_id).first()
            supplier = db.query(Supplier).filter(Supplier.id == option.supplier_id).first()

            # Calculate cost basis
            premium_per_ton = float(option.premium_paid) / float(option.quantity) if option.quantity > 0 else 0
            cost_basis = float(option.strike_price) + premium_per_ton

            # Calculate days until expiry
            days_until_expiry = (option.expiry_date - datetime.utcnow()).days

            response_options.append(OptionContractResponse(
                id=str(option.id),
                material_name=material.name if material else "Unknown",
                supplier_name=supplier.name if supplier else "Unknown",
                strike_price=float(option.strike_price),
                quantity=float(option.quantity),
                premium=float(option.premium_paid),
                cost_basis=cost_basis,
                days_until_expiry=max(0, days_until_expiry),
                expires_at=option.expiry_date.isoformat(),
                status=option.status,
                created_at=option.created_at.isoformat()
            ))

        return response_options

    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching portfolio: {str(e)}"
        )


@router.get("/stats", response_model=PortfolioStats)
async def get_portfolio_stats(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio statistics

    Returns aggregate stats for H.H. Holdings option portfolio.
    """
    try:
        active_options = db.query(OptionContractModel).filter(
            OptionContractModel.status == 'ACTIVE'
        ).all()

        total_locked_value = sum(float(opt.strike_price) * float(opt.quantity) for opt in active_options)
        total_capacity = sum(float(opt.quantity) for opt in active_options)
        total_premium_paid = sum(float(opt.premium_paid) for opt in active_options)

        # Count expiring soon (within 7 days)
        seven_days = datetime.utcnow() + timedelta(days=7)
        expiring_soon = sum(
            1 for opt in active_options
            if opt.expiry_date <= seven_days
        )

        return PortfolioStats(
            active_options=len(active_options),
            total_locked_value=total_locked_value,
            total_capacity=total_capacity,
            expiring_soon=expiring_soon,
            total_premium_paid=total_premium_paid
        )

    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating stats: {str(e)}"
        )


@router.post("/create", response_model=OptionContractResponse, status_code=status.HTTP_201_CREATED)
async def create_option(
    option_data: OptionContractCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new option contract

    Use this after completing a phone deal with a supplier.
    Records the option contract in H.H. Holdings portfolio.

    **Example:**
    After calling Clifton Quarry and agreeing to:
    - 500 tons of Road Base Gravel
    - Strike price: $28.50/ton
    - Premium: $1,000 for 90 days

    Create the option to track it in your portfolio.
    """
    try:
        # Verify material exists
        material = db.query(Material).filter(Material.id == option_data.material_id).first()
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Material not found: {option_data.material_id}"
            )

        # Verify supplier exists
        supplier = db.query(Supplier).filter(Supplier.id == option_data.supplier_id).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier not found: {option_data.supplier_id}"
            )

        # Calculate expiry date
        expiry_date = datetime.utcnow() + timedelta(days=option_data.duration_days)

        # Create option contract
        new_option = OptionContractModel(
            material_id=option_data.material_id,
            supplier_id=option_data.supplier_id,
            strike_price=Decimal(str(option_data.strike_price)),
            quantity=Decimal(str(option_data.quantity)),
            premium_paid=Decimal(str(option_data.premium)),
            expiry_date=expiry_date,
            status='ACTIVE',
            created_at=datetime.utcnow()
        )

        db.add(new_option)
        db.commit()
        db.refresh(new_option)

        # Calculate cost basis
        premium_per_ton = option_data.premium / option_data.quantity
        cost_basis = option_data.strike_price + premium_per_ton

        logger.info(
            f"Option created: {material.name} - {option_data.quantity} tons "
            f"@ ${option_data.strike_price} from {supplier.name} by {current_user.email}"
        )

        return OptionContractResponse(
            id=str(new_option.id),
            material_name=material.name,
            supplier_name=supplier.name,
            strike_price=float(new_option.strike_price),
            quantity=float(new_option.quantity),
            premium=float(new_option.premium_paid),
            cost_basis=cost_basis,
            days_until_expiry=option_data.duration_days,
            expires_at=new_option.expiry_date.isoformat(),
            status=new_option.status,
            created_at=new_option.created_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating option: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating option: {str(e)}"
        )


@router.post("/calculate-bid", response_model=BidCalculationResponse)
async def calculate_bid(
    bid_calc: BidCalculation,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate competitive bid using option cost basis

    Uses your locked-in option price to calculate a competitive bid.
    Formula: (Strike Price + Premium/Ton + Target Margin) × Quantity

    **Example:**
    County needs 500 tons of Road Base Gravel.
    You have option: Strike $28.50, Premium $1,000 (500 tons) = $2/ton
    Cost basis: $28.50 + $2.00 = $30.50/ton
    Target margin: $3.00/ton
    Bid: $33.50/ton × 500 = $16,750
    Potential profit: $3.00 × 500 = $1,500
    """
    try:
        # Get option contract
        option = db.query(OptionContractModel).filter(
            OptionContractModel.id == bid_calc.option_id
        ).first()

        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Option contract not found"
            )

        if option.status != 'ACTIVE':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Option is {option.status}, cannot use for bidding"
            )

        # Check if option has enough quantity
        if bid_calc.quantity_needed > float(option.quantity):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Option only has {option.quantity} tons, need {bid_calc.quantity_needed}"
            )

        # Get material name
        material = db.query(Material).filter(Material.id == option.material_id).first()

        # Calculate bid
        strike_price = float(option.strike_price)
        premium_per_ton = float(option.premium_paid) / float(option.quantity)
        cost_basis = strike_price + premium_per_ton
        calculated_bid = cost_basis + bid_calc.target_margin
        total_bid_amount = calculated_bid * bid_calc.quantity_needed
        potential_profit = bid_calc.target_margin * bid_calc.quantity_needed

        logger.info(
            f"Bid calculated for {material.name if material else 'Unknown'}: "
            f"{bid_calc.quantity_needed} tons @ ${calculated_bid:.2f}/ton = ${total_bid_amount:.2f}"
        )

        return BidCalculationResponse(
            option_id=str(option.id),
            material_name=material.name if material else "Unknown",
            strike_price=strike_price,
            premium_per_ton=premium_per_ton,
            cost_basis=cost_basis,
            quantity_needed=bid_calc.quantity_needed,
            target_margin=bid_calc.target_margin,
            calculated_bid=calculated_bid,
            total_bid_amount=total_bid_amount,
            potential_profit=potential_profit
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating bid: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating bid: {str(e)}"
        )


@router.get("/materials", response_model=List[dict])
async def get_materials(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available materials for options"""
    try:
        materials = db.query(Material).all()
        return [
            {
                "id": str(m.id),
                "name": m.name,
                "material_type": m.material_type,
                "unit": m.unit
            }
            for m in materials
        ]
    except Exception as e:
        logger.error(f"Error fetching materials: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching materials: {str(e)}"
        )


@router.get("/suppliers", response_model=List[dict])
async def get_suppliers(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active suppliers for options"""
    try:
        suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()
        return [
            {
                "id": str(s.id),
                "name": s.name,
                "contact_name": s.contact_name,
                "phone": s.phone,
                "city": s.city
            }
            for s in suppliers
        ]
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching suppliers: {str(e)}"
        )
