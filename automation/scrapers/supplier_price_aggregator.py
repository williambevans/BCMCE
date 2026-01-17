"""
Supplier Price Aggregator
Collects and aggregates pricing from multiple supplier sources
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging
import json
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MaterialPrice:
    """Material pricing data point"""
    supplier_id: str
    supplier_name: str
    material_code: str
    material_name: str
    price_per_ton: float
    quantity_available: float
    delivery_radius_miles: int
    location_lat: float
    location_lng: float
    timestamp: datetime
    source: str


class SupplierPriceAggregator:
    """Aggregates pricing from multiple supplier sources"""

    def __init__(self):
        self.prices: List[MaterialPrice] = []

    def fetch_txdot_average_prices(self) -> List[MaterialPrice]:
        """
        Fetch TxDOT average low bid prices

        Returns:
            List of material prices from TxDOT data
        """
        logger.info("Fetching TxDOT average low bid prices")

        # TxDOT publishes average low bid unit prices
        # URL: https://www.dot.state.tx.us/insdtdot/orgchart/cmd/cserve/bidprice/

        # Mock data based on actual TxDOT January 2026 prices
        txdot_prices = [
            MaterialPrice(
                supplier_id="txdot-avg",
                supplier_name="TxDOT Average (Central TX)",
                material_code="GRVL-RB",
                material_name="Road Base Gravel",
                price_per_ton=28.50,
                quantity_available=0,  # Reference price only
                delivery_radius_miles=0,
                location_lat=31.5,
                location_lng=-97.5,
                timestamp=datetime.utcnow(),
                source="TxDOT Average Low Bid"
            ),
            MaterialPrice(
                supplier_id="txdot-avg",
                supplier_name="TxDOT Average (Central TX)",
                material_code="FLEX-12",
                material_name="Flexible Base Grade 1-2",
                price_per_ton=32.00,
                quantity_available=0,
                delivery_radius_miles=0,
                location_lat=31.5,
                location_lng=-97.5,
                timestamp=datetime.utcnow(),
                source="TxDOT Average Low Bid"
            ),
            MaterialPrice(
                supplier_id="txdot-avg",
                supplier_name="TxDOT Average (Central TX)",
                material_code="LIME-SLR",
                material_name="Lime Slurry",
                price_per_ton=143.00,
                quantity_available=0,
                delivery_radius_miles=0,
                location_lat=31.5,
                location_lng=-97.5,
                timestamp=datetime.utcnow(),
                source="TxDOT Average Low Bid"
            ),
            MaterialPrice(
                supplier_id="txdot-avg",
                supplier_name="TxDOT Average (Central TX)",
                material_code="HMAC-STD",
                material_name="Hot Mix Asphalt Type D",
                price_per_ton=109.58,
                quantity_available=0,
                delivery_radius_miles=0,
                location_lat=31.5,
                location_lng=-97.5,
                timestamp=datetime.utcnow(),
                source="TxDOT Average Low Bid"
            ),
        ]

        logger.info(f"Fetched {len(txdot_prices)} TxDOT reference prices")
        return txdot_prices

    def fetch_supplier_api_prices(self, supplier_id: str, api_url: str) -> List[MaterialPrice]:
        """
        Fetch prices from supplier API

        Args:
            supplier_id: Supplier identifier
            api_url: Supplier API endpoint

        Returns:
            List of material prices
        """
        logger.info(f"Fetching prices from supplier API: {supplier_id}")

        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Convert API response to MaterialPrice objects
            prices = []
            for item in data.get('materials', []):
                prices.append(MaterialPrice(
                    supplier_id=supplier_id,
                    supplier_name=data.get('supplier_name', 'Unknown'),
                    material_code=item['code'],
                    material_name=item['name'],
                    price_per_ton=item['price'],
                    quantity_available=item.get('quantity', 0),
                    delivery_radius_miles=item.get('delivery_radius', 50),
                    location_lat=data.get('location', {}).get('lat', 0),
                    location_lng=data.get('location', {}).get('lng', 0),
                    timestamp=datetime.utcnow(),
                    source='Supplier API'
                ))

            logger.info(f"Fetched {len(prices)} prices from {supplier_id}")
            return prices

        except Exception as e:
            logger.error(f"Error fetching from supplier API {supplier_id}: {str(e)}")
            return []

    def fetch_local_supplier_prices(self) -> List[MaterialPrice]:
        """
        Fetch prices from local Bosque County suppliers

        Returns:
            List of material prices
        """
        logger.info("Fetching prices from local suppliers")

        # Mock data from known local suppliers
        local_prices = [
            MaterialPrice(
                supplier_id="clifton-quarry",
                supplier_name="Clifton Quarry",
                material_code="GRVL-RB",
                material_name="Road Base Gravel",
                price_per_ton=27.50,
                quantity_available=500.0,
                delivery_radius_miles=50,
                location_lat=31.7813,
                location_lng=-97.5778,
                timestamp=datetime.utcnow(),
                source="Direct Supplier"
            ),
            MaterialPrice(
                supplier_id="clifton-quarry",
                supplier_name="Clifton Quarry",
                material_code="LMST-CR",
                material_name="Crushed Limestone",
                price_per_ton=34.00,
                quantity_available=750.0,
                delivery_radius_miles=50,
                location_lat=31.7813,
                location_lng=-97.5778,
                timestamp=datetime.utcnow(),
                source="Direct Supplier"
            ),
            MaterialPrice(
                supplier_id="bosque-river-pit",
                supplier_name="Bosque River Pit",
                material_code="CALC-STD",
                material_name="Caliche",
                price_per_ton=44.00,
                quantity_available=300.0,
                delivery_radius_miles=40,
                location_lat=31.8200,
                location_lng=-97.6100,
                timestamp=datetime.utcnow(),
                source="Direct Supplier"
            ),
        ]

        logger.info(f"Fetched {len(local_prices)} local supplier prices")
        return local_prices

    def aggregate_all_prices(self) -> Dict:
        """
        Aggregate prices from all sources

        Returns:
            Aggregated pricing data
        """
        logger.info("Aggregating prices from all sources")

        all_prices = []

        # Fetch from all sources
        all_prices.extend(self.fetch_txdot_average_prices())
        all_prices.extend(self.fetch_local_supplier_prices())

        # Calculate market statistics
        market_stats = self._calculate_market_stats(all_prices)

        return {
            'aggregated_at': datetime.utcnow().isoformat(),
            'total_prices': len(all_prices),
            'sources': list(set(p.source for p in all_prices)),
            'suppliers': list(set(p.supplier_id for p in all_prices)),
            'market_stats': market_stats,
            'prices': [asdict(p) for p in all_prices]
        }

    def _calculate_market_stats(self, prices: List[MaterialPrice]) -> Dict:
        """Calculate market statistics by material"""
        stats = {}

        # Group by material code
        by_material = {}
        for price in prices:
            if price.material_code not in by_material:
                by_material[price.material_code] = []
            by_material[price.material_code].append(price)

        # Calculate stats for each material
        for material_code, material_prices in by_material.items():
            price_values = [p.price_per_ton for p in material_prices]
            stats[material_code] = {
                'material_name': material_prices[0].material_name,
                'suppliers_count': len(set(p.supplier_id for p in material_prices)),
                'min_price': min(price_values),
                'max_price': max(price_values),
                'avg_price': round(sum(price_values) / len(price_values), 2),
                'total_available_tons': sum(p.quantity_available for p in material_prices)
            }

        return stats


def main():
    """Main execution function"""
    logging.basicConfig(level=logging.INFO)

    aggregator = SupplierPriceAggregator()

    # Aggregate all prices
    results = aggregator.aggregate_all_prices()

    # Save results
    with open('aggregated_prices.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"Price aggregation complete. Processed {results['total_prices']} prices.")
    logger.info(f"Results saved to aggregated_prices.json")

    # Print summary
    print("\n=== BCMCE Price Aggregation Summary ===")
    print(f"Total Prices: {results['total_prices']}")
    print(f"Sources: {', '.join(results['sources'])}")
    print(f"Suppliers: {len(results['suppliers'])}")
    print("\nMarket Statistics by Material:")
    for code, stats in results['market_stats'].items():
        print(f"\n{code} - {stats['material_name']}")
        print(f"  Suppliers: {stats['suppliers_count']}")
        print(f"  Price Range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
        print(f"  Average: ${stats['avg_price']:.2f}/ton")
        print(f"  Available: {stats['total_available_tons']:.0f} tons")


if __name__ == "__main__":
    main()
