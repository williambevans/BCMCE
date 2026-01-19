# BCMCE Platform - Revised Internal Architecture

```
╔═══════════════════════════════════════════════════════════════════════════╗
║   H. H. HOLDINGS INTERNAL PLATFORM                                        ║
║   BCMCE - Procurement Operations Management                               ║
║   PROPRIETARY - NOT A PUBLIC MARKETPLACE                                  ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

## Platform Purpose (Revised)

**BCMCE is H.H. Holdings' internal operations platform for competitive bidding on county materials contracts.**

### What It Does:
1. **Monitors** county commissioners court RFPs and bid opportunities
2. **Tracks** options contracts purchased from suppliers
3. **Manages** your options portfolio (strike prices, expiries, quantities)
4. **Calculates** competitive bids using option-locked prices
5. **Submits** bids to counties when RFPs are posted
6. **Alerts** your team about opportunities and expiring options

### What It Is NOT:
- ❌ NOT a public marketplace
- ❌ NOT open to other companies
- ❌ NOT a platform for suppliers to login
- ❌ NOT a platform for counties to post RFPs directly

---

## Core Users

### Primary User: H.H. Holdings Team
**Who:**
- Biri Bevans (Designated Broker)
- H.H. Holdings employees
- Bevans Real Estate staff

**What They Do:**
- Monitor county RFP opportunities
- Purchase options from suppliers (offline/phone deals)
- Enter option contracts into system
- Calculate bids using option prices
- Submit bids to counties
- Track portfolio performance

**Authentication:**
- Simple username/password
- No multi-tenant features needed
- Admin role for Biri, user role for staff

---

## Core Workflows

### Workflow 1: County RFP Monitoring

```
┌─────────────────────────────────────────────────────────────────┐
│ AUTOMATED MONITORING                                            │
├─────────────────────────────────────────────────────────────────┤
│ 1. Scraper monitors county websites                            │
│    - Bosque County commissioners court                         │
│    - Hill County                                                │
│    - McLennan County                                            │
│    - Coryell County                                             │
│                                                                 │
│ 2. Detect new RFPs for materials                               │
│    - Parse meeting minutes                                      │
│    - Identify material requirements                             │
│    - Extract quantities and deadlines                           │
│                                                                 │
│ 3. Alert H.H. Holdings team                                     │
│    - Email notification                                         │
│    - Dashboard alert                                            │
│    - Show matched options you have                              │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow 2: Options Management

```
┌─────────────────────────────────────────────────────────────────┐
│ INTERNAL OPTIONS TRACKING                                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. Call suppliers to negotiate options                         │
│    - H.H. Holdings makes phone calls                           │
│    - Negotiate strike price and premium                        │
│    - Agree on quantity and duration                             │
│                                                                 │
│ 2. Enter option into BCMCE system                              │
│    - Material type                                              │
│    - Supplier                                                   │
│    - Strike price (locked-in price)                            │
│    - Quantity (tons)                                            │
│    - Premium paid                                               │
│    - Expiry date                                                │
│                                                                 │
│ 3. System tracks option                                         │
│    - Shows in portfolio                                         │
│    - Calculates current value                                   │
│    - Alerts when nearing expiry (7 days)                       │
│    - Matches to relevant RFPs                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow 3: Bid Calculation & Submission

```
┌─────────────────────────────────────────────────────────────────┐
│ COMPETITIVE BIDDING                                             │
├─────────────────────────────────────────────────────────────────┤
│ 1. County posts RFP                                             │
│    - Example: Bosque County needs 500 tons road base gravel    │
│    - Deadline: Submit by commissioners court meeting           │
│                                                                 │
│ 2. BCMCE shows matched options                                  │
│    - Display: You have 600 ton option on road base            │
│    - Strike price: $28.50/ton                                   │
│    - Premium paid: $2.00/ton                                    │
│    - Expiry: 45 days remaining                                  │
│                                                                 │
│ 3. Calculate competitive bid                                    │
│    - Cost basis: $28.50 (strike) + $2.00 (premium) = $30.50   │
│    - Add margin: $30.50 + $3.00 = $33.50/ton                  │
│    - Total bid: 500 tons × $33.50 = $16,750                   │
│    - Compare to current spot price: $35.00/ton                 │
│    - Your advantage: $1.50/ton cheaper                         │
│                                                                 │
│ 4. Submit bid to county                                         │
│    - Generate bid document                                      │
│    - Submit via county process (online/email/paper)            │
│    - Track submission status                                    │
│                                                                 │
│ 5. If awarded                                                   │
│    - Exercise option with supplier                              │
│    - Arrange delivery to county                                 │
│    - Mark option as exercised in system                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Simplified Architecture

### Frontend (H.H. Holdings Dashboard Only)

```
┌─────────────────────────────────────────────────────────────────┐
│ H.H. HOLDINGS INTERNAL DASHBOARD                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 PORTFOLIO VIEW                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Active Options:           12 contracts                   │  │
│  │ Total Locked Value:       $125,000                       │  │
│  │ Expiring Soon (7 days):   3 contracts                    │  │
│  │ Available Capacity:       2,400 tons across materials    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  🎯 ACTIVE RFPs                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Bosque County - Road Base Gravel                         │  │
│  │ Quantity: 500 tons | Deadline: Jan 25                    │  │
│  │ ✅ You have matching option (Strike: $28.50)            │  │
│  │ [Calculate Bid] [Submit Bid]                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  📋 OPTIONS CONTRACTS                                           │
│  ┌────────────────────────────────────────────────────────────┐│
│  │Material    │Supplier │Strike│Qty  │Expiry │Status        ││ │
│  │Road Base   │Clifton  │$28.50│600t │45d    │Active        ││ │
│  │Lime Slurry │LAT      │$140  │200t │12d    │⚠️ Expiring   ││ │
│  │Caliche     │Loftin   │$43   │400t │90d    │Active        ││ │
│  └────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [Add Option] [View Reports] [Settings]                        │
└─────────────────────────────────────────────────────────────────┘
```

### Backend (Internal Operations API)

**Simplified API Endpoints:**

```python
# Authentication (Internal Team Only)
POST   /api/v1/auth/login        # H.H. Holdings team login
GET    /api/v1/auth/me           # Current user info

# Options Management (Internal)
GET    /api/v1/options            # List your options portfolio
POST   /api/v1/options            # Add new option (after phone deal with supplier)
PUT    /api/v1/options/{id}       # Update option details
DELETE /api/v1/options/{id}       # Remove/cancel option
POST   /api/v1/options/{id}/exercise  # Mark option as exercised

# County RFPs (Monitored)
GET    /api/v1/rfps               # List detected RFPs from scraping
GET    /api/v1/rfps/{id}          # RFP details
POST   /api/v1/rfps/{id}/bid      # Calculate and submit bid

# Bid Management
GET    /api/v1/bids               # Your submitted bids
POST   /api/v1/bids               # Create new bid
GET    /api/v1/bids/{id}          # Bid details
PUT    /api/v1/bids/{id}/status   # Update bid status (awarded/rejected)

# Portfolio Analytics
GET    /api/v1/portfolio/summary  # Portfolio overview
GET    /api/v1/portfolio/p-l      # Profit/loss analysis
GET    /api/v1/portfolio/expiring # Options expiring soon

# Supplier Reference Data (Not Users)
GET    /api/v1/suppliers          # List supplier contacts
POST   /api/v1/suppliers          # Add supplier contact
PUT    /api/v1/suppliers/{id}     # Update supplier info

# Materials Reference Data
GET    /api/v1/materials          # List materials and current prices
```

### Database (Simplified Schema)

**Core Tables:**

1. **users** - H.H. Holdings team members
2. **options_contracts** - Your purchased options
3. **rfps** - Detected county RFPs
4. **bids** - Your submitted bids
5. **suppliers** - Supplier contact information (reference data)
6. **materials** - Material types and specs (reference data)
7. **price_history** - Track spot prices over time

**Removed:**
- Multi-tenant features
- Supplier login/authentication
- Commissioner login/authentication
- Public marketplace features

---

## Revised Deployment Priorities

### Phase 1: Core Internal Tool (1-2 days)

**Essential Features:**
1. ✅ H.H. Holdings team login
2. ✅ Options portfolio view
3. ✅ Add/edit/remove options manually
4. ✅ County RFP list view
5. ✅ Basic bid calculator
6. ✅ Options expiry alerts

**Skip for Now:**
- Public dashboards
- Supplier portals
- Multi-tenant auth
- Complex marketplace features

### Phase 2: Automation (2-3 days)

**Automated Features:**
1. ✅ County commissioners court scrapers
2. ✅ RFP detection and alerts
3. ✅ Email notifications
4. ✅ Option expiry monitoring
5. ✅ TxDOT price tracking

### Phase 3: Advanced Features (3-4 days)

**Power Features:**
1. ✅ Bid document generation
2. ✅ Portfolio analytics and P&L
3. ✅ Historical pricing data
4. ✅ Supplier relationship tracking
5. ✅ Win/loss tracking on bids

---

## Simplified Tech Stack

```
Frontend:  Single internal dashboard (HTML/CSS/JS with Bloomberg styling)
Backend:   FastAPI with simplified endpoints
Database:  PostgreSQL with 7 core tables
Auth:      Simple JWT for H.H. Holdings team
Alerts:    Email notifications for RFPs and expiring options
Scrapers:  County website monitoring
```

---

## Key Differences from Original Design

### REMOVED:
- ❌ Public marketplace features
- ❌ Supplier login portals
- ❌ Commissioner dashboards
- ❌ Multi-tenant architecture
- ❌ Public API for third parties
- ❌ Complex options trading marketplace

### SIMPLIFIED:
- ✅ Single company use (H.H. Holdings only)
- ✅ Manual option entry (after offline deals)
- ✅ Reference data for suppliers (not users)
- ✅ Automated RFP monitoring (not posting)
- ✅ Internal bid management

### FOCUSED ON:
- ✅ Your procurement operations
- ✅ Your options portfolio
- ✅ Your competitive advantage
- ✅ Your bid submissions
- ✅ Your P&L tracking

---

## Business Logic (Revised)

### How You Make Money:

1. **Purchase Options from Suppliers**
   - Call Clifton Quarry: "Lock in 500 tons road base at $28.50 for 90 days"
   - Pay premium: $2/ton = $1,000 upfront
   - Enter into BCMCE system

2. **Monitor County RFPs**
   - BCMCE scrapes commissioners court minutes
   - Detects: "Bosque County needs 500 tons road base"
   - Alerts you immediately

3. **Submit Competitive Bid**
   - Your cost: $28.50 (strike) + $2 (premium) = $30.50/ton
   - Current market: $35/ton
   - Your bid: $33.50/ton (below market, still profitable)
   - County saves $1.50/ton vs market
   - You profit: $3/ton = $1,500 on this deal

4. **Execute**
   - County awards bid to you
   - Exercise option with supplier at $28.50
   - Supplier delivers to county
   - County pays you $33.50/ton
   - Net profit: $1,500 (minus any delivery/admin costs)

---

## Security & Access

**Access Control:**
- Platform accessible only by H.H. Holdings team
- Username/password authentication
- No public signup
- No API keys for third parties
- Hosted internally or with strict access controls

**Data Privacy:**
- Your options portfolio is private
- Your bid strategies are private
- Supplier relationships are confidential
- Only your team sees the data

---

## Next Steps for Development

### Immediate Actions:

1. **Simplify Authentication**
   - Remove multi-tenant features
   - Create H.H. Holdings user accounts
   - Simple admin/user roles

2. **Build Internal Dashboard**
   - Portfolio view
   - Active RFPs
   - Bid calculator
   - Options list

3. **Manual Option Entry**
   - Form to add options after phone deals
   - Track all option details
   - Calculate cost basis for bids

4. **County RFP Monitoring**
   - Set up scrapers for target counties
   - Alert system for new RFPs
   - Match RFPs to available options

---

```
════════════════════════════════════════════════════════════════════════════════
                   BCMCE - INTERNAL PROCUREMENT TOOL
                     For H.H. Holdings Operations Only
                           PROPRIETARY SYSTEM
════════════════════════════════════════════════════════════════════════════════
```

**This is YOUR tool to win county materials contracts using options-based procurement.**

© 2026 HH Holdings LLC / Bevans Real Estate - Proprietary and Confidential
