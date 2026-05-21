#!/usr/bin/env python3
"""
Ion Wave platform scraper for Texas county bids.

Scrapes Ion Wave (https://www.ionwave.net) for Texas county solicitations.
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


class IonWaveScraper:
    """Scraper for Ion Wave platform."""

    BASE_URL = "https://www.ionwave.net"

    TARGET_COUNTIES = [
        "Bosque", "Hill", "Erath", "Hamilton", "McLennan",
        "Comanche", "Somervell", "Coryell"
    ]

    MATERIALS_KEYWORDS = [
        "aggregate", "gravel", "base", "limestone", "asphalt",
        "concrete", "pipe", "material", "txdot"
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Hamilton Hayduke Holdings Co. Bid Intelligence Bot/1.0'
        })

    def scrape(self) -> List[Solicitation]:
        """Scrape Ion Wave for Texas county materials bids."""
        solicitations = []

        for county in self.TARGET_COUNTIES:
            try:
                county_sols = self._scrape_county(county)
                solicitations.extend(county_sols)
            except Exception as e:
                print(f"Error scraping Ion Wave for {county}: {e}")

        return solicitations

    def _scrape_county(self, county: str) -> List[Solicitation]:
        """Scrape Ion Wave for specific county."""
        solicitations = []

        try:
            # Ion Wave often has county-specific portals
            county_url = f"{self.BASE_URL}/texas/{county.lower()}"

            response = self.session.get(county_url, timeout=15)
            if response.status_code == 404:
                # Try alternative URL structure
                county_url = f"{self.BASE_URL}/PortalBids.aspx?org={county}County"
                response = self.session.get(county_url, timeout=15)

            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse bid listings
            bid_rows = soup.find_all(['tr', 'div'], class_=re.compile(r'bid|solicitation'))

            for row in bid_rows:
                try:
                    sol = self._parse_bid_row(row, county)
                    if sol and self._is_materials_bid(sol):
                        solicitations.append(sol)
                except Exception as e:
                    print(f"Error parsing bid row: {e}")

        except Exception as e:
            print(f"Error in county scrape: {e}")

        return solicitations

    def _parse_bid_row(self, row, county: str) -> Solicitation:
        """Parse individual bid row."""
        # Extract title from link or header
        title_elem = row.find(['a', 'td', 'span'], class_=re.compile(r'title|name|description'))
        title = title_elem.get_text().strip() if title_elem else "Untitled"

        # Extract description if available
        desc_elem = row.find(['td', 'div'], class_=re.compile(r'desc|detail'))
        description = desc_elem.get_text().strip() if desc_elem else ""

        # Extract deadline
        deadline_elem = row.find(['td', 'span'], class_=re.compile(r'due|deadline|close'))
        deadline = self._parse_deadline(deadline_elem.get_text()) if deadline_elem else datetime.now()

        # Extract URL
        link = row.find('a', href=True)
        url = self._make_absolute_url(link['href']) if link else self.BASE_URL

        return Solicitation(
            source="Ion Wave",
            county=county,
            title=title,
            description=description,
            deadline=deadline,
            url=url,
            contact_email="",
            contact_phone="",
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

        match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', str(text))
        if match:
            try:
                month, day, year = match.groups()
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


def scrape_ionwave() -> List[Solicitation]:
    """Convenience function."""
    scraper = IonWaveScraper()
    return scraper.scrape()


if __name__ == '__main__':
    solicitations = scrape_ionwave()
    print(f"Found {len(solicitations)} materials solicitations on Ion Wave")
