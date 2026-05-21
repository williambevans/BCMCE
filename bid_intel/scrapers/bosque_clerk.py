#!/usr/bin/env python3
"""
Bosque County Clerk & Commissioner Court scraper.

Scrapes:
- Bosque County Clerk website (https://www.co.bosque.tx.us/page/bosque.Clerk)
- Commissioner Court agendas and bids
- County purchasing announcements

Returns standardized Solicitation objects for matching.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
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


class BosqueClerkScraper:
    """Scraper for Bosque County Clerk and Commissioner Court."""

    BASE_URL = "https://www.co.bosque.tx.us"
    CLERK_PAGE = f"{BASE_URL}/page/bosque.Clerk"
    COMMISSIONER_PAGE = f"{BASE_URL}/page/bosque.Commissioners.Court"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Hamilton Hayduke Holdings Co. Bid Intelligence Bot/1.0'
        })

    def scrape(self) -> List[Solicitation]:
        """
        Scrape Bosque County for procurement solicitations.

        Returns:
            List of Solicitation objects
        """
        solicitations = []

        try:
            # Scrape clerk page
            solicitations.extend(self._scrape_clerk_page())

            # Scrape commissioner court agendas
            solicitations.extend(self._scrape_commissioner_agendas())

        except Exception as e:
            print(f"Error scraping Bosque County: {e}")

        return solicitations

    def _scrape_clerk_page(self) -> List[Solicitation]:
        """Scrape main clerk page for bid announcements."""
        solicitations = []

        try:
            response = self.session.get(self.CLERK_PAGE, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for bid-related links and content
            # Note: Actual selectors will need adjustment based on site structure
            bid_links = soup.find_all('a', href=re.compile(r'bid|rfb|rfp|solicitation', re.I))

            for link in bid_links:
                try:
                    sol = self._parse_bid_link(link)
                    if sol:
                        solicitations.append(sol)
                except Exception as e:
                    print(f"Error parsing bid link: {e}")

        except Exception as e:
            print(f"Error scraping clerk page: {e}")

        return solicitations

    def _scrape_commissioner_agendas(self) -> List[Solicitation]:
        """Scrape commissioner court agendas for procurement items."""
        solicitations = []

        try:
            response = self.session.get(self.COMMISSIONER_PAGE, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for agenda links (typically PDFs)
            agenda_links = soup.find_all('a', href=re.compile(r'\.pdf', re.I))

            for link in agenda_links:
                href = link.get('href')
                if not href:
                    continue

                # Check if agenda is recent (last 60 days)
                link_text = link.get_text()
                if self._is_recent_agenda(link_text):
                    try:
                        # Extract procurement items from agenda
                        # Note: PDF parsing would require additional libraries
                        # For now, flag for manual review
                        sol = Solicitation(
                            source="Bosque County Commissioner Court Agenda",
                            county="Bosque",
                            title=f"Commissioner Court Agenda: {link_text}",
                            description="Manual review required - PDF agenda may contain procurement items",
                            deadline=datetime.now() + timedelta(days=14),
                            url=self._make_absolute_url(href),
                            contact_email="[email protected]",
                            contact_phone="(254) 435-2201",
                            discovered_date=datetime.now()
                        )
                        solicitations.append(sol)
                    except Exception as e:
                        print(f"Error parsing agenda link: {e}")

        except Exception as e:
            print(f"Error scraping commissioner agendas: {e}")

        return solicitations

    def _parse_bid_link(self, link) -> Solicitation:
        """Parse individual bid link into Solicitation."""
        href = link.get('href')
        text = link.get_text().strip()

        # Extract deadline if present in text
        deadline = self._extract_deadline(text)

        return Solicitation(
            source="Bosque County Clerk",
            county="Bosque",
            title=text,
            description=f"Bid opportunity: {text}",
            deadline=deadline or (datetime.now() + timedelta(days=30)),
            url=self._make_absolute_url(href),
            contact_email="[email protected]",
            contact_phone="(254) 435-2201",
            discovered_date=datetime.now()
        )

    def _is_recent_agenda(self, text: str) -> bool:
        """Check if agenda text indicates recent meeting."""
        # Look for date patterns in text
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                try:
                    # Parse date and check if within last 60 days
                    # Simplified logic - would need robust date parsing
                    return True
                except:
                    pass

        return False

    def _extract_deadline(self, text: str) -> datetime:
        """Extract deadline from text if present."""
        # Look for common deadline patterns
        patterns = [
            r'deadline[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'due[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                try:
                    month, day, year = match.groups()
                    year = int(year)
                    if year < 100:
                        year += 2000
                    return datetime(year, int(month), int(day))
                except:
                    pass

        return None

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute."""
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return f"{self.BASE_URL}{url}"
        else:
            return f"{self.BASE_URL}/{url}"


def scrape_bosque() -> List[Solicitation]:
    """Convenience function to scrape Bosque County."""
    scraper = BosqueClerkScraper()
    return scraper.scrape()


if __name__ == '__main__':
    # Test scraper
    solicitations = scrape_bosque()
    print(f"Found {len(solicitations)} solicitations from Bosque County:")
    for sol in solicitations:
        print(f"  - {sol.title} (deadline: {sol.deadline.strftime('%Y-%m-%d')})")
