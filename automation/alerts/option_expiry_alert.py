"""
Option Expiry Alert System
Monitors option contracts approaching expiration
"""

import logging
from typing import List
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExpiryAlert:
    """Option expiry alert"""
    option_id: str
    buyer_id: str
    buyer_email: str
    material_code: str
    material_name: str
    quantity_tons: float
    strike_price: float
    expires_at: datetime
    days_until_expiry: int


class OptionExpiryAlertManager:
    """Manages option expiry alerts"""

    ALERT_DAYS = [30, 14, 7, 3, 1]  # Send alerts at these days before expiry

    def __init__(self):
        self.alerts_sent = set()

    def check_expiring_options(self, active_options: List[dict]) -> List[ExpiryAlert]:
        """
        Check for options approaching expiration

        Args:
            active_options: List of active option contracts

        Returns:
            List of expiry alerts
        """
        logger.info(f"Checking {len(active_options)} active options for expiry")

        alerts = []
        now = datetime.utcnow()

        for option in active_options:
            expires_at = option['expires_at']
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)

            days_until_expiry = (expires_at - now).days

            # Check if we should send an alert
            if days_until_expiry in self.ALERT_DAYS:
                alert_key = f"{option['id']}_{days_until_expiry}"

                # Don't send duplicate alerts
                if alert_key not in self.alerts_sent:
                    alert = ExpiryAlert(
                        option_id=option['id'],
                        buyer_id=option['buyer_id'],
                        buyer_email=option.get('buyer_email', ''),
                        material_code=option['material_code'],
                        material_name=option['material_name'],
                        quantity_tons=option['quantity_tons'],
                        strike_price=option['strike_price'],
                        expires_at=expires_at,
                        days_until_expiry=days_until_expiry
                    )

                    alerts.append(alert)
                    self.alerts_sent.add(alert_key)

                    logger.info(
                        f"Expiry alert: Option {option['id']} expires in {days_until_expiry} days"
                    )

        return alerts

    def send_expiry_notifications(self, alerts: List[ExpiryAlert]):
        """
        Send expiry notification emails

        Args:
            alerts: List of expiry alerts to send
        """
        logger.info(f"Sending {len(alerts)} expiry notifications")

        for alert in alerts:
            # In production, would send email
            logger.info(
                f"EXPIRY ALERT to {alert.buyer_email}: "
                f"Option for {alert.quantity_tons} tons of {alert.material_name} "
                f"expires in {alert.days_until_expiry} days"
            )

            # Email template would include:
            # - Option details
            # - Days until expiry
            # - Instructions to exercise
            # - Link to platform


def main():
    """Demo option expiry alerts"""
    logging.basicConfig(level=logging.INFO)

    manager = OptionExpiryAlertManager()

    # Mock active options
    active_options = [
        {
            "id": "opt-001",
            "buyer_id": "buyer-001",
            "buyer_email": "commissioner@co.bosque.tx.us",
            "material_code": "GRVL-RB",
            "material_name": "Road Base Gravel",
            "quantity_tons": 500.0,
            "strike_price": 28.50,
            "expires_at": datetime.utcnow() + timedelta(days=7)
        },
        {
            "id": "opt-002",
            "buyer_id": "buyer-001",
            "buyer_email": "commissioner@co.bosque.tx.us",
            "material_code": "CALC-STD",
            "material_name": "Caliche",
            "quantity_tons": 300.0,
            "strike_price": 45.00,
            "expires_at": datetime.utcnow() + timedelta(days=30)
        }
    ]

    alerts = manager.check_expiring_options(active_options)
    manager.send_expiry_notifications(alerts)


if __name__ == "__main__":
    main()
