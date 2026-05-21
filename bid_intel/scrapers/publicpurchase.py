#!/usr/bin/env python3
"""
Public Purchase platform scraper for Texas county bids.

Scrapes Public Purchase (https://www.publicpurchase.com) for Texas county
solicitations matching HHH materials catalog.
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


class PublicPurchaseScraper:
    """Scraper for Public Purchase platform."""

    BASE_URL = "https://www.publicpurchase.com"
    TEXAS_URL = f"{BASE_URL}/gems/browse/state?state=TX"

    TARGET_COUNTIES = [
        "Bosque", "Hill", "Erath", "Hamilton", "McLennan",
        "Comanche", "Somervell", "Coryell"
    ]

    MATERIALS_KEYWORDS = [
        "aggregate", "gravel", "base", "limestone", "stone",
        "asphalt", "paving", "concrete", "pipe", "drainage",
        "material", "txdot"
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Hamilton Hayduke Holdings Co. Bid Intelligence Bot/1.0'
        })

    def scrape(self) -> List[Solicitation]:
        """Scrape Public Purchase for Texas county materials bids."""
        solicitations = []

        for county in self.TARGET_COUNTIES:
            try:
                county_sols = self._scrape_county(county)
                solicitations.extend(county_sols)
            except Exception as e:
                print(f"Error scraping Public Purchase for {county}: {e}")

        return solicitations

    def _scrape_county(self, county: str) -> List[Solicitation]:
        """Scrape Public Purchase for specific county."""
        solicitations = []

        try:
            # Search for county
            search_params = {
                'q': f'{county} County',
                'state': 'TX',
                'category': 'Construction'
            }

            response = self.session.get(self.BASE_URL + '/search', params=search_params, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse solicitation listings
            listings = soup.find_all('div', class_=re.compile(r'solicitation|gem-listing'))

            for listing in listings:
                try:
                    sol = self._parse_listing(listing, county)
                    if sol and self._is_materials_bid(sol):
                        solicitations.append(sol)
                except Exception as e:
                    print(f"Error parsing listing: {e}")

        except Exception as e:
            print(f"Error in county scrape: {e}")

        return solicitations

    def _parse_listing(self, listing, county: str) -> Solicitation:
        """Parse individual solicitation listing."""
        title_elem = listing.find(['h3', 'h4', 'a'])
        title = title_elem.get_text().strip() if title_elem else "Untitled"

        desc_elem = listing.find('p', class_=re.compile(r'desc|summary'))
        description = desc_elem.get_text().strip() if desc_elem else ""

        deadline_elem = listing.find(text=re.compile(r'due|deadline', re.I))
        deadline = self._parse_deadline(deadline_elem) if deadline_elem else datetime.now()

        link = listing.find('a', href=True)
        url = self._make_absolute_url(link['href']) if link else self.BASE_URL

        return Solicitation(
            source="Public Purchase",
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


def scrape_publicpurchase() -> List[Solicitation]:
    """Convenience function."""
    scraper = PublicPurchaseScraper()
    return scraper.scrape()


if __name__ == '__main__':
    solicitations = scrape_publicpurchase()
    print(f"Found {len(solicitations)} materials solicitations on Public Purchase")
