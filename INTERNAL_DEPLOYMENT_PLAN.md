# BCMCE Internal Tool - Deployment Plan

```
╔═══════════════════════════════════════════════════════════════════════════╗
║   H.H. HOLDINGS INTERNAL TOOL                                            ║
║   Simplified Deployment for Single-Company Use                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

## Purpose

Build BCMCE as an **internal operations tool for H.H. Holdings** to:
1. Track options purchased from suppliers
2. Monitor county RFP opportunities
3. Calculate competitive bids
4. Submit bids to counties
5. Manage procurement portfolio

**NOT a public marketplace** - this is your private business tool.

---

## Simplified Scope

### What We're Building:

✅ **H.H. Holdings Dashboard**
- Login for your team
- Portfolio view of active options
- List of county RFPs (auto-detected)
- Bid calculator
- Options entry form

✅ **Options Management**
- Add options after phone deals with suppliers
- Track strike price, quantity, expiry
- Alert when options near expiry
- Calculate cost basis for bids

✅ **County RFP Monitoring**
- Scrape county commissioners court websites
- Detect material RFPs
- Email alerts to your team
- Match RFPs to your options

✅ **Bid Submission**
- Calculate bid using option price + premium + margin
- Generate bid documents
- Track submission status
- Record wins/losses

### What We're NOT Building:

❌ Public marketplace
❌ Supplier login portals
❌ Commissioner dashboards
❌ Multi-tenant features
❌ Public API access

---

## Phase 1: MVP Internal Tool (2-3 days)

### Day 1: Core Backend

**Morning: Fix Critical Issues**
- [ ] Fix Pydantic import (5 min)
- [ ] Fix health check import (5 min)
- [ ] Create .env file (15 min)
- [ ] Resolve database schema - use UUID (2 hours)

**Afternoon: Simplified Auth**
- [ ] Create simple H.H. Holdings auth
  - Remove multi-tenant complexity
  - Just username/password for your team
  - Admin role for Biri, user role for staff
- [ ] Create initial user accounts
  - Biri Bevans (admin)
  - 2-3 team members (users)

**Time: 4-5 hours**

---

### Day 2: Internal Dashboard

**Morning: Options Portfolio**
- [ ] Create options entry form
  ```
  Add Option Form:
  - Material: [dropdown]
  - Supplier: [dropdown]
  - Strike Price: [input]
  - Quantity (tons): [input]
  - Premium Paid: [input]
  - Expiry Date: [date picker]
  - Notes: [textarea]
  [Save Option]
  ```

- [ ] Create options list view
  ```
  Active Options Portfolio:
  ┌────────────────────────────────────────────────────────────┐
  │ Material    │ Supplier │ Strike │ Qty │ Expiry │ Actions  │
  ├────────────────────────────────────────────────────────────┤
  │ Road Base   │ Clifton  │ $28.50 │ 600t│ 45 days│ [Edit]   │
  │ Lime Slurry │ LAT      │ $140   │ 200t│ 12 days│ ⚠️[Edit] │
  └────────────────────────────────────────────────────────────┘
  ```

**Afternoon: RFP List & Bid Calculator**
- [ ] Create RFP list view (manual entry for now)
  ```
  County RFPs:
  ┌────────────────────────────────────────────────────────────┐
  │ County  │ Material    │ Quantity │ Deadline │ Actions     │
  ├────────────────────────────────────────────────────────────┤
  │ Bosque  │ Road Base   │ 500 tons │ Jan 25   │ [Calc Bid] │
  │ Hill    │ Caliche     │ 300 tons │ Jan 28   │ [Calc Bid] │
  └────────────────────────────────────────────────────────────┘
  ```

- [ ] Create bid calculator
  ```
  Bid Calculator:

  RFP: Bosque County - Road Base Gravel (500 tons)

  Your Option:
  Strike Price:    $28.50/ton
  Premium Paid:    $2.00/ton
  Cost Basis:      $30.50/ton

  Your Bid:
  Cost Basis:      $30.50
  + Margin:        $3.00
  = Bid Price:     $33.50/ton

  Total Bid:       $16,750

  Market Comparison:
  Current Spot:    $35.00/ton
  Your Savings:    $1.50/ton vs market
  County Saves:    $750 total

  [Generate Bid Document] [Submit to County]
  ```

**Time: 6-7 hours**

---

### Day 3: Testing & Polish

**Morning: Data Loading**
- [ ] Create seed data script
  - Load 12 material types
  - Add 7 supplier contacts
  - Create 2-3 sample options
  - Add 2-3 sample RFPs

- [ ] Test complete workflow:
  1. Login as Biri
  2. Add new option
  3. View portfolio
  4. Create RFP manually
  5. Calculate bid
  6. Verify calculations

**Afternoon: Deployment**
- [ ] Deploy to Docker
- [ ] Test in production environment
- [ ] Create user accounts
- [ ] Train Biri on platform use

**Time: 6-7 hours**

---

## Phase 2: Automation (2-3 days)

### Day 4: County Scrapers

**Morning: Scraper Setup**
- [ ] Configure Bosque County scraper
  - Commissioners court website
  - Meeting minutes parsing
  - RFP detection logic

- [ ] Configure 3 additional counties
  - Hill County
  - McLennan County
  - Coryell County

**Afternoon: Alert System**
- [ ] Email alerts when RFP detected
  - Send to Biri's email
  - Include RFP details
  - Show matching options

- [ ] Email alerts for expiring options
  - 7 days before expiry
  - 1 day before expiry
  - List affected options

**Time: 6-7 hours**

---

### Day 5: Integration & Testing

**Morning: WebSocket Integration**
- [ ] Wire WebSocket to FastAPI
- [ ] Real-time updates for:
  - New RFPs detected
  - Option expiry warnings
  - Bid status changes

**Afternoon: End-to-End Testing**
- [ ] Test scraper detection
- [ ] Verify email alerts work
- [ ] Test option entry → bid calculation → submission
- [ ] Verify portfolio calculations
- [ ] Test with actual county website

**Time: 6-7 hours**

---

### Day 6: TxDOT Integration

**Morning: Price Tracking**
- [ ] Complete TxDOT scraper
  - Pull average low bid prices
  - Update material spot prices
  - Historical price tracking

**Afternoon: Analytics**
- [ ] Portfolio P&L view
  - Cost basis vs current market
  - Unrealized gains/losses
  - Expiry risk analysis

- [ ] Bid win/loss tracking
  - Track submitted bids
  - Record awards
  - Calculate actual profits

**Time: 6-7 hours**

---

## Phase 3: Advanced Features (Optional)

### Document Generation
- [ ] Bid document templates
- [ ] Auto-populate county forms
- [ ] Export to PDF

### Supplier Relationship Management
- [ ] Supplier contact database
- [ ] Call log/notes
- [ ] Option purchase history per supplier

### Reporting
- [ ] Monthly P&L reports
- [ ] Options utilization rate
- [ ] Bid win rate analytics
- [ ] County market share

---

## Simplified Database Schema

### Core Tables (7 tables):

```sql
-- H.H. Holdings team members
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255),
    password_hash VARCHAR(255),
    role VARCHAR(20), -- 'admin' or 'user'
    created_at TIMESTAMP
);

-- Your purchased options
CREATE TABLE options_contracts (
    id UUID PRIMARY KEY,
    material_id UUID REFERENCES materials(id),
    supplier_id UUID REFERENCES suppliers(id),
    strike_price DECIMAL(10,2),
    quantity_tons DECIMAL(10,2),
    premium_paid DECIMAL(10,2),
    purchase_date DATE,
    expiry_date DATE,
    status VARCHAR(20), -- 'active', 'exercised', 'expired'
    notes TEXT,
    created_by UUID REFERENCES users(id)
);

-- Detected county RFPs
CREATE TABLE rfps (
    id UUID PRIMARY KEY,
    county_name VARCHAR(100),
    material_id UUID REFERENCES materials(id),
    quantity_tons DECIMAL(10,2),
    deadline DATE,
    requirements TEXT,
    detected_at TIMESTAMP,
    source_url TEXT,
    status VARCHAR(20) -- 'open', 'closed', 'awarded'
);

-- Your submitted bids
CREATE TABLE bids (
    id UUID PRIMARY KEY,
    rfp_id UUID REFERENCES rfps(id),
    option_id UUID REFERENCES options_contracts(id),
    bid_price_per_ton DECIMAL(10,2),
    total_bid_amount DECIMAL(12,2),
    submitted_date DATE,
    status VARCHAR(20), -- 'submitted', 'awarded', 'rejected'
    profit_loss DECIMAL(12,2),
    submitted_by UUID REFERENCES users(id)
);

-- Supplier contact info (reference data)
CREATE TABLE suppliers (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    contact_name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    notes TEXT
);

-- Material types (reference data)
CREATE TABLE materials (
    id UUID PRIMARY KEY,
    code VARCHAR(20),
    name VARCHAR(255),
    txdot_spec VARCHAR(100),
    unit VARCHAR(20),
    current_spot_price DECIMAL(10,2)
);

-- Price history tracking
CREATE TABLE price_history (
    id UUID PRIMARY KEY,
    material_id UUID REFERENCES materials(id),
    price DECIMAL(10,2),
    source VARCHAR(50), -- 'txdot', 'supplier', 'manual'
    recorded_at TIMESTAMP
);
```

---

## API Endpoints (Simplified)

### Authentication
```
POST   /api/v1/auth/login          # Login
GET    /api/v1/auth/me             # Current user
POST   /api/v1/auth/logout         # Logout
```

### Options Management
```
GET    /api/v1/options             # List your options
POST   /api/v1/options             # Add new option
GET    /api/v1/options/{id}        # Option details
PUT    /api/v1/options/{id}        # Update option
DELETE /api/v1/options/{id}        # Delete option
POST   /api/v1/options/{id}/exercise  # Mark exercised
```

### RFP Management
```
GET    /api/v1/rfps                # List RFPs
POST   /api/v1/rfps                # Add RFP manually
GET    /api/v1/rfps/{id}           # RFP details
GET    /api/v1/rfps/{id}/match     # Find matching options
```

### Bid Management
```
GET    /api/v1/bids                # Your bids
POST   /api/v1/bids                # Create bid
GET    /api/v1/bids/{id}           # Bid details
PUT    /api/v1/bids/{id}           # Update status
POST   /api/v1/bids/calculate      # Calculate bid
```

### Portfolio
```
GET    /api/v1/portfolio/summary   # Overview
GET    /api/v1/portfolio/p-l       # P&L report
GET    /api/v1/portfolio/expiring  # Expiring options
```

### Reference Data
```
GET    /api/v1/materials           # Material list
GET    /api/v1/suppliers           # Supplier list
POST   /api/v1/suppliers           # Add supplier
```

---

## Quick Start (After Phase 1)

### For Biri Bevans:

**1. Login**
```
URL: https://your-bcmce-domain.com
Username: biri
Password: [secure password]
```

**2. Add Your First Option**
```
Dashboard → [Add Option]

Example:
Material: Road Base Gravel
Supplier: Clifton Quarry
Strike Price: $28.50
Quantity: 600 tons
Premium Paid: $2.00/ton ($1,200 total)
Expiry: 90 days from today
Notes: Phone deal with John at Clifton, verbal agreement
[Save]
```

**3. Monitor RFPs**
```
Dashboard → RFPs Tab

System will automatically scrape county websites and populate this list.
You'll get email alerts when new RFPs match your materials.
```

**4. Calculate & Submit Bid**
```
When RFP appears:
1. Click [Calculate Bid]
2. Review your cost basis from option
3. Add desired margin
4. System shows competitive bid price
5. Click [Generate Document]
6. Submit to county (email/paper/online)
7. Track in system
```

---

## Security & Privacy

**Access:**
- HTTPS only
- Strong passwords required
- Session timeout after 30 min inactivity
- No public access

**Data:**
- All data is private to H.H. Holdings
- No data shared with suppliers or counties
- Regular backups
- Encrypted database

**Hosting:**
- Private server or secured cloud
- Firewall rules
- VPN access if needed

---

## Timeline Summary

```
┌────────────────────────────────────────────────────────────┐
│ Phase 1: MVP Internal Tool        2-3 days                │
│   Day 1: Core backend + auth      (4-5 hours)             │
│   Day 2: Dashboard + calculator   (6-7 hours)             │
│   Day 3: Testing + deployment     (6-7 hours)             │
│   ✅ Deliverable: Working internal tool                   │
├────────────────────────────────────────────────────────────┤
│ Phase 2: Automation                2-3 days                │
│   Day 4: County scrapers           (6-7 hours)             │
│   Day 5: Integration + testing     (6-7 hours)             │
│   Day 6: TxDOT + analytics         (6-7 hours)             │
│   ✅ Deliverable: Fully automated monitoring              │
├────────────────────────────────────────────────────────────┤
│ Phase 3: Advanced (Optional)       3-4 days                │
│   Document generation, CRM, reporting                      │
│   ✅ Deliverable: Enterprise features                     │
└────────────────────────────────────────────────────────────┘

Total: 7-10 days for complete internal tool
Minimum viable: 2-3 days
```

---

## Success Metrics

**After Phase 1, you should be able to:**
✅ Login to your dashboard
✅ Add options after phone calls with suppliers
✅ View your options portfolio
✅ Enter county RFPs manually
✅ Calculate competitive bids
✅ Track bid submissions

**After Phase 2, system should:**
✅ Automatically detect county RFPs
✅ Email you when opportunities appear
✅ Alert about expiring options
✅ Match RFPs to your options
✅ Track TxDOT pricing

**Business Impact:**
✅ Faster response to county RFPs
✅ Better bid calculations (cost basis tracking)
✅ No missed opportunities (automated monitoring)
✅ Higher win rate (competitive options-based pricing)
✅ Better portfolio management

---

```
════════════════════════════════════════════════════════════════════════════════
                      YOUR INTERNAL PROCUREMENT TOOL
                    From Options to Winning County Bids
════════════════════════════════════════════════════════════════════════════════
```

**Ready to start Phase 1?**

© 2026 HH Holdings LLC / Bevans Real Estate - Proprietary
