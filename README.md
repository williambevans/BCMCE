```
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
║                    A Bloomberg Terminal for County Materials             ║
║                                                                           ║
║   Operator:    HH Holdings LLC / Bevans Real Estate                      ║
║   Location:    397 Highway 22, Clifton, TX 76634                         ║
║   Broker:      Biri Bevans, Designated Broker                            ║
║   Platform:    BCMCE - Transparent Materials Marketplace                 ║
║                                                                           ║
║   Built with:  FastAPI • PostgreSQL • React • WebSocket                  ║
║   Version:     1.0.0 - Production Ready                                  ║
║   Copyright:   © 2026 HH Holdings LLC. All rights reserved.              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

# Bosque County Mineral & Commodities Exchange (BCMCE)

<p align="center">
  <img src="https://img.shields.io/badge/Status-Coming%20Q1%202026-ff9500?style=for-the-badge&labelColor=0a0a0a" alt="Status">
  <img src="https://img.shields.io/badge/Region-Central%20Texas-00a8ff?style=for-the-badge&labelColor=0a0a0a" alt="Region">
  <img src="https://img.shields.io/badge/License-Proprietary-ff3b3b?style=for-the-badge&labelColor=0a0a0a" alt="License">
</p>

<p align="center">
  <strong>A transparent, real-time marketplace for county construction materials with options-based pricing</strong>
</p>

<p align="center">
  <em>Solving the rural Texas county road maintenance crisis through market innovation</em>
</p>

```
════════════════════════════════════════════════════════════════════════════════
                            TERMINAL ACCESS GRANTED
════════════════════════════════════════════════════════════════════════════════
```

## 🎯 PROBLEM STATEMENT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CRITICAL INFRASTRUCTURE CRISIS                                              │
│                                                                             │
│ Bosque County has been unable to secure competitive bids for road          │
│ maintenance materials for 3-4 consecutive years.                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**This crisis extends across rural Texas counties facing:**
- `[ALERT]` Price volatility in essential construction materials
- `[ALERT]` Complex procurement processes that exclude small suppliers
- `[ALERT]` Limited budget visibility for multi-year infrastructure projects
- `[ALERT]` Inefficient market coordination between suppliers and government
- `[ALERT]` Deteriorating county road conditions

---

## 💡 THE BCMCE SOLUTION

BCMCE operates as a **Bloomberg Terminal for county road materials** combined with an **options market for government procurement**.

### Core Features

```
┌────────────────────────┬──────────────────────────────────────────────────┐
│ FEATURE                │ DESCRIPTION                                      │
├────────────────────────┼──────────────────────────────────────────────────┤
│ Real-Time Pricing      │ Live commodity prices from regional suppliers    │
│ Options Contracts      │ Lock in prices for 30, 90, or 365 days          │
│ Direct Bid Submission  │ Submit bids to Commissioners Court via platform  │
│ Supplier Aggregation   │ Single interface for all material sourcing       │
│ Budget Transparency    │ Track county spending and commitments            │
└────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 📊 MATERIALS COVERED

### Primary Commodities (Phase 1)

```
┌──────────┬─────────────────────────┬────────────────┬──────────────────────┐
│ CODE     │ MATERIAL                │ TxDOT SPEC     │ SPOT PRICE*          │
├──────────┼─────────────────────────┼────────────────┼──────────────────────┤
│ GRVL-RB  │ Road Base Gravel        │ Type A         │ $28.50/ton           │
│ FLEX-12  │ Flexible Base Gr 1-2    │ Item 247       │ $32.00/ton           │
│ CALC-STD │ Caliche                 │ Standard       │ $45.00/ton           │
│ LIME-SLR │ Lime Slurry             │ Hydrated Comm. │ $143.00/ton          │
│ LMST-CR  │ Crushed Limestone       │ 3/4" Minus     │ $35.00/ton           │
│ GRVL-PEA │ Pea Gravel              │ 3/8" Washed    │ $42.00/ton           │
│ GRVL-TOP │ Topping Gravel          │ Surface Grade  │ $38.00/ton           │
│ CLAY-FIL │ Fill Clay               │ Compactable    │ $18.00/ton           │
│ CMNT-PRT │ Portland Cement         │ Type I         │ $153.25/ton          │
│ CRSH-RUN │ Crusher Run             │ Dense Grade    │ $26.00/ton           │
│ LIME-QK  │ Quicklime (Dry)         │ TxDOT Type C   │ $170.85/ton          │
│ HMAC-STD │ Hot Mix Asphalt         │ Type D PG64    │ $109.58/ton          │
└──────────┴─────────────────────────┴────────────────┴──────────────────────┘

*Prices based on TxDOT Average Low Bid Unit Price data and
 regional supplier quotes (January 2026)
```

### Future Expansion (Phase 2+)
- Bridge materials & culverts
- Road signs & safety equipment
- Drainage systems
- Seal coat / chip seal materials
- Concrete ready-mix

---

## 🏗️ MARKET STRUCTURE

### Option Contract Types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CONTRACT TYPE    │  PREMIUM   │  USE CASE                                 │
├───────────────────┼────────────┼───────────────────────────────────────────┤
│  30-Day Option    │  +5-8%     │  Immediate project planning               │
│  90-Day Option    │  +8-12%    │  Quarterly budget cycles                  │
│  6-Month Option   │  +12-15%   │  Seasonal planning                        │
│  Annual Option    │  +15-20%   │  Multi-year road programs                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pricing Transparency

**All pricing visible in real-time:**
- `[LIVE]` **Spot Prices**: Current delivery pricing by material
- `[LIVE]` **Option Premiums**: Contract costs by duration
- `[LIVE]` **Supplier Inventory**: Available quantities
- `[CALC]` **Delivery Costs**: Distance-based pricing
- `[DATA]` **Historical Trends**: Market movement data

---

## 🛠️ TECHNICAL ARCHITECTURE

### Technology Stack

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                            BCMCE PLATFORM                                   ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  FRONTEND                                                                   ║
║  ├── Landing Page: HTML/CSS/JS (Bloomberg Terminal Style)                  ║
║  ├── Commissioner Dashboard: React + Tailwind                              ║
║  └── Supplier Portal: React + Tailwind                                     ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  BACKEND                                                                    ║
║  ├── API Server: Python FastAPI                                            ║
║  ├── Pricing Engine: Python + NumPy                                        ║
║  ├── Contract Manager: Python                                              ║
║  └── Bid Generator: Python                                                 ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  DATA LAYER                                                                 ║
║  ├── Primary DB: PostgreSQL                                                ║
║  ├── Cache: Redis                                                          ║
║  └── Time Series: TimescaleDB                                              ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  AUTOMATION                                                                 ║
║  ├── County Scraper: Python (Meeting minutes, RFPs)                       ║
║  ├── Price Aggregator: Python (Supplier feeds)                            ║
║  └── Settlement Processor: Python                                          ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

### API Endpoints

```python
# ═══════════════════════════════════════════════════════════════════════════
# PRICING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════
GET  /api/v1/pricing/current                    # All current prices
GET  /api/v1/pricing/{commodity_code}           # Single commodity
GET  /api/v1/pricing/history/{commodity_code}   # Historical data

# ═══════════════════════════════════════════════════════════════════════════
# OPTIONS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════
GET  /api/v1/options/available                  # Available contracts
POST /api/v1/options/purchase                   # Purchase option
GET  /api/v1/options/holdings                   # View held options
POST /api/v1/options/exercise                   # Exercise option

# ═══════════════════════════════════════════════════════════════════════════
# SUPPLIER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════
GET  /api/v1/suppliers                          # List suppliers
POST /api/v1/suppliers/inventory                # Update inventory
POST /api/v1/suppliers/pricing                  # Update pricing

# ═══════════════════════════════════════════════════════════════════════════
# COUNTY INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════
GET  /api/v1/county/requirements                # Posted requirements
POST /api/v1/county/bids/submit                 # Submit bid
GET  /api/v1/county/budget                      # Budget tracking
```

### Database Schema

```sql
-- ═══════════════════════════════════════════════════════════════════════════
-- CORE TABLES
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE suppliers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location_lat DECIMAL(10,6),
    location_lng DECIMAL(10,6),
    txdot_certified BOOLEAN DEFAULT FALSE,
    contact_info JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE materials (
    id UUID PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    grade VARCHAR(100),
    txdot_spec VARCHAR(50),
    unit VARCHAR(20) DEFAULT 'TON',
    category VARCHAR(50)
);

CREATE TABLE pricing_history (
    id UUID PRIMARY KEY,
    material_id UUID REFERENCES materials(id),
    supplier_id UUID REFERENCES suppliers(id),
    spot_price DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    delivery_radius_miles INTEGER
);

CREATE TABLE option_contracts (
    id UUID PRIMARY KEY,
    material_id UUID REFERENCES materials(id),
    supplier_id UUID REFERENCES suppliers(id),
    buyer_id UUID,
    strike_price DECIMAL(10,2) NOT NULL,
    quantity_tons DECIMAL(10,2) NOT NULL,
    duration_days INTEGER NOT NULL,
    premium_paid DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE county_requirements (
    id UUID PRIMARY KEY,
    material_id UUID REFERENCES materials(id),
    quantity_tons DECIMAL(10,2) NOT NULL,
    delivery_location VARCHAR(255),
    required_by DATE,
    budget_allocated DECIMAL(12,2),
    status VARCHAR(20) DEFAULT 'open',
    posted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bids (
    id UUID PRIMARY KEY,
    requirement_id UUID REFERENCES county_requirements(id),
    supplier_id UUID REFERENCES suppliers(id),
    price_per_ton DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    delivery_date DATE,
    submitted_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending'
);
```

---

## 📁 PROJECT STRUCTURE

```
bcmce/
├── README.md
├── LICENSE
├── .env.example
├── docker-compose.yml
│
├── frontend/
│   ├── index.html                      # Bloomberg-style landing page
│   ├── supplier-portal.html            # Supplier dashboard
│   ├── commissioner-dashboard.html     # Commissioner dashboard
│   └── js/
│       └── bcmce-client.js             # API client library
│
├── backend/
│   ├── requirements.txt
│   ├── main.py                         # FastAPI application
│   ├── models/
│   │   └── schemas.py                  # Pydantic models
│   ├── database.py                     # SQLAlchemy ORM
│   ├── auth.py                         # JWT authentication
│   ├── config.py                       # Configuration management
│   ├── websocket.py                    # WebSocket server
│   ├── notifications.py                # Email notifications
│   └── tests/
│       └── test_api.py                 # Integration tests
│
├── automation/
│   ├── scrapers/
│   │   ├── county_minutes_scraper.py
│   │   ├── rfp_detector.py
│   │   └── supplier_price_aggregator.py
│   └── alerts/
│       ├── price_alert.py
│       └── option_expiry_alert.py
│
├── data/
│   ├── seed/
│   │   ├── materials.json
│   │   └── suppliers.json
│   └── migrations/
│       └── 001_create_tables.sql
│
└── docs/
    ├── API.md
    ├── DEPLOYMENT.md
    └── GETTING_STARTED.md
```

---

## 💰 BUSINESS MODEL

### Revenue Streams

```
┌──────────────────────────┬───────────────────────────────┬─────────────────┐
│ STREAM                   │ DESCRIPTION                   │ EST. REVENUE    │
├──────────────────────────┼───────────────────────────────┼─────────────────┤
│ Option Premium Split     │ 40% HH Holdings / 60% Supplier│ Variable        │
│ Transaction Fees         │ 2.5% on executed contracts    │ ~$3,750/yr*     │
│ Performance Guarantee    │ Fee for price/delivery assure │ ~$5,000/yr      │
│ Data Services            │ Market reports to suppliers   │ ~$2,400/yr      │
└──────────────────────────┴───────────────────────────────┴─────────────────┘

*Based on $150K annual transaction volume (Year 1)
```

### Value Proposition

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ FOR BOSQUE COUNTY                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✓ 10-20% cost savings on materials                                         │
│ ✓ Budget certainty through options                                         │
│ ✓ Simplified procurement process                                           │
│ ✓ Faster project execution                                                 │
│ ✓ Transparent market pricing                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ FOR SUPPLIERS                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✓ Access to government contracts without bid complexity                    │
│ ✓ Predictable revenue through options                                      │
│ ✓ Reduced marketing costs                                                  │
│ ✓ Payment reliability from government contracts                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ FOR HH HOLDINGS                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✓ Transaction-based revenue                                                │
│ ✓ Market-making spread                                                     │
│ ✓ Strategic positioning in county operations                               │
│ ✓ Expansion potential to other counties                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ IMPLEMENTATION ROADMAP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: FOUNDATION (Months 1-2)                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ [ ] Entity formation (HH Holdings DBA BCMCE)                               │
│ [ ] Legal structure and agreements                                         │
│ [ ] Master Supply Agreement template                                       │
│ [ ] Basic landing page deployment                                          │
│ [ ] Initial supplier outreach                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: PILOT PROGRAM (Months 2-4)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ [ ] 3-5 supplier network established                                       │
│ [ ] Gravel and caliche markets operational                                 │
│ [ ] First option contracts issued                                          │
│ [ ] Commissioner demonstration                                             │
│ [ ] Feedback integration                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: FULL LAUNCH (Months 4-6)                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ [ ] All material categories active                                         │
│ [ ] 10+ supplier participants                                              │
│ [ ] Automated bid submission                                               │
│ [ ] Settlement coordination                                                │
│ [ ] County budget integration                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: REGIONAL EXPANSION (Months 6-12)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ [ ] Hill County integration                                                │
│ [ ] McLennan County integration                                            │
│ [ ] Coryell County integration                                             │
│ [ ] Enhanced analytics platform                                            │
│ [ ] Multi-county aggregation                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 COMPLIANCE & REGULATIONS

### Texas Government Code Compliance
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Chapter 262: County Purchasing Act                                         │
│ §262.023: Competitive bidding requirements (>$50,000)                      │
│ §262.024: Competitive sealed proposals                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### TxDOT Standards
- **Item 247**: Flexible Base specifications
- **Item 260**: Lime Treatment standards
- **Item 275**: Cement Treatment standards
- **DMS-6350**: Lime and Lime Slurry requirements

### Required Certifications
- TxDOT Approved Supplier status
- Lime Association of Texas (LAT) certification (for lime products)
- County vendor registration

---

## 🤝 INITIAL SUPPLIER NETWORK (Target)

```
┌─────────────────────────────┬──────────────┬─────────────────────┬─────────┐
│ SUPPLIER                    │ LOCATION     │ MATERIALS           │ STATUS  │
├─────────────────────────────┼──────────────┼─────────────────────┼─────────┤
│ Clifton Quarry              │ Clifton, TX  │ Limestone, Roadbase │ Target  │
│ Loftin Dirt Works           │ Bosque Co.   │ Gravel, Excavation  │ Target  │
│ Central TX Stone & Agg.     │ Central TX   │ Flex Base, Riprap   │ Target  │
│ LAT Member Suppliers        │ Regional     │ Lime Products       │ Target  │
│ Local Caliche Operators     │ Bosque/Hill  │ Caliche, Fill       │ Target  │
└─────────────────────────────┴──────────────┴─────────────────────┴─────────┘
```

---

## 🔗 RELATED RESOURCES

### TxDOT References
- [TxDOT Average Low Bid Prices](https://www.dot.state.tx.us/insdtdot/orgchart/cmd/cserve/bidprice/)
- [TxDOT Flexible Base Guidelines](https://ftp.txdot.gov/pub/txdot-info/cst/tips/flex-base-guidelines.pdf)
- [TxDOT 2024 Specifications](https://ftp.txdot.gov/pub/txdot-info/cmd/cserve/specs/2024/)

### Industry Resources
- [Lime Association of Texas](https://limetexas.org/)
- [Texas County Progress - Road Survey](https://countyprogress.com/road-survey-report/)
- [AGC Texas Material Suppliers](https://web.agctx.org/Material-and-Product-Suppliers-Sand-and-Gravel)

---

## 📞 CONTACT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  HH HOLDINGS / BEVANS REAL ESTATE                                          │
│  Biri Bevans, Designated Broker                                            │
│                                                                             │
│  397 Highway 22                                                            │
│  Clifton, TX 76634                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📜 LICENSE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Proprietary - All Rights Reserved                                          │
│ © 2026 HH Holdings / Bevans Real Estate                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

```
════════════════════════════════════════════════════════════════════════════════
              BUILDING TRANSPARENT INFRASTRUCTURE MARKETS
                        FOR RURAL TEXAS COUNTIES
════════════════════════════════════════════════════════════════════════════════
                    SOLVING REAL PROBLEMS WITH
                      MARKET INNOVATION
════════════════════════════════════════════════════════════════════════════════
                   BCMCE v1.0.0 - PRODUCTION READY
════════════════════════════════════════════════════════════════════════════════
```
