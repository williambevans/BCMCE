"""
WebSocket Server for Real-Time Updates
Pushes live pricing updates, option expirations, and bid notifications
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
import json
import asyncio
import logging
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, Set[WebSocket]] = {
            "pricing": set(),
            "options": set(),
            "bids": set(),
            "orders": set(),
            "all": set()
        }

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        """
        Accept new WebSocket connection and subscribe to channel

        Args:
            websocket: WebSocket connection
            channel: Channel to subscribe to (pricing, options, bids, orders, all)
        """
        await websocket.accept()
        self.active_connections.append(websocket)

        if channel in self.subscriptions:
            self.subscriptions[channel].add(websocket)
        else:
            self.subscriptions["all"].add(websocket)

        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection",
                "message": f"Connected to BCMCE {channel} channel",
                "timestamp": datetime.utcnow().isoformat()
            },
            websocket
        )

    def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection

        Args:
            websocket: WebSocket connection to remove
        """
        self.active_connections.remove(websocket)

        # Remove from all subscription channels
        for channel_connections in self.subscriptions.values():
            channel_connections.discard(websocket)

        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to specific connection

        Args:
            message: Message data
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")

    async def broadcast(self, message: dict, channel: str = "all"):
        """
        Broadcast message to all connections in a channel

        Args:
            message: Message data
            channel: Target channel (pricing, options, bids, orders, all)
        """
        message["timestamp"] = datetime.utcnow().isoformat()

        target_connections = self.subscriptions.get(channel, set())

        # Also send to "all" channel subscribers
        if channel != "all":
            target_connections = target_connections.union(self.subscriptions["all"])

        disconnected = []

        for connection in target_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Broadcast error: {str(e)}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_pricing_update(self, material_id: int, material_name: str,
                                      supplier_id: int, supplier_name: str,
                                      old_price: Decimal, new_price: Decimal):
        """
        Broadcast pricing update

        Args:
            material_id: Material ID
            material_name: Material name
            supplier_id: Supplier ID
            supplier_name: Supplier name
            old_price: Previous price
            new_price: New price
        """
        change_percent = float((new_price - old_price) / old_price * 100)

        message = {
            "type": "pricing_update",
            "material_id": material_id,
            "material_name": material_name,
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "old_price": float(old_price),
            "new_price": float(new_price),
            "change_percent": round(change_percent, 2),
            "direction": "up" if new_price > old_price else "down"
        }

        await self.broadcast(message, "pricing")
        logger.info(f"Price update broadcast: {material_name} @ ${new_price}")

    async def broadcast_option_expiry(self, contract_number: str, county_name: str,
                                     material_name: str, quantity: Decimal,
                                     days_until_expiry: int):
        """
        Broadcast option contract expiry alert

        Args:
            contract_number: Option contract number
            county_name: County name
            material_name: Material name
            quantity: Contract quantity
            days_until_expiry: Days remaining
        """
        message = {
            "type": "option_expiry",
            "contract_number": contract_number,
            "county_name": county_name,
            "material_name": material_name,
            "quantity": float(quantity),
            "days_until_expiry": days_until_expiry,
            "urgency": "high" if days_until_expiry <= 3 else "medium" if days_until_expiry <= 7 else "low"
        }

        await self.broadcast(message, "options")
        logger.info(f"Option expiry broadcast: {contract_number} ({days_until_expiry} days)")

    async def broadcast_new_bid(self, requirement_number: str, county_name: str,
                               material_name: str, quantity: Decimal,
                               bid_count: int):
        """
        Broadcast new bid submission

        Args:
            requirement_number: Requirement number
            county_name: County name
            material_name: Material name
            quantity: Required quantity
            bid_count: Number of bids received
        """
        message = {
            "type": "new_bid",
            "requirement_number": requirement_number,
            "county_name": county_name,
            "material_name": material_name,
            "quantity": float(quantity),
            "bid_count": bid_count
        }

        await self.broadcast(message, "bids")
        logger.info(f"New bid broadcast: {requirement_number} ({bid_count} bids)")

    async def broadcast_order_status(self, order_number: str, status: str,
                                    county_name: str, supplier_name: str,
                                    material_name: str, quantity: Decimal):
        """
        Broadcast order status change

        Args:
            order_number: Order number
            status: New status
            county_name: County name
            supplier_name: Supplier name
            material_name: Material name
            quantity: Order quantity
        """
        message = {
            "type": "order_status",
            "order_number": order_number,
            "status": status,
            "county_name": county_name,
            "supplier_name": supplier_name,
            "material_name": material_name,
            "quantity": float(quantity)
        }

        await self.broadcast(message, "orders")
        logger.info(f"Order status broadcast: {order_number} - {status}")

    async def broadcast_market_alert(self, alert_type: str, message: str,
                                    severity: str = "info"):
        """
        Broadcast general market alert

        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity (info, warning, critical)
        """
        alert_message = {
            "type": "market_alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity
        }

        await self.broadcast(alert_message, "all")
        logger.info(f"Market alert broadcast: {alert_type} - {severity}")


# Global connection manager instance
manager = ConnectionManager()


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def pricing_monitor_task():
    """
    Background task to monitor pricing changes
    Runs continuously and broadcasts updates
    """
    from backend.database import get_db_session
    from backend.database import Pricing, Material, Supplier

    logger.info("Pricing monitor task started")

    # Store previous prices
    price_cache = {}

    while True:
        try:
            db = get_db_session()

            # Query active pricing
            pricings = db.query(Pricing).filter(Pricing.is_active == True).all()

            for pricing in pricings:
                cache_key = f"{pricing.supplier_id}_{pricing.material_id}"
                current_price = pricing.spot_price

                # Check if price changed
                if cache_key in price_cache:
                    old_price = price_cache[cache_key]

                    if current_price != old_price:
                        # Price changed - broadcast update
                        material = db.query(Material).get(pricing.material_id)
                        supplier = db.query(Supplier).get(pricing.supplier_id)

                        await manager.broadcast_pricing_update(
                            material_id=pricing.material_id,
                            material_name=material.name,
                            supplier_id=pricing.supplier_id,
                            supplier_name=supplier.name,
                            old_price=old_price,
                            new_price=current_price
                        )

                # Update cache
                price_cache[cache_key] = current_price

            db.close()

        except Exception as e:
            logger.error(f"Pricing monitor error: {str(e)}")

        # Check every 30 seconds
        await asyncio.sleep(30)


async def option_expiry_monitor_task():
    """
    Background task to monitor option expirations
    Sends alerts for expiring options
    """
    from backend.database import get_db_session
    from backend.database import OptionContract, County, OptionPrice, Material
    from datetime import date, timedelta

    logger.info("Option expiry monitor task started")

    while True:
        try:
            db = get_db_session()

            today = date.today()
            alert_date = today + timedelta(days=7)  # Alert 7 days before

            # Query expiring options
            expiring_options = db.query(OptionContract).filter(
                OptionContract.status == "ACTIVE",
                OptionContract.expiration_date <= alert_date,
                OptionContract.expiration_date >= today
            ).all()

            for option in expiring_options:
                county = db.query(County).get(option.county_id)
                option_price = db.query(OptionPrice).get(option.option_price_id)
                material = db.query(Material).get(option_price.material_id)

                days_until_expiry = (option.expiration_date - today).days

                await manager.broadcast_option_expiry(
                    contract_number=option.contract_number,
                    county_name=county.name,
                    material_name=material.name,
                    quantity=option.quantity,
                    days_until_expiry=days_until_expiry
                )

            db.close()

        except Exception as e:
            logger.error(f"Option expiry monitor error: {str(e)}")

        # Check every hour
        await asyncio.sleep(3600)


# ============================================================================
# FASTAPI WEBSOCKET ENDPOINT
# ============================================================================

async def websocket_endpoint(websocket: WebSocket, channel: str = "all"):
    """
    WebSocket endpoint for real-time updates

    Usage in FastAPI:
        @app.websocket("/ws/{channel}")
        async def websocket_route(websocket: WebSocket, channel: str):
            await websocket_endpoint(websocket, channel)
    """
    await manager.connect(websocket, channel)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()

            # Handle ping/pong
            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test WebSocket manager
    print("BCMCE WebSocket Server")
    print("=" * 50)
    print(f"Active connections: {len(manager.active_connections)}")
    print(f"Subscription channels: {list(manager.subscriptions.keys())}")
    print("\nTo start WebSocket server, run the FastAPI application")
