# Getting Started with BCMCE Platform

## What is BCMCE?

The Bosque County Mineral & Commodities Exchange (BCMCE) is a transparent marketplace that brings financial market sophistication to local government procurement of construction materials.

**Key Features:**
- Real-time pricing from multiple suppliers
- Options contracts to lock in future prices
- Direct bid submission to county commissioners
- Automated market monitoring and alerts

## Who Should Use BCMCE?

### County Officials & Commissioners
- View real-time material pricing
- Purchase options to lock in budget prices
- Submit requirements and receive bids
- Track spending and commitments

### Material Suppliers
- List inventory and pricing
- Sell option contracts for guaranteed revenue
- Submit bids directly to counties
- Access to government contracts without complexity

### County Road Administrators
- Monitor price trends
- Plan material purchases
- Exercise options when needed
- Track deliveries and spending

## Quick Start Guide

### For County Officials

#### 1. View Current Pricing

Visit the BCMCE landing page to see current spot prices for all materials:
- **Landing Page:** https://williambevans.github.io/BCMCE/
- **API:** http://localhost:8000/api/v1/pricing/current

#### 2. Explore Available Options

See what option contracts are available:

```bash
curl http://localhost:8000/api/v1/options/available
```

You'll see options like:
- 30-day option on Road Base Gravel at $30.78/ton
- 90-day option on Caliche at $48.60/ton

#### 3. Purchase an Option (Budget Lock)

To lock in a price for future needs:

```bash
curl -X POST http://localhost:8000/api/v1/options/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "material_code": "GRVL-RB",
    "quantity_tons": 500,
    "duration_days": 90,
    "buyer_id": "bosque-county",
    "buyer_name": "Bosque County",
    "buyer_email": "commissioners@co.bosque.tx.us"
  }'
```

**What this means:**
- You pay a small premium (~12% for 90 days)
- Your price is locked for 3 months
- You can exercise the option anytime within 90 days
- If market prices rise, you save money
- If prices fall, you can buy at market price instead

#### 4. Post a Material Requirement

When you need materials, post a requirement:

```bash
curl -X POST http://localhost:8000/api/v1/county/requirements \
  -H "Content-Type: application/json" \
  -d '{
    "material_code": "GRVL-RB",
    "quantity_tons": 500,
    "delivery_location": "FM 219 at CR 1740",
    "required_by_date": "2026-02-15",
    "budget_allocated": 15000,
    "bid_deadline": "2026-01-31T17:00:00Z"
  }'
```

Suppliers will submit bids, and you can review them through the platform.

### For Suppliers

#### 1. Register as a Supplier

```bash
curl -X POST http://localhost:8000/api/v1/suppliers/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Company Name",
    "contact_name": "John Smith",
    "email": "contact@yourcompany.com",
    "phone": "254-555-1234",
    "address": "123 Business Road",
    "city": "Clifton",
    "zip_code": "76634",
    "latitude": 31.7813,
    "longitude": -97.5778,
    "txdot_certified": true,
    "materials_offered": ["GRVL-RB", "LMST-CR"]
  }'
```

#### 2. Update Your Inventory & Pricing

```bash
curl -X POST http://localhost:8000/api/v1/suppliers/YOUR_ID/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "material_code": "GRVL-RB",
    "quantity_available_tons": 500,
    "price_per_ton": 28.50,
    "quality_grade": "TxDOT Type A",
    "txdot_spec": "Type A"
  }'
```

#### 3. View County Requirements

```bash
curl http://localhost:8000/api/v1/county/requirements?status=open
```

#### 4. Submit a Bid

```bash
curl -X POST http://localhost:8000/api/v1/county/bids/submit \
  -H "Content-Type: application/json" \
  -d '{
    "requirement_id": "req-001",
    "supplier_id": "YOUR_ID",
    "supplier_name": "Your Company Name",
    "quantity_tons": 500,
    "price_per_ton": 28.50,
    "delivery_date": "2026-02-10"
  }'
```

## Understanding the Platform

### How Pricing Works

1. **Spot Price**: Current market price for immediate delivery
2. **Option Price**: Spot price + premium for future delivery guarantee

**Example:**
```
Road Base Gravel:
- Spot Price: $28.50/ton
- 30-day Option: $30.78/ton (8% premium)
- 90-day Option: $31.92/ton (12% premium)
```

### How Options Work

**Purchase an option:**
- County pays premium upfront
- Locks in strike price for X days
- Can exercise anytime before expiration

**Exercise the option:**
- County requests delivery
- Pays strike price × quantity
- HH Holdings coordinates delivery from supplier

**Benefits:**
- Budget certainty
- Protection from price increases
- Flexibility to buy at market if prices fall

### Material Codes Reference

| Code | Material | Typical Use |
|------|----------|-------------|
| GRVL-RB | Road Base Gravel | Road foundation |
| FLEX-12 | Flexible Base Grade 1-2 | Road base |
| CALC-STD | Caliche | Unpaved roads |
| LIME-SLR | Lime Slurry | Soil stabilization |
| LMST-CR | Crushed Limestone | Drainage, aggregate |
| GRVL-TOP | Topping Gravel | Road surface |
| HMAC-STD | Hot Mix Asphalt | Paving |

## Example Workflows

### Workflow 1: Planning a Road Project

1. **Check Current Prices** → See that gravel is $28.50/ton
2. **Review Budget** → Allocated $15,000 for project in March
3. **Purchase 90-day Option** → Lock in price now
4. **Post Requirement** → When ready to execute in February
5. **Review Bids** → Accept best bid
6. **Exercise Option** → Get materials at locked price

**Result:** Budget protection and price certainty

### Workflow 2: Supplier Participation

1. **Register** → Become approved supplier
2. **Post Inventory** → Update available materials and prices
3. **Monitor Requirements** → Get alerts for new county needs
4. **Submit Bids** → Compete for county business
5. **Deliver Materials** → Fulfill awarded contracts

**Result:** Access to government contracts without complexity

## Best Practices

### For Counties
- Purchase options at budget approval time
- Monitor price trends before large purchases
- Post requirements with adequate lead time
- Exercise options 3-5 days before needed

### For Suppliers
- Update pricing weekly
- Maintain accurate inventory levels
- Respond to requirements within 48 hours
- Provide TxDOT certifications when applicable

## Common Questions

### Q: What if I don't exercise my option?
**A:** The option expires, and you forfeit the premium. Only purchase options if you're confident you'll need the materials.

### Q: Can I purchase options for multiple materials?
**A:** Yes! You can have multiple active options across different materials.

### Q: How do suppliers get paid?
**A:** Through standard county payment processes (typically Net 30).

### Q: What if prices fall after I buy an option?
**A:** You can choose to buy at current market price instead and let your option expire.

### Q: Is there a minimum order quantity?
**A:** Typically 10-50 tons depending on material and supplier.

## Getting Help

- **API Documentation:** http://localhost:8000/api/docs
- **Technical Docs:** `/docs` directory
- **Issues:** https://github.com/williambevans/BCMCE/issues
- **Email:** contact@hhholdings.com

## What's Next?

1. Explore the [API Documentation](API.md)
2. Review [Deployment Guide](DEPLOYMENT.md) for installation
3. Check out [County Integration Guide](COUNTY_INTEGRATION.md)
4. Read [Supplier Onboarding Guide](SUPPLIER_ONBOARDING.md)

---

**Welcome to transparent, efficient government procurement!**

*BCMCE Platform - Operated by HH Holdings / Bevans Real Estate*
