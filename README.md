# Hamilton Hayduke Holdings Co. — BCMCE Platform

**Registered Texas Vendor** providing materials meeting TxDOT specifications for county procurement under Tex. Loc. Gov't Code Ch. 262.

**Website:** [williambevans.github.io/BCMCE](https://williambevans.github.io/BCMCE)

---

## Platform Overview

The BCMCE (Bosque County Materials & Contracting Exchange) platform is a dual-purpose system:

1. **Public-Facing Website**: Materials catalog and vendor registration portal
2. **Bid Intelligence System**: Automated procurement opportunity discovery and matching

### Critical Compliance Rules

This platform operates under strict compliance constraints:

1. **No Auto-Submission**: The system produces print-ready packets; humans deliver them. Never auto-submit registrations or bids.

2. **No Fictional Data**: All `[PENDING]` fields must be filled by human before packet generation. The generator refuses to build packets with missing data.

3. **Honest Language**: 
   - ❌ Never: "licensed contractor", "TxDOT certified", "certified materials"
   - ✅ Always: "registered vendor", "TxDOT spec-compliant", "meets TxDOT specifications"

4. **CIQ Ch. 176 Honesty**: The Conflict of Interest Questionnaire requires disclosure of relationships with local government officers as defined in §176.001(1). For Bosque County specifically:
   - Principal (Biri) is a constituent and active complainant on county matters
   - Principal is **NOT** an officer, employee, or family member of a county officer
   - No business or financial relationship exists with county officials
   - Therefore: "No relationship requiring disclosure under §176.003"
   - This reasoning is documented in `company_profile.json` and preserved in generated CIQ forms

5. **Bosque Deployment Strategy**: Bosque County is the reference implementation for code purposes. However, **do not auto-submit** a Bosque registration packet from cron jobs. Bosque registration is a manual decision made after reviewing the political landscape.

---

## Platform Components

### Part 1: Public Website

Static HTML site hosted on GitHub Pages with elegant gold/black design.

**Pages:**
- `index.html` — Materials catalog (43 TxDOT items, Bloomberg terminal aesthetic)
- `request-bid.html` — Bid request form for counties
- `supplier-signup.html` — Registration form for mines/aggregates to register HHH as contractor
- `poster.html` — Print-ready promotional poster (8.5" × 11")

**Compliance Updates (2026-05-21):**
- Removed all fictional licensing: "TX-AG-2024-00123" → "Texas SOS Filing: [PENDING]"
- Removed 555 phone numbers: "(254) 555-0100" → "(254) [PENDING]"
- Changed "Licensed Texas Contractor" → "Registered Texas Vendor" globally
- Changed "TxDOT Certified" → "TxDOT Spec-Compliant"
- Added pricing timestamp with JavaScript date
- Added legal disclaimer in footer documenting TxDOT MPL sourcing and Tex. Loc. Gov't Code Ch. 262 basis

### Part 2: Vendor Registration System

Python-based packet generator for county vendor registration.

**Location:** `vendor_registration/`

**Usage:**
```bash
cd vendor_registration

# First: Fill all [PENDING] fields in company_profile.json
# DO NOT run generator until all required fields are filled

# Validate profile without generating
python build_packet.py --county bosque --validate-only

# Generate packet (only works if no PENDING fields)
python build_packet.py --county bosque

# Output: packets/bosque_HHH_VendorRegistration_YYYY-MM-DD.pdf
```

**Generated Packet Includes:**
1. Cover letter addressed to county purchasing
2. Vendor information form
3. IRS Form W-9 placeholder
4. Certificate of Insurance placeholder
5. Conflict of Interest Questionnaire (Ch. 176 Form CIQ) with honest disclosure
6. Form 1295 instructions (per-contract basis)
7. Debarment certification
8. Business references
9. Signature page

**Manual Delivery Required:** Print packet and deliver to county purchasing office. No electronic auto-submission.

**County Templates:** Directory structure created for:
- Bosque (reference implementation)
- Hill, Erath, Hamilton (stubs for future development)
- McLennan, Comanche, Somervell, Coryell (stubs)

### Part 3: Bid Intelligence System

Automated procurement opportunity discovery and matching.

**Location:** `bid_intel/`

**Architecture:**

```
bid_intel/
├── scrapers/
│   ├── bosque_clerk.py      # Bosque County Clerk + Commissioner Court
│   ├── bidnet_tx.py          # Bidnet Direct platform
│   ├── publicpurchase.py     # Public Purchase platform
│   └── ionwave.py            # Ion Wave platform
├── matcher.py                # Scoring algorithm (0-110 points)
├── brief.py                  # PDF + HTML brief generator
├── run_daily.py              # Orchestrator (called by cron)
├── catalog.json              # Materials catalog (43 items)
└── briefs/                   # Generated briefs (PDF + HTML)
    └── latest.html           # Latest brief (GitHub Pages)
```

**Scoring Algorithm (0-110 points):**
- **Keyword match**: 0-50 points (2 points per catalog keyword found)
- **TxDOT item match**: +30 points if TxDOT item number referenced
- **County priority**: +20 for Tier 1 (Bosque/Hill/Erath), +10 for Tier 2
- **Deadline urgency**: +10 if deadline within 14 days

**Priority Levels:**
- **High (80-110)**: Auto-draft recommended (score ≥ 80)
- **Medium (60-79)**: Review recommended
- **Low (40-59)**: Monitor only
- **None (0-39)**: Ignore

**Automation:**
- GitHub Actions cron: 6 AM and 6 PM Central daily
- Scrapes all sources, matches against catalog, generates briefs
- Commits briefs to repo (PDF + HTML + JSON)
- Latest brief always at: `williambevans.github.io/BCMCE/bid_intel/briefs/latest.html`

**Manual Testing:**
```bash
cd bid_intel

# Test individual scrapers
python scrapers/bosque_clerk.py
python scrapers/bidnet_tx.py

# Test matcher
python matcher.py

# Test brief generator
python brief.py

# Run full daily pipeline
python run_daily.py
```

**GitHub Actions Workflow:** `.github/workflows/bid_intel.yml`
- Scheduled runs: `0 12 * * *` (6 AM Central) and `0 0 * * *` (6 PM Central)
- Manual trigger: Available via workflow_dispatch
- Artifact retention: 90 days for PDF briefs

---

## Development Setup

### Local Development

```bash
# Clone repository
git clone https://github.com/williambevans/BCMCE.git
cd BCMCE

# Install vendor registration dependencies
pip install -r vendor_registration/requirements.txt

# Install bid intelligence dependencies
pip install -r bid_intel/requirements.txt

# Serve website locally
python -m http.server 8000
# Visit: http://localhost:8000
```

### Git Workflow

Development branches must follow format: `claude/bcmce-platform-build-<sessionID>`

**Push commands:**
```bash
# Always use -u flag for first push
git push -u origin claude/bcmce-platform-build-nmObJ

# Network retry logic built into automation (4 retries with exponential backoff)
```

**Branch protection:**
- Main branch is protected
- All changes via PR merge through GitHub UI
- Feature branches start with `claude/` prefix

---

## Contact Information

**Company:** Hamilton Hayduke Holdings Co.  
**Address:** 397 Highway 22, Clifton, TX 76634  
**Email:** bids@hhholdings.com  
**Website:** https://williambevans.github.io/BCMCE  

**Texas Registrations:**
- SOS Filing: `[PENDING]`
- TX Comptroller TIN: `[PENDING]`
- TEC Form 1295: Per-contract basis

**Phone:** `[PENDING]` — To be filled before vendor registration

---

## Legal Disclaimers

### Materials Sourcing
HHH is a registered Texas business entity. Materials sourced from TxDOT Material Producer List (MPL) approved producers. HHH bids county procurement contracts pursuant to Tex. Loc. Gov't Code Ch. 262.

### Procurement Compliance
All county procurement activities follow Texas Local Government Code Chapter 262 (county purchasing). Form 1295 Certificate of Interested Parties filed on per-contract basis per Tex. Gov't Code §2252.908.

### Conflict of Interest
Conflict of Interest Questionnaire (Ch. 176 Form CIQ) completed honestly based on actual relationships as defined in Tex. Loc. Gov't Code §176.001(1). See `company_profile.json` for documented reasoning.

---

## Revision History

- **2026-05-21**: Platform compliance overhaul
  - Removed all fictional data (fake licenses, 555 numbers)
  - Updated language (licensed → registered, certified → spec-compliant)
  - Built vendor registration packet generator
  - Built bid intelligence scraping and matching system
  - Deployed GitHub Actions automation

- **2026-05 (Earlier)**: Initial platform build
  - Materials catalog with 43 TxDOT items
  - Bloomberg terminal design aesthetic
  - Request bid and supplier signup pages
  - Print-ready promotional poster

---

## License

© 2026 Hamilton Hayduke Holdings Co. All Rights Reserved.
