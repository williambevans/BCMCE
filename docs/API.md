# BCMCE Platform API Documentation

## Overview

The BCMCE Platform API provides real-time access to commodity pricing, option contracts, supplier inventory, and county procurement data.

**Base URL:** `http://localhost:8000` (development)
**API Version:** v1
**Format:** JSON

## Authentication

Currently, the API uses basic authentication for supplier and county endpoints. Public endpoints (pricing, available options) do not require authentication.

```bash
# Example authenticated request
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/suppliers/inventory
```

## Endpoints

### Pricing API

#### Get Current Pricing

```http
GET /api/v1/pricing/current
```

Returns current spot pricing and option premiums for all commodities.

**Response:**
```json
[
  {
    "commodity_code": "GRVL-RB",
    "commodity_name": "Road Base Gravel",
    "spot_price": 28.50,
    "option_30d": 30.78,
    "option_90d": 31.92,
    "option_180d": 32.78,
    "option_365d": 34.20,
    "unit": "TON",
    "last_updated": "2026-01-17T10:30:00Z",
    "suppliers_count": 3,
    "average_delivery_days": 3
  }
]
```

#### Get Commodity Price

```http
GET /api/v1/pricing/{commodity_code}
```

**Parameters:**
- `commodity_code` (path): Material code (e.g., GRVL-RB, CALC-STD)

**Example:**
```bash
curl http://localhost:8000/api/v1/pricing/GRVL-RB
```

#### Get Price History

```http
GET /api/v1/pricing/history/{commodity_code}?days=30
```

**Parameters:**
- `commodity_code` (path): Material code
- `days` (query): Number of days (1-365, default: 30)

**Response:**
```json
{
  "commodity_code": "GRVL-RB",
  "start_date": "2025-12-18T00:00:00Z",
  "end_date": "2026-01-17T00:00:00Z",
  "prices": [
    {"timestamp": "2025-12-18T00:00:00Z", "price": 28.25},
    {"timestamp": "2025-12-19T00:00:00Z", "price": 28.50}
  ],
  "min_price": 27.50,
  "max_price": 29.00,
  "avg_price": 28.45
}
```

### Options API

#### Get Available Options

```http
GET /api/v1/options/available?material_code=GRVL-RB&duration_days=90
```

**Query Parameters:**
- `material_code` (optional): Filter by material
- `duration_days` (optional): Filter by duration (30, 90, 180, 365)

**Response:**
```json
[
  {
    "material_code": "GRVL-RB",
    "material_name": "Road Base Gravel",
    "supplier_id": "supp-001",
    "supplier_name": "Clifton Quarry",
    "duration_days": 90,
    "strike_price": 28.50,
    "premium_percentage": 12.0,
    "total_price": 31.92,
    "available_quantity_tons": 500.0,
    "min_quantity_tons": 10.0,
    "delivery_radius_miles": 50
  }
]
```

#### Purchase Option

```http
POST /api/v1/options/purchase
```

**Request Body:**
```json
{
  "material_code": "GRVL-RB",
  "quantity_tons": 100.0,
  "duration_days": 90,
  "buyer_id": "bosque-county",
  "buyer_name": "Bosque County",
  "buyer_email": "commissioners@co.bosque.tx.us"
}
```

**Response:**
```json
{
  "id": "opt-12345",
  "material_code": "GRVL-RB",
  "material_name": "Road Base Gravel",
  "strike_price": 28.50,
  "quantity_tons": 100.0,
  "premium_paid": 342.00,
  "status": "active",
  "created_at": "2026-01-17T10:30:00Z",
  "expires_at": "2026-04-17T10:30:00Z"
}
```

#### Exercise Option

```http
POST /api/v1/options/exercise
```

**Request Body:**
```json
{
  "option_id": "opt-12345",
  "delivery_location": "FM 219 at CR 1740",
  "delivery_date": "2026-02-01",
  "notes": "Deliver to north end of road"
}
```

### Suppliers API

#### List Suppliers

```http
GET /api/v1/suppliers?status=active&txdot_certified=true
```

**Query Parameters:**
- `status` (optional): active, pending, suspended, inactive
- `txdot_certified` (optional): true/false

#### Get Supplier Details

```http
GET /api/v1/suppliers/{supplier_id}
```

#### Update Inventory

```http
POST /api/v1/suppliers/{supplier_id}/inventory
```

**Request Body:**
```json
{
  "material_code": "GRVL-RB",
  "quantity_available_tons": 500.0,
  "price_per_ton": 28.50,
  "quality_grade": "TxDOT Type A",
  "txdot_spec": "Type A"
}
```

### County API

#### Get County Requirements

```http
GET /api/v1/county/requirements?status=open
```

**Query Parameters:**
- `status` (optional): open, bidding, awarded, closed, cancelled
- `material_code` (optional): Filter by material

**Response:**
```json
[
  {
    "id": "req-001",
    "county_name": "Bosque County",
    "precinct": 1,
    "material_code": "GRVL-RB",
    "material_name": "Road Base Gravel",
    "quantity_tons": 500.0,
    "delivery_location": "FM 219 at County Road 1740",
    "required_by_date": "2026-02-15",
    "budget_allocated": 15000.00,
    "status": "open",
    "bid_deadline": "2026-01-31T17:00:00Z"
  }
]
```

#### Submit Bid

```http
POST /api/v1/county/bids/submit
```

**Request Body:**
```json
{
  "requirement_id": "req-001",
  "supplier_id": "supp-001",
  "supplier_name": "Clifton Quarry",
  "quantity_tons": 500.0,
  "price_per_ton": 28.50,
  "delivery_date": "2026-02-10",
  "notes": "Can deliver early if needed"
}
```

#### Get County Budget

```http
GET /api/v1/county/budget?fiscal_year=2026
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, there are no rate limits for the API. This may change in production.

## WebSocket Support (Future)

Real-time price updates will be available via WebSocket connection:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/prices');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Price update:', update);
};
```

## Changelog

### v1.0.0 (2026-01-17)
- Initial API release
- Pricing endpoints
- Options trading endpoints
- Supplier management
- County procurement integration
