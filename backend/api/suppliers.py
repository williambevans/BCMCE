"""
BCMCE Suppliers API
Supplier management and inventory endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


# Enums
class SupplierStatus(str, Enum):
    """Supplier account status"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


# Pydantic Models
class Location(BaseModel):
    """Geographic location"""
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str
    city: str
    state: str = "TX"
    zip_code: str


class Supplier(BaseModel):
    """Supplier profile"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contact_name: str
    email: EmailStr
    phone: str
    location: Location
    txdot_certified: bool = False
    lat_certified: bool = False  # Lime Association of Texas
    delivery_radius_miles: int = 50
    status: SupplierStatus = SupplierStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MaterialInventory(BaseModel):
    """Material inventory item"""
    supplier_id: str
    material_code: str
    material_name: str
    quantity_available_tons: float
    price_per_ton: float
    quality_grade: str
    txdot_spec: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class InventoryUpdate(BaseModel):
    """Request to update inventory"""
    material_code: str
    quantity_available_tons: float = Field(ge=0)
    price_per_ton: float = Field(gt=0)
    quality_grade: str
    txdot_spec: Optional[str] = None


class PricingUpdate(BaseModel):
    """Request to update pricing"""
    material_code: str
    price_per_ton: float = Field(gt=0)
    effective_date: Optional[datetime] = None


class SupplierRegistration(BaseModel):
    """New supplier registration"""
    name: str
    contact_name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    zip_code: str
    latitude: float
    longitude: float
    txdot_certified: bool = False
    lat_certified: bool = False
    materials_offered: List[str]


# Mock data
MOCK_SUPPLIERS = [
    Supplier(
        id="supp-001",
        name="Clifton Quarry",
        contact_name="John Smith",
        email="john@cliftonquarry.com",
        phone="254-675-1234",
        location=Location(
            latitude=31.7813,
            longitude=-97.5778,
            address="123 Quarry Road",
            city="Clifton",
            state="TX",
            zip_code="76634"
        ),
        txdot_certified=True,
        status=SupplierStatus.ACTIVE
    ),
    Supplier(
        id="supp-002",
        name="Bosque River Pit",
        contact_name="Mary Johnson",
        email="mary@bosqueriver.com",
        phone="254-675-5678",
        location=Location(
            latitude=31.8000,
            longitude=-97.6000,
            address="456 River Road",
            city="Meridian",
            state="TX",
            zip_code="76665"
        ),
        txdot_certified=True,
        status=SupplierStatus.ACTIVE
    )
]

MOCK_INVENTORY = []


@router.get("", response_model=List[Supplier])
async def list_suppliers(
    status: Optional[SupplierStatus] = None,
    txdot_certified: Optional[bool] = None
):
    """
    List all suppliers

    Args:
        status: Filter by supplier status
        txdot_certified: Filter by TxDOT certification

    Returns:
        List of suppliers
    """
    logger.info(f"Listing suppliers: status={status}, txdot_certified={txdot_certified}")

    suppliers = MOCK_SUPPLIERS.copy()

    if status:
        suppliers = [s for s in suppliers if s.status == status]
    if txdot_certified is not None:
        suppliers = [s for s in suppliers if s.txdot_certified == txdot_certified]

    return suppliers


@router.post("/register", response_model=Supplier)
async def register_supplier(registration: SupplierRegistration):
    """
    Register a new supplier

    Args:
        registration: Supplier registration details

    Returns:
        Created supplier profile
    """
    logger.info(f"Registering new supplier: {registration.name}")

    supplier = Supplier(
        name=registration.name,
        contact_name=registration.contact_name,
        email=registration.email,
        phone=registration.phone,
        location=Location(
            latitude=registration.latitude,
            longitude=registration.longitude,
            address=registration.address,
            city=registration.city,
            state="TX",
            zip_code=registration.zip_code
        ),
        txdot_certified=registration.txdot_certified,
        lat_certified=registration.lat_certified,
        status=SupplierStatus.PENDING
    )

    MOCK_SUPPLIERS.append(supplier)

    logger.info(f"Supplier registered: {supplier.id}")
    return supplier


@router.get("/{supplier_id}", response_model=Supplier)
async def get_supplier(supplier_id: str):
    """
    Get supplier details

    Args:
        supplier_id: Supplier ID

    Returns:
        Supplier profile
    """
    logger.info(f"Fetching supplier: {supplier_id}")

    supplier = next((s for s in MOCK_SUPPLIERS if s.id == supplier_id), None)

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return supplier


@router.post("/{supplier_id}/inventory", response_model=MaterialInventory)
async def update_inventory(supplier_id: str, update: InventoryUpdate):
    """
    Update supplier inventory

    Args:
        supplier_id: Supplier ID
        update: Inventory update details

    Returns:
        Updated inventory item
    """
    logger.info(f"Updating inventory for supplier {supplier_id}: {update.material_code}")

    # Verify supplier exists
    supplier = next((s for s in MOCK_SUPPLIERS if s.id == supplier_id), None)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Create or update inventory item
    inventory = MaterialInventory(
        supplier_id=supplier_id,
        material_code=update.material_code,
        material_name="Road Base Gravel",  # Would lookup from materials table
        quantity_available_tons=update.quantity_available_tons,
        price_per_ton=update.price_per_ton,
        quality_grade=update.quality_grade,
        txdot_spec=update.txdot_spec
    )

    # In real implementation, would update database
    MOCK_INVENTORY.append(inventory)

    logger.info(f"Inventory updated: {supplier_id}/{update.material_code}")
    return inventory


@router.get("/{supplier_id}/inventory", response_model=List[MaterialInventory])
async def get_supplier_inventory(supplier_id: str):
    """
    Get all inventory for a supplier

    Args:
        supplier_id: Supplier ID

    Returns:
        List of inventory items
    """
    logger.info(f"Fetching inventory for supplier: {supplier_id}")

    inventory = [item for item in MOCK_INVENTORY if item.supplier_id == supplier_id]
    return inventory


@router.post("/{supplier_id}/pricing", response_model=dict)
async def update_pricing(supplier_id: str, update: PricingUpdate):
    """
    Update supplier pricing

    Args:
        supplier_id: Supplier ID
        update: Pricing update details

    Returns:
        Update confirmation
    """
    logger.info(f"Updating pricing for supplier {supplier_id}: {update.material_code}")

    # Verify supplier exists
    supplier = next((s for s in MOCK_SUPPLIERS if s.id == supplier_id), None)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # In real implementation, would update database and trigger pricing recalculation

    return {
        "status": "success",
        "message": "Pricing updated",
        "supplier_id": supplier_id,
        "material_code": update.material_code,
        "new_price": update.price_per_ton,
        "effective_date": update.effective_date or datetime.utcnow()
    }
