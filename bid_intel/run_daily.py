#!/usr/bin/env python3
"""
Daily bid intelligence runner.

Orchestrates:
1. Run all scrapers
2. Match solicitations against catalog
3. Generate daily brief
4. Auto-draft responses for high-priority (score ≥ 80)

Called by GitHub Actions cron at 6 AM and 6 PM Central.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bid_intel.scrapers.bosque_clerk import scrape_bosque
from bid_intel.scrapers.bidnet_tx import scrape_bidnet
from bid_intel.scrapers.publicpurchase import scrape_publicpurchase
from bid_intel.scrapers.ionwave import scrape_ionwave
from bid_intel.matcher import BidMatcher, Solicitation
from bid_intel.brief import BriefGenerator


def run_all_scrapers() -> List[Solicitation]:
    """
    Run all configured scrapers and aggregate results.

    Returns:
        Combined list of all discovered solicitations
    """
    print(f"\n{'='*60}")
    print(f"BID INTELLIGENCE RUN - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print(f"{'='*60}\n")

    all_solicitations = []

    # Bosque County Clerk
    print("Scraping Bosque County Clerk...")
    try:
        bosque_sols = scrape_bosque()
        all_solicitations.extend(bosque_sols)
        print(f"  ✓ Found {len(bosque_sols)} solicitations")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Bidnet Direct
    print("Scraping Bidnet Direct...")
    try:
        bidnet_sols = scrape_bidnet()
        all_solicitations.extend(bidnet_sols)
        print(f"  ✓ Found {len(bidnet_sols)} solicitations")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Public Purchase
    print("Scraping Public Purchase...")
    try:
        pp_sols = scrape_publicpurchase()
        all_solicitations.extend(pp_sols)
        print(f"  ✓ Found {len(pp_sols)} solicitations")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Ion Wave
    print("Scraping Ion Wave...")
    try:
        iw_sols = scrape_ionwave()
        all_solicitations.extend(iw_sols)
        print(f"  ✓ Found {len(iw_sols)} solicitations")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print(f"\nTotal solicitations discovered: {len(all_solicitations)}")
    return all_solicitations


def main():
    """Main execution flow."""
    script_dir = Path(__file__).parent
    catalog_path = script_dir / "catalog.json"
    briefs_dir = script_dir / "briefs"

    # Run scrapers
    solicitations = run_all_scrapers()

    if not solicitations:
        print("\n⚠ No solicitations found. Generating empty brief.\n")

    # Match against catalog
    print("\nMatching against HHH catalog...")
    matcher = BidMatcher(catalog_path)
    scored_solicitations = matcher.match_batch(solicitations)

    # Filter for relevant (Medium+ priority)
    relevant = [s for s in scored_solicitations if s.priority in ["High", "Medium"]]
    high_priority = [s for s in scored_solicitations if s.priority == "High"]

    print(f"  Relevant solicitations: {len(relevant)}")
    print(f"  High priority (≥80): {len(high_priority)}")
    print(f"  Medium priority (60-79): {len([s for s in relevant if s.priority == 'Medium'])}")

    # Generate brief
    print("\nGenerating daily brief...")
    generator = BriefGenerator(briefs_dir)
    generator.generate_brief(scored_solicitations)

    # Auto-draft high-priority responses
    if high_priority:
        print(f"\n{len(high_priority)} high-priority solicitations flagged for auto-draft")
        print("(Auto-draft feature to be implemented in draft_response.py)")

    print(f"\n{'='*60}")
    print("RUN COMPLETE")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
