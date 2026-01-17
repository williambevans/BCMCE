"""
RFP (Request for Proposal) Detector
Monitors county websites for new RFPs and bid opportunities
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import re
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


class RFPDetector:
    """Detects new RFPs and bid opportunities"""

    COUNTY_URLS = {
        'bosque': 'https://www.co.bosque.tx.us',
        'hill': 'https://www.co.hill.tx.us',
        'mclennan': 'https://www.co.mclennan.tx.us',
        'coryell': 'https://www.coryellcounty.org'
    }

    RFP_KEYWORDS = [
        'rfp', 'request for proposal', 'request for bid', 'rfb',
        'invitation to bid', 'itb', 'bid opportunity',
        'road materials', 'gravel', 'asphalt', 'construction materials'
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BCMCE RFP Monitor 1.0'
        })
        self.seen_rfps = self._load_seen_rfps()

    def _load_seen_rfps(self) -> set:
        """Load previously seen RFPs to avoid duplicates"""
        try:
            with open('seen_rfps.json', 'r') as f:
                data = json.load(f)
                return set(data.get('seen_hashes', []))
        except FileNotFoundError:
            return set()

    def _save_seen_rfps(self):
        """Save seen RFPs to file"""
        with open('seen_rfps.json', 'w') as f:
            json.dump({'seen_hashes': list(self.seen_rfps)}, f)

    def _generate_rfp_hash(self, rfp: Dict) -> str:
        """Generate unique hash for RFP"""
        content = f"{rfp['county']}{rfp['title']}{rfp['posted_date']}"
        return hashlib.md5(content.encode()).hexdigest()

    def scan_county_website(self, county_name: str, base_url: str) -> List[Dict]:
        """
        Scan a county website for RFPs

        Args:
            county_name: County name
            base_url: Base URL of county website

        Returns:
            List of found RFPs
        """
        logger.info(f"Scanning {county_name} County website for RFPs")

        rfps = []

        try:
            # Common RFP page paths
            rfp_paths = [
                '/bids',
                '/rfp',
                '/purchasing',
                '/procurement',
                '/bids-and-rfps',
                '/business-opportunities'
            ]

            for path in rfp_paths:
                url = f"{base_url}{path}"

                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        found_rfps = self._parse_rfp_page(response.text, county_name, url)
                        rfps.extend(found_rfps)
                except requests.RequestException:
                    continue

            logger.info(f"Found {len(rfps)} RFPs on {county_name} County website")
            return rfps

        except Exception as e:
            logger.error(f"Error scanning {county_name} County: {str(e)}")
            return []

    def _parse_rfp_page(self, html: str, county_name: str, url: str) -> List[Dict]:
        """Parse RFP listings from HTML page"""
        soup = BeautifulSoup(html, 'html.parser')
        rfps = []

        # Look for links and text containing RFP keywords
        for element in soup.find_all(['a', 'div', 'p', 'tr']):
            text = element.get_text(strip=True)

            # Check if text contains RFP keywords
            if any(keyword in text.lower() for keyword in self.RFP_KEYWORDS):
                rfp = {
                    'county': county_name,
                    'title': text[:200],  # Limit title length
                    'url': self._extract_link(element, url),
                    'posted_date': self._extract_date(text),
                    'deadline': self._extract_deadline(text),
                    'description': text,
                    'detected_at': datetime.utcnow(),
                    'source_page': url
                }

                # Only add if contains material-related keywords
                if self._is_material_related(text):
                    rfp_hash = self._generate_rfp_hash(rfp)

                    # Only add if not seen before
                    if rfp_hash not in self.seen_rfps:
                        rfps.append(rfp)
                        self.seen_rfps.add(rfp_hash)

        return rfps

    def _extract_link(self, element, base_url: str) -> Optional[str]:
        """Extract link from element"""
        if element.name == 'a' and element.get('href'):
            href = element['href']
            if href.startswith('http'):
                return href
            return f"{base_url.rstrip('/')}/{href.lstrip('/')}"

        # Look for link in children
        link = element.find('a', href=True)
        if link:
            href = link['href']
            if href.startswith('http'):
                return href
            return f"{base_url.rstrip('/')}/{href.lstrip('/')}"

        return base_url

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        # Common date patterns
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\w+ \d{1,2},? \d{4}'  # Month DD, YYYY
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return None

    def _extract_deadline(self, text: str) -> Optional[str]:
        """Extract deadline date from text"""
        deadline_keywords = ['deadline', 'due date', 'due by', 'submit by', 'closing date']

        text_lower = text.lower()
        for keyword in deadline_keywords:
            if keyword in text_lower:
                # Look for date after keyword
                idx = text_lower.index(keyword)
                context = text[idx:idx+100]
                date = self._extract_date(context)
                if date:
                    return date

        return None

    def _is_material_related(self, text: str) -> bool:
        """Check if RFP is related to construction materials"""
        material_keywords = [
            'gravel', 'road base', 'caliche', 'lime', 'limestone',
            'asphalt', 'concrete', 'materials', 'aggregate',
            'road maintenance', 'road repair', 'paving'
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in material_keywords)

    def scan_all_counties(self) -> List[Dict]:
        """
        Scan all configured county websites

        Returns:
            List of all found RFPs
        """
        logger.info("Scanning all county websites for RFPs")

        all_rfps = []

        for county_name, url in self.COUNTY_URLS.items():
            rfps = self.scan_county_website(county_name, url)
            all_rfps.extend(rfps)

        # Save seen RFPs
        self._save_seen_rfps()

        logger.info(f"Total RFPs found: {len(all_rfps)}")
        return all_rfps


def main():
    """Main execution function"""
    logging.basicConfig(level=logging.INFO)

    detector = RFPDetector()

    # Scan all counties
    rfps = detector.scan_all_counties()

    # Save results
    output = {
        'scanned_at': datetime.utcnow().isoformat(),
        'counties_scanned': list(detector.COUNTY_URLS.keys()),
        'rfps_found': len(rfps),
        'new_rfps': rfps
    }

    with open('detected_rfps.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    logger.info(f"RFP detection complete. Found {len(rfps)} new RFPs.")
    logger.info(f"Results saved to detected_rfps.json")

    # Print summary
    if rfps:
        print("\n=== New RFPs Detected ===")
        for rfp in rfps:
            print(f"\n{rfp['county'].upper()} COUNTY")
            print(f"Title: {rfp['title'][:100]}")
            print(f"Posted: {rfp['posted_date'] or 'Unknown'}")
            print(f"Deadline: {rfp['deadline'] or 'Not specified'}")
            print(f"URL: {rfp['url']}")
    else:
        print("\nNo new RFPs detected.")


if __name__ == "__main__":
    main()
