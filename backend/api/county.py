"""
BCMCE County Integration API
County procurement and bid management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


# Enums
class RequirementStatus(str, Enum):
    """County requirement status"""
    OPEN = "open"
    BIDDING = "bidding"
    AWARDED = "awarded"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class BidStatus(str, Enum):
    """Bid submission status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# Pydantic Models
class CountyRequirement(BaseModel):
    """County material requirement/RFP"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    county_name: str = "Bosque County"
    precinct: Optional[int] = None
    material_code: str
    material_name: str
    quantity_tons: float
    delivery_location: str
    delivery_latitude: float
    delivery_longitude: float
    required_by_date: date
    budget_allocated: float
    txdot_spec_required: Optional[str] = None
    special_requirements: Optional[str] = None
    status: RequirementStatus = RequirementStatus.OPEN
    posted_at: datetime = Field(default_factory=datetime.utcnow)
    bid_deadline: datetime


class BidSubmission(BaseModel):
    """Bid submission to county"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requirement_id: str
    supplier_id: str
    supplier_name: str
    material_code: str
    quantity_tons: float
    price_per_ton: float
    total_price: float
    delivery_date: date
    delivery_method: str = "Supplier Delivery"
    payment_terms: str = "Net 30"
    txdot_certified: bool
    insurance_certificate: bool = True
    performance_bond: bool = False
    notes: Optional[str] = None
    status: BidStatus = BidStatus.PENDING
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class BidRequest(BaseModel):
    """Request to submit a bid"""
    requirement_id: str
    supplier_id: str
    supplier_name: str
    quantity_tons: float = Field(gt=0)
    price_per_ton: float = Field(gt=0)
    delivery_date: date
    delivery_method: str = "Supplier Delivery"
    payment_terms: str = "Net 30"
    notes: Optional[str] = None


class CountyBudget(BaseModel):
    """County budget tracking"""
    county_name: str = "Bosque County"
    fiscal_year: int
    total_budget: float
    allocated: float
    spent: float
    committed: float  # Option contracts
    available: float
    by_material: dict


# Mock data
MOCK_REQUIREMENTS = [
    CountyRequirement(
        id="req-001",
        precinct=1,
        material_code="GRVL-RB",
        material_name="Road Base Gravel",
        quantity_tons=500.0,
        delivery_location="FM 219 at County Road 1740",
        delivery_latitude=31.7813,
        delivery_longitude=-97.5778,
        required_by_date=date(2026, 2, 15),
        budget_allocated=15000.00,
        txdot_spec_required="Type A",
        status=RequirementStatus.OPEN,
        bid_deadline=datetime(2026, 1, 31, 17, 0, 0)
    ),
    CountyRequirement(
        id="req-002",
        precinct=3,
        material_code="CALC-STD",
        material_name="Caliche",
        quantity_tons=300.0,
        delivery_location="County Road 3320",
        delivery_latitude=31.8200,
        delivery_longitude=-97.6100,
        required_by_date=date(2026, 2, 28),
        budget_allocated=14000.00,
        status=RequirementStatus.OPEN,
        bid_deadline=datetime(2026, 2, 7, 17, 0, 0)
    )
]

MOCK_BIDS = []


@router.get("/requirements", response_model=List[CountyRequirement])
async def get_county_requirements(
    status: Optional[RequirementStatus] = None,
    material_code: Optional[str] = None
):
    """
    Get all county material requirements

    Args:
        status: Filter by requirement status
        material_code: Filter by material

    Returns:
        List of county requirements
    """
    logger.info(f"Fetching county requirements: status={status}, material={material_code}")

    requirements = MOCK_REQUIREMENTS.copy()

    if status:
        requirements = [r for r in requirements if r.status == status]
    if material_code:
        requirements = [r for r in requirements if r.material_code == material_code]

    return requirements


@router.get("/requirements/{requirement_id}", response_model=CountyRequirement)
async def get_requirement_details(requirement_id: str):
    """
    Get details of a specific requirement

    Args:
        requirement_id: Requirement ID

    Returns:
        Requirement details
    """
    logger.info(f"Fetching requirement: {requirement_id}")

    requirement = next((r for r in MOCK_REQUIREMENTS if r.id == requirement_id), None)

    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    return requirement


@router.post("/bids/submit", response_model=BidSubmission)
async def submit_bid(bid_request: BidRequest):
    """
    Submit a bid to a county requirement

    Args:
        bid_request: Bid submission details

    Returns:
        Created bid submission
    """
    logger.info(f"Processing bid submission: {bid_request.requirement_id}")

    # Verify requirement exists and is open
    requirement = next(
        (r for r in MOCK_REQUIREMENTS if r.id == bid_request.requirement_id),
        None
    )

    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    if requirement.status != RequirementStatus.OPEN:
        raise HTTPException(status_code=400, detail="Requirement is not open for bidding")

    if datetime.utcnow() > requirement.bid_deadline:
        raise HTTPException(status_code=400, detail="Bid deadline has passed")

    # Create bid submission
    bid = BidSubmission(
        requirement_id=bid_request.requirement_id,
        supplier_id=bid_request.supplier_id,
        supplier_name=bid_request.supplier_name,
        material_code=requirement.material_code,
        quantity_tons=bid_request.quantity_tons,
        price_per_ton=bid_request.price_per_ton,
        total_price=bid_request.quantity_tons * bid_request.price_per_ton,
        delivery_date=bid_request.delivery_date,
        delivery_method=bid_request.delivery_method,
        payment_terms=bid_request.payment_terms,
        txdot_certified=True,  # Would lookup from supplier profile
        notes=bid_request.notes
    )

    MOCK_BIDS.append(bid)

    logger.info(f"Bid submitted: {bid.id}")
    return bid


@router.get("/bids", response_model=List[BidSubmission])
async def get_bids(
    requirement_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    status: Optional[BidStatus] = None
):
    """
    Get bid submissions

    Args:
        requirement_id: Filter by requirement
        supplier_id: Filter by supplier
        status: Filter by bid status

    Returns:
        List of bid submissions
    """
    logger.info(f"Fetching bids: req={requirement_id}, supplier={supplier_id}, status={status}")

    bids = MOCK_BIDS.copy()

    if requirement_id:
        bids = [b for b in bids if b.requirement_id == requirement_id]
    if supplier_id:
        bids = [b for b in bids if b.supplier_id == supplier_id]
    if status:
        bids = [b for b in bids if b.status == status]

    return bids


@router.get("/budget", response_model=CountyBudget)
async def get_county_budget(fiscal_year: int = 2026):
    """
    Get county budget information

    Args:
        fiscal_year: Fiscal year

    Returns:
        County budget summary
    """
    logger.info(f"Fetching county budget for FY{fiscal_year}")

    # Mock budget data
    total_budget = 500000.00
    allocated = 187500.00
    spent = 87500.00
    committed = 35000.00

    return CountyBudget(
        fiscal_year=fiscal_year,
        total_budget=total_budget,
        allocated=allocated,
        spent=spent,
        committed=committed,
        available=total_budget - allocated,
        by_material={
            "GRVL-RB": {"allocated": 75000, "spent": 32000, "committed": 15000},
            "CALC-STD": {"allocated": 45000, "spent": 18000, "committed": 10000},
            "LIME-SLR": {"allocated": 35000, "spent": 22500, "committed": 8000},
            "FLEX-12": {"allocated": 32500, "spent": 15000, "committed": 2000}
        }
    )


@router.post("/requirements", response_model=CountyRequirement)
async def create_requirement(requirement: CountyRequirement):
    """
    Create a new county requirement (County use only)

    Args:
        requirement: Requirement details

    Returns:
        Created requirement
    """
    logger.info(f"Creating county requirement: {requirement.material_code}")

    # In production, this would require county authentication
    MOCK_REQUIREMENTS.append(requirement)

    logger.info(f"Requirement created: {requirement.id}")
    return requirement
