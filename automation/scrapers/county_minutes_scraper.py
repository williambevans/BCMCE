"""
Bosque County Commissioners Court Minutes Scraper
Automatically extracts material requirements from meeting minutes
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import logging
import json

logger = logging.getLogger(__name__)


class CountyMinutesScraper:
    """Scraper for Bosque County Commissioners Court minutes"""

    BASE_URL = "https://www.co.bosque.tx.us"
    MINUTES_URL = f"{BASE_URL}/page/co.commissioners.court"

    MATERIAL_KEYWORDS = [
        "gravel", "road base", "topping", "caliche", "lime", "limestone",
        "asphalt", "hot mix", "flex base", "fill", "clay", "crusher run",
        "cement", "concrete", "road materials", "maintenance materials"
    ]

    QUANTITY_PATTERN = r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(ton|tons|yd|yards|cubic yards)'
    DOLLAR_PATTERN = r'\$\s*(\d+(?:,\d+)?(?:\.\d+)?)'

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BCMCE Material Requirements Bot 1.0'
        })

    def fetch_recent_minutes(self, days_back: int = 90) -> List[Dict]:
        """
        Fetch recent commissioners court minutes

        Args:
            days_back: How many days back to search

        Returns:
            List of meeting minute documents
        """
        logger.info(f"Fetching commissioners court minutes from last {days_back} days")

        try:
            response = self.session.get(self.MINUTES_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links to PDF minutes
            minutes = []
            for link in soup.find_all('a', href=True):
                if 'minutes' in link.text.lower() and '.pdf' in link['href'].lower():
                    minutes.append({
                        'title': link.text.strip(),
                        'url': self._make_absolute_url(link['href']),
                        'date': self._extract_date_from_text(link.text)
                    })

            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_minutes = [
                m for m in minutes
                if m['date'] and m['date'] >= cutoff_date
            ]

            logger.info(f"Found {len(recent_minutes)} recent minute documents")
            return recent_minutes

        except Exception as e:
            logger.error(f"Error fetching minutes: {str(e)}")
            return []

    def extract_material_requirements(self, minutes_doc: Dict) -> List[Dict]:
        """
        Extract material requirements from meeting minutes

        Args:
            minutes_doc: Minutes document metadata

        Returns:
            List of extracted material requirements
        """
        logger.info(f"Extracting requirements from: {minutes_doc['title']}")

        requirements = []

        try:
            # Download PDF
            response = self.session.get(minutes_doc['url'], timeout=30)
            response.raise_for_status()

            # Extract text from PDF (simplified - would use PyPDF2 in production)
            text = self._extract_text_from_pdf(response.content)

            # Search for material mentions
            for material_keyword in self.MATERIAL_KEYWORDS:
                if material_keyword.lower() in text.lower():
                    context = self._get_context_around_keyword(text, material_keyword)

                    requirement = {
                        'source': minutes_doc['title'],
                        'source_url': minutes_doc['url'],
                        'meeting_date': minutes_doc['date'],
                        'material_type': material_keyword,
                        'context': context,
                        'quantity': self._extract_quantity(context),
                        'budget': self._extract_budget(context),
                        'extracted_at': datetime.utcnow()
                    }

                    requirements.append(requirement)

            logger.info(f"Extracted {len(requirements)} requirements")
            return requirements

        except Exception as e:
            logger.error(f"Error extracting requirements: {str(e)}")
            return []

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute"""
        if url.startswith('http'):
            return url
        return f"{self.BASE_URL}{url if url.startswith('/') else '/' + url}"

    def _extract_date_from_text(self, text: str) -> Optional[datetime]:
        """Extract date from text like 'Minutes January 12, 2026'"""
        try:
            # Try common date formats
            date_patterns = [
                r'(\w+ \d{1,2},? \d{4})',  # January 12, 2026
                r'(\d{1,2}/\d{1,2}/\d{4})',  # 01/12/2026
                r'(\d{4}-\d{2}-\d{2})'  # 2026-01-12
            ]

            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    date_str = match.group(1)
                    # Try parsing with different formats
                    for fmt in ['%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%Y-%m-%d']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue

            return None

        except Exception:
            return None

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF content (simplified)"""
        # In production, would use PyPDF2 or pdfplumber
        # For now, return placeholder
        return "Sample minutes text with gravel and road materials mentioned"

    def _get_context_around_keyword(self, text: str, keyword: str, context_chars: int = 300) -> str:
        """Get text context around a keyword"""
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        index = text_lower.find(keyword_lower)
        if index == -1:
            return ""

        start = max(0, index - context_chars)
        end = min(len(text), index + len(keyword) + context_chars)

        return text[start:end]

    def _extract_quantity(self, text: str) -> Optional[Dict]:
        """Extract quantity from text"""
        match = re.search(self.QUANTITY_PATTERN, text, re.IGNORECASE)
        if match:
            return {
                'amount': float(match.group(1).replace(',', '')),
                'unit': match.group(2).lower()
            }
        return None

    def _extract_budget(self, text: str) -> Optional[float]:
        """Extract budget amount from text"""
        match = re.search(self.DOLLAR_PATTERN, text)
        if match:
            return float(match.group(1).replace(',', ''))
        return None


def main():
    """Main execution function"""
    logging.basicConfig(level=logging.INFO)

    scraper = CountyMinutesScraper()

    # Fetch recent minutes
    minutes = scraper.fetch_recent_minutes(days_back=90)

    # Extract requirements from each document
    all_requirements = []
    for minute_doc in minutes:
        requirements = scraper.extract_material_requirements(minute_doc)
        all_requirements.extend(requirements)

    # Save results
    output = {
        'scraped_at': datetime.utcnow().isoformat(),
        'documents_processed': len(minutes),
        'requirements_found': len(all_requirements),
        'requirements': all_requirements
    }

    with open('county_requirements_extracted.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    logger.info(f"Scraping complete. Found {len(all_requirements)} requirements.")
    logger.info(f"Results saved to county_requirements_extracted.json")


if __name__ == "__main__":
    main()
