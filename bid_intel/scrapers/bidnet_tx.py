#!/usr/bin/env python3
"""
Bidnet Direct scraper for Texas county bids.

Scrapes Bidnet Direct platform (https://www.bidnetdirect.com) for Texas
county solicitations matching HHH materials catalog.

Focus counties:
- Bosque, Hill, Erath, Hamilton, McLennan, Comanche, Somervell, Coryell
"""

import re
from datetime import datetime
from typing import List
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class Solicitation:
    """Standardized solicitation record."""
    source: str
    county: str
    title: str
    description: str
    deadline: datetime
    url: str
    contact_email: str
    contact_phone: str
    discovered_date: datetime


class BidnetScraper:
    """Scraper for Bidnet Direct platform."""

    BASE_URL = "https://www.bidnetdirect.com"
    SEARCH_URL = f"{BASE_URL}/texas/search"

    # Target counties
    TARGET_COUNTIES = [
        "Bosque", "Hill", "Erath", "Hamilton", "McLennan",
        "Comanche", "Somervell", "Coryell"
    ]

    # Materials keywords for filtering
    MATERIALS_KEYWORDS = [
        "aggregate", "gravel", "base", "limestone", "stone",
        "asphalt", "paving", "concrete", "pipe", "drainage",
        "rcp", "hdpe", "soil", "fill", "topsoil", "erosion",
        "geotextile", "striping", "pavement", "caliche", "sand",
        "riprap", "gabion", "txdot", "spec", "material"
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Hamilton Hayduke Holdings Co. Bid Intelligence Bot/1.0'
        })

    def scrape(self) -> List[Solicitation]:
        """
        Scrape Bidnet Direct for Texas county materials solicitations.

        Returns:
            List of Solicitation objects
        """
        solicitations = []

        for county in self.TARGET_COUNTIES:
            try:
                county_sols = self._scrape_county(county)
                solicitations.extend(county_sols)
            except Exception as e:
                print(f"Error scraping Bidnet for {county} County: {e}")

        return solicitations

    def _scrape_county(self, county: str) -> List[Solicitation]:
        """Scrape Bidnet for specific county."""
        solicitations = []

        try:
            # Build search params
            params = {
                'q': f'{county} County Texas',
                'categories': 'Construction,Materials,Public Works'
            }

            response = self.session.get(self.SEARCH_URL, params=params, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse bid listings
            # Note: Selectors are placeholders - need adjustment for actual site
            bid_items = soup.find_all('div', class_=re.compile(r'bid-item|listing-item'))

            for item in bid_items:
                try:
                    sol = self._parse_bid_item(item, county)
                    if sol and self._is_materials_bid(sol):
                        solicitations.append(sol)
                except Exception as e:
                    print(f"Error parsing bid item: {e}")

        except Exception as e:
            print(f"Error in county scrape: {e}")

        return solicitations

    def _parse_bid_item(self, item, county: str) -> Solicitation:
        """Parse individual bid listing item."""
        # Extract title
        title_elem = item.find(['h3', 'h4', 'a'], class_=re.compile(r'title|name'))
        title = title_elem.get_text().strip() if title_elem else "Untitled Bid"

        # Extract description
        desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|summary'))
        description = desc_elem.get_text().strip() if desc_elem else ""

        # Extract deadline
        deadline_elem = item.find(text=re.compile(r'deadline|due|close', re.I))
        deadline = self._parse_deadline(deadline_elem) if deadline_elem else datetime.now()

        # Extract URL
        link_elem = item.find('a', href=True)
        url = self._make_absolute_url(link_elem['href']) if link_elem else self.BASE_URL

        # Extract contact (often not available in listings)
        contact_email = ""
        contact_phone = ""

        return Solicitation(
            source="Bidnet Direct",
            county=county,
            title=title,
            description=description,
            deadline=deadline,
            url=url,
            contact_email=contact_email,
            contact_phone=contact_phone,
            discovered_date=datetime.now()
        )

    def _is_materials_bid(self, sol: Solicitation) -> bool:
        """Check if solicitation matches materials keywords."""
        text = f"{sol.title} {sol.description}".lower()
        return any(keyword in text for keyword in self.MATERIALS_KEYWORDS)

    def _parse_deadline(self, text: str) -> datetime:
        """Parse deadline from text."""
        if not text:
            return datetime.now()

        # Look for date patterns
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, str(text))
            if match:
                try:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY-MM-DD
                        year, month, day = groups
                    else:  # MM/DD/YYYY
                        month, day, year = groups

                    year = int(year)
                    if year < 100:
                        year += 2000

                    return datetime(year, int(month), int(day))
                except:
                    pass

        return datetime.now()

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute."""
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return f"{self.BASE_URL}{url}"
        else:
            return f"{self.BASE_URL}/{url}"


def scrape_bidnet() -> List[Solicitation]:
    """Convenience function to scrape Bidnet Direct."""
    scraper = BidnetScraper()
    return scraper.scrape()


if __name__ == '__main__':
    # Test scraper
    solicitations = scrape_bidnet()
    print(f"Found {len(solicitations)} materials solicitations on Bidnet:")
    for sol in solicitations:
        print(f"  - [{sol.county}] {sol.title}")
