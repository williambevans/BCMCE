"""
BCMCE Pricing API
Real-time commodity pricing endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic Models
class PricePoint(BaseModel):
    """Single price data point"""
    timestamp: datetime
    price: float
    supplier_id: Optional[str] = None


class CommodityPrice(BaseModel):
    """Current commodity pricing"""
    commodity_code: str
    commodity_name: str
    spot_price: float
    option_30d: float
    option_90d: float
    option_180d: Optional[float] = None
    option_365d: Optional[float] = None
    unit: str = "TON"
    last_updated: datetime
    suppliers_count: int
    average_delivery_days: int


class PriceHistory(BaseModel):
    """Historical pricing data"""
    commodity_code: str
    start_date: datetime
    end_date: datetime
    prices: List[PricePoint]
    min_price: float
    max_price: float
    avg_price: float


# Mock data for demonstration
MOCK_COMMODITIES = {
    "GRVL-RB": {
        "name": "Road Base Gravel",
        "spot": 28.50,
        "suppliers": 3
    },
    "FLEX-12": {
        "name": "Flex Base Grade 1-2",
        "spot": 32.00,
        "suppliers": 2
    },
    "CALC-STD": {
        "name": "Caliche",
        "spot": 45.00,
        "suppliers": 4
    },
    "LIME-SLR": {
        "name": "Lime Slurry",
        "spot": 143.00,
        "suppliers": 2
    }
}


@router.get("/current", response_model=List[CommodityPrice])
async def get_current_pricing():
    """
    Get current pricing for all commodities

    Returns:
        List of current commodity prices with option premiums
    """
    logger.info("Fetching current pricing for all commodities")

    result = []
    for code, data in MOCK_COMMODITIES.items():
        spot = data["spot"]
        result.append(CommodityPrice(
            commodity_code=code,
            commodity_name=data["name"],
            spot_price=spot,
            option_30d=round(spot * 1.08, 2),
            option_90d=round(spot * 1.12, 2),
            option_180d=round(spot * 1.15, 2),
            option_365d=round(spot * 1.20, 2),
            last_updated=datetime.utcnow(),
            suppliers_count=data["suppliers"],
            average_delivery_days=3
        ))

    return result


@router.get("/{commodity_code}", response_model=CommodityPrice)
async def get_commodity_price(commodity_code: str):
    """
    Get current pricing for a specific commodity

    Args:
        commodity_code: Commodity code (e.g., GRVL-RB)

    Returns:
        Current pricing data for the commodity
    """
    logger.info(f"Fetching pricing for commodity: {commodity_code}")

    if commodity_code not in MOCK_COMMODITIES:
        raise HTTPException(status_code=404, detail="Commodity not found")

    data = MOCK_COMMODITIES[commodity_code]
    spot = data["spot"]

    return CommodityPrice(
        commodity_code=commodity_code,
        commodity_name=data["name"],
        spot_price=spot,
        option_30d=round(spot * 1.08, 2),
        option_90d=round(spot * 1.12, 2),
        option_180d=round(spot * 1.15, 2),
        option_365d=round(spot * 1.20, 2),
        last_updated=datetime.utcnow(),
        suppliers_count=data["suppliers"],
        average_delivery_days=3
    )


@router.get("/history/{commodity_code}", response_model=PriceHistory)
async def get_price_history(
    commodity_code: str,
    days: int = Query(default=30, ge=1, le=365)
):
    """
    Get historical pricing data for a commodity

    Args:
        commodity_code: Commodity code
        days: Number of days of history to retrieve

    Returns:
        Historical pricing data
    """
    logger.info(f"Fetching {days} days of price history for {commodity_code}")

    if commodity_code not in MOCK_COMMODITIES:
        raise HTTPException(status_code=404, detail="Commodity not found")

    # Generate mock historical data
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    base_price = MOCK_COMMODITIES[commodity_code]["spot"]
    prices = []

    for i in range(days):
        date = start_date + timedelta(days=i)
        # Add some random variation
        variation = (hash(f"{commodity_code}{i}") % 100 - 50) / 100.0
        price = round(base_price + variation, 2)
        prices.append(PricePoint(
            timestamp=date,
            price=price
        ))

    price_values = [p.price for p in prices]

    return PriceHistory(
        commodity_code=commodity_code,
        start_date=start_date,
        end_date=end_date,
        prices=prices,
        min_price=min(price_values),
        max_price=max(price_values),
        avg_price=round(sum(price_values) / len(price_values), 2)
    )


@router.post("/update")
async def update_supplier_pricing():
    """
    Update pricing from supplier feeds
    (Protected endpoint - requires supplier authentication)
    """
    # TODO: Implement supplier authentication
    # TODO: Implement pricing update logic
    logger.info("Pricing update triggered")
    return {"status": "success", "message": "Pricing updated"}
