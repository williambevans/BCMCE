"""
Price Alert System
Monitors price changes and sends notifications
"""

import logging
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PriceAlert:
    """Price alert notification"""
    material_code: str
    material_name: str
    old_price: float
    new_price: float
    change_percentage: float
    supplier_id: str
    supplier_name: str
    timestamp: datetime


class PriceAlertManager:
    """Manages price change alerts"""

    ALERT_THRESHOLD_PERCENTAGE = 5.0  # Alert if price changes by 5% or more

    def __init__(self):
        self.alerts: List[PriceAlert] = []

    def check_price_changes(self, old_prices: Dict, new_prices: Dict) -> List[PriceAlert]:
        """
        Compare old and new prices, generate alerts for significant changes

        Args:
            old_prices: Previous pricing data
            new_prices: Current pricing data

        Returns:
            List of price alerts
        """
        logger.info("Checking for significant price changes")

        alerts = []

        for material_code, new_data in new_prices.items():
            if material_code not in old_prices:
                continue

            old_price = old_prices[material_code]['price']
            new_price = new_data['price']

            change_pct = ((new_price - old_price) / old_price) * 100

            if abs(change_pct) >= self.ALERT_THRESHOLD_PERCENTAGE:
                alert = PriceAlert(
                    material_code=material_code,
                    material_name=new_data['name'],
                    old_price=old_price,
                    new_price=new_price,
                    change_percentage=round(change_pct, 2),
                    supplier_id=new_data['supplier_id'],
                    supplier_name=new_data['supplier_name'],
                    timestamp=datetime.utcnow()
                )

                alerts.append(alert)
                logger.warning(
                    f"Price alert: {material_code} changed {change_pct:+.2f}% "
                    f"(${old_price:.2f} -> ${new_price:.2f})"
                )

        self.alerts.extend(alerts)
        return alerts

    def send_alert_notifications(self, alerts: List[PriceAlert]):
        """
        Send alert notifications via email/SMS

        Args:
            alerts: List of price alerts to send
        """
        logger.info(f"Sending {len(alerts)} price alert notifications")

        for alert in alerts:
            # In production, would send email via SMTP
            logger.info(f"ALERT: {alert.material_name} price changed by {alert.change_percentage:+.2f}%")

            # Could integrate with:
            # - Email (SMTP)
            # - SMS (Twilio)
            # - Slack/Discord webhooks
            # - Push notifications


def main():
    """Demo price alert system"""
    logging.basicConfig(level=logging.INFO)

    manager = PriceAlertManager()

    # Mock old and new prices
    old_prices = {
        "GRVL-RB": {"price": 28.50, "name": "Road Base Gravel", "supplier_id": "s1", "supplier_name": "Supplier A"},
        "CALC-STD": {"price": 45.00, "name": "Caliche", "supplier_id": "s2", "supplier_name": "Supplier B"}
    }

    new_prices = {
        "GRVL-RB": {"price": 30.50, "name": "Road Base Gravel", "supplier_id": "s1", "supplier_name": "Supplier A"},
        "CALC-STD": {"price": 44.00, "name": "Caliche", "supplier_id": "s2", "supplier_name": "Supplier B"}
    }

    alerts = manager.check_price_changes(old_prices, new_prices)
    manager.send_alert_notifications(alerts)


if __name__ == "__main__":
    main()
