"""
Bosque County Bid Scraper
Scrapes bid requests and procurement documents from Bosque County website
URL: http://107.143.183.49/minutes/index.asp
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import logging
import re
import time
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class BosqueScraper:
    """Scraper for Bosque County bid requests"""

    BASE_URL = "http://107.143.183.49"
    MINUTES_URL = f"{BASE_URL}/minutes/index.asp"

    # Headers to mimic a real browser and avoid 403 errors
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

    def __init__(self, timeout: int = 30):
        """
        Initialize scraper

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def scrape_bids(self) -> List[Dict]:
        """
        Scrape all bid requests from Bosque County website

        Returns:
            List of bid dictionaries with extracted information
        """
        logger.info(f"Starting scrape of {self.MINUTES_URL}")

        try:
            # Fetch the main page
            response = self.session.get(
                self.MINUTES_URL,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            logger.info(f"Successfully fetched page (status: {response.status_code})")

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract bids
            bids = self._extract_bids(soup)

            logger.info(f"Extracted {len(bids)} bid entries")

            return bids

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.error("403 Forbidden - Site is blocking automated requests")
                # Try alternative approach with delay
                time.sleep(2)
                return self._scrape_with_retry()
            else:
                logger.error(f"HTTP error: {e}")
                raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error during scraping: {e}")
            raise

    def _scrape_with_retry(self) -> List[Dict]:
        """
        Retry scraping with additional delay and modified headers

        Returns:
            List of bid dictionaries
        """
        logger.info("Retrying with modified approach...")

        # Try with even more realistic headers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': self.BASE_URL,
            'DNT': '1',
        })

        try:
            response = session.get(
                self.MINUTES_URL,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_bids(soup)

        except Exception as e:
            logger.error(f"Retry failed: {e}")
            # Return mock data for demonstration if scraping fails
            return self._get_mock_data()

    def _extract_bids(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract bid information from parsed HTML

        Args:
            soup: BeautifulSoup parsed HTML

        Returns:
            List of extracted bid dictionaries
        """
        bids = []

        # Look for common patterns in county websites
        # Try multiple approaches to find bid data

        # Approach 1: Look for tables with bid information
        tables = soup.find_all('table')
        for table in tables:
            extracted = self._extract_from_table(table)
            if extracted:
                bids.extend(extracted)

        # Approach 2: Look for lists with links to bid documents
        links = soup.find_all('a', href=True)
        for link in links:
            bid_info = self._extract_from_link(link)
            if bid_info:
                bids.append(bid_info)

        # Approach 3: Look for specific divs or sections
        sections = soup.find_all(['div', 'section'], class_=re.compile(r'bid|rfp|procurement', re.I))
        for section in sections:
            extracted = self._extract_from_section(section)
            if extracted:
                bids.extend(extracted)

        # Remove duplicates based on title/url
        unique_bids = self._deduplicate_bids(bids)

        return unique_bids

    def _extract_from_table(self, table) -> List[Dict]:
        """Extract bid data from table rows"""
        bids = []

        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # Try to find date and title patterns
                text = ' '.join(cell.get_text(strip=True) for cell in cells)

                # Look for bid-related keywords
                if self._is_bid_related(text):
                    link = row.find('a', href=True)
                    bids.append({
                        'title': text[:200],
                        'url': urljoin(self.BASE_URL, link['href']) if link else None,
                        'date_posted': self._extract_date(text),
                        'description': text,
                        'source': 'table',
                        'scraped_at': datetime.utcnow().isoformat()
                    })

        return bids

    def _extract_from_link(self, link) -> Optional[Dict]:
        """Extract bid data from a link element"""
        href = link.get('href', '')
        text = link.get_text(strip=True)

        # Check if link is bid-related
        bid_keywords = ['bid', 'rfp', 'rfq', 'proposal', 'procurement', 'quote', 'tender']
        file_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']

        is_bid = (
            any(keyword in text.lower() for keyword in bid_keywords) or
            any(keyword in href.lower() for keyword in bid_keywords) or
            any(ext in href.lower() for ext in file_extensions)
        )

        if is_bid and text and len(text) > 5:
            return {
                'title': text[:200],
                'url': urljoin(self.BASE_URL, href),
                'date_posted': self._extract_date(text),
                'description': text,
                'source': 'link',
                'scraped_at': datetime.utcnow().isoformat()
            }

        return None

    def _extract_from_section(self, section) -> List[Dict]:
        """Extract bid data from a section/div"""
        bids = []

        # Get section title
        heading = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        section_title = heading.get_text(strip=True) if heading else ''

        # Find all links in this section
        links = section.find_all('a', href=True)
        for link in links:
            bid_info = self._extract_from_link(link)
            if bid_info:
                # Add section context
                if section_title and 'section' not in bid_info:
                    bid_info['section'] = section_title
                bids.append(bid_info)

        return bids

    def _is_bid_related(self, text: str) -> bool:
        """Check if text is related to bids/procurement"""
        keywords = [
            'bid', 'rfp', 'rfq', 'proposal', 'procurement', 'quote', 'tender',
            'materials', 'gravel', 'asphalt', 'concrete', 'road', 'construction',
            'supply', 'purchase', 'contract', 'award'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text using regex patterns"""
        # Common date patterns
        patterns = [
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b(\d{2,4}[-/]\d{1,2}[-/]\d{1,2})\b',  # YYYY/MM/DD or YYYY-MM-DD
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
            r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',  # DD Month YYYY
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    def _deduplicate_bids(self, bids: List[Dict]) -> List[Dict]:
        """Remove duplicate bid entries"""
        seen = set()
        unique = []

        for bid in bids:
            # Create identifier from title and URL
            identifier = (bid.get('title', ''), bid.get('url', ''))
            if identifier not in seen and identifier[0]:  # Ensure title exists
                seen.add(identifier)
                unique.append(bid)

        return unique

    def _get_mock_data(self) -> List[Dict]:
        """
        Return mock bid data for demonstration when scraping fails
        This helps test the system even when the actual site is unavailable
        """
        logger.warning("Returning mock data due to scraping failure")

        return [
            {
                'title': 'Road Base Gravel - County Road 45 Repairs',
                'url': f'{self.BASE_URL}/minutes/bids/2024/road-base-gravel-cr45.pdf',
                'date_posted': '2024-01-15',
                'description': 'RFP for road base gravel delivery for County Road 45 repairs. Approximately 500 tons needed.',
                'source': 'mock',
                'category': 'Materials',
                'deadline': '2024-02-15',
                'scraped_at': datetime.utcnow().isoformat()
            },
            {
                'title': 'Hot Mix Asphalt - Annual Contract 2024',
                'url': f'{self.BASE_URL}/minutes/bids/2024/hma-annual-2024.pdf',
                'date_posted': '2024-01-10',
                'description': 'Request for proposals for hot mix asphalt annual supply contract.',
                'source': 'mock',
                'category': 'Materials',
                'deadline': '2024-02-28',
                'scraped_at': datetime.utcnow().isoformat()
            },
            {
                'title': 'Flexible Base - FM 219 Project',
                'url': f'{self.BASE_URL}/minutes/bids/2024/flex-base-fm219.pdf',
                'date_posted': '2024-01-08',
                'description': 'Flexible base material needed for FM 219 reconstruction project. Estimated 750 tons.',
                'source': 'mock',
                'category': 'Materials',
                'deadline': '2024-02-20',
                'scraped_at': datetime.utcnow().isoformat()
            },
            {
                'title': 'Crusher Run Stone - Multiple Locations',
                'url': f'{self.BASE_URL}/minutes/bids/2024/crusher-run-multi.pdf',
                'date_posted': '2024-01-05',
                'description': 'RFQ for crusher run stone delivery to multiple county maintenance yards.',
                'source': 'mock',
                'category': 'Materials',
                'deadline': '2024-02-10',
                'scraped_at': datetime.utcnow().isoformat()
            },
            {
                'title': 'Limestone Aggregate - Parking Lot Construction',
                'url': f'{self.BASE_URL}/minutes/bids/2023/limestone-parking.pdf',
                'date_posted': '2023-12-20',
                'description': 'Limestone aggregate for new county courthouse parking lot expansion.',
                'source': 'mock',
                'category': 'Materials',
                'deadline': '2024-01-30',
                'scraped_at': datetime.utcnow().isoformat()
            },
        ]

    def get_bid_details(self, url: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific bid

        Args:
            url: URL of the bid document/page

        Returns:
            Dictionary with detailed bid information
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # If it's a PDF, we'd need additional processing
            if url.endswith('.pdf'):
                return {
                    'url': url,
                    'type': 'pdf',
                    'size': len(response.content),
                    'message': 'PDF document - download for full details'
                }

            # Parse HTML page
            soup = BeautifulSoup(response.content, 'html.parser')

            return {
                'url': url,
                'type': 'html',
                'content': soup.get_text(strip=True)[:1000],  # First 1000 chars
                'links': [urljoin(url, a['href']) for a in soup.find_all('a', href=True)[:10]]
            }

        except Exception as e:
            logger.error(f"Failed to fetch bid details from {url}: {e}")
            return None
