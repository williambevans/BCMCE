#!/usr/bin/env python3
"""
Bid matcher - scores solicitations against HHH materials catalog.

Scoring algorithm:
- Keyword match: 0-50 points (number of catalog keywords found in solicitation)
- TxDOT item match: +30 points if TxDOT item number referenced
- County priority: +20 points for Bosque/Hill/Erath (primary focus)
- Deadline urgency: +10 points if deadline within 14 days
- Total: 0-110 points

Score interpretation:
- 80-110: High priority (auto-draft response)
- 60-79: Medium priority (flag for review)
- 40-59: Low priority (monitor)
- 0-39: No match (ignore)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


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


@dataclass
class ScoredSolicitation:
    """Solicitation with match score and analysis."""
    solicitation: Solicitation
    score: int
    matched_materials: List[str]
    matched_txdot_items: List[str]
    priority: str  # "High", "Medium", "Low", "None"


class BidMatcher:
    """Matches solicitations against HHH materials catalog."""

    # County priority tiers
    TIER1_COUNTIES = ["Bosque", "Hill", "Erath"]  # Primary focus
    TIER2_COUNTIES = ["Hamilton", "McLennan", "Comanche", "Somervell", "Coryell"]

    def __init__(self, catalog_path: Path):
        self.catalog = self._load_catalog(catalog_path)
        self.materials = self.catalog['materials']
        self._build_keyword_index()
        self._build_txdot_index()

    def _load_catalog(self, path: Path) -> Dict:
        """Load materials catalog JSON."""
        with open(path, 'r') as f:
            return json.load(f)

    def _build_keyword_index(self):
        """Build keyword index from catalog."""
        self.keyword_to_materials = {}
        for material in self.materials:
            for keyword in material['keywords']:
                keyword = keyword.lower()
                if keyword not in self.keyword_to_materials:
                    self.keyword_to_materials[keyword] = []
                self.keyword_to_materials[keyword].append(material['item'])

    def _build_txdot_index(self):
        """Build TxDOT item number index."""
        self.txdot_to_materials = {}
        for material in self.materials:
            txdot_item = material['txdot_item']
            if txdot_item not in self.txdot_to_materials:
                self.txdot_to_materials[txdot_item] = []
            self.txdot_to_materials[txdot_item].append(material['item'])

    def score_solicitation(self, sol: Solicitation) -> ScoredSolicitation:
        """
        Score solicitation against catalog.

        Returns:
            ScoredSolicitation with score and matched materials
        """
        score = 0
        matched_materials = set()
        matched_txdot_items = set()

        # Combine title and description for matching
        text = f"{sol.title} {sol.description}".lower()

        # Keyword matching (0-50 points)
        keyword_score = 0
        for keyword, materials in self.keyword_to_materials.items():
            if keyword in text:
                keyword_score += 2  # 2 points per keyword
                matched_materials.update(materials)

        score += min(keyword_score, 50)  # Cap at 50

        # TxDOT item number matching (+30 points)
        for txdot_item, materials in self.txdot_to_materials.items():
            # Look for TxDOT item numbers (e.g., "247", "340", "item 247")
            patterns = [
                f"item {txdot_item}",
                f"item#{txdot_item}",
                f"txdot {txdot_item}",
                f"spec {txdot_item}",
                f"\\b{txdot_item}\\b"  # Word boundary match
            ]
            for pattern in patterns:
                if re.search(pattern, text, re.I):
                    score += 30
                    matched_txdot_items.add(txdot_item)
                    matched_materials.update(materials)
                    break  # Only count each TxDOT item once

        # County priority boost
        if sol.county in self.TIER1_COUNTIES:
            score += 20
        elif sol.county in self.TIER2_COUNTIES:
            score += 10

        # Deadline urgency boost
        if sol.deadline:
            days_until = (sol.deadline - datetime.now()).days
            if days_until <= 14:
                score += 10

        # Determine priority
        if score >= 80:
            priority = "High"
        elif score >= 60:
            priority = "Medium"
        elif score >= 40:
            priority = "Low"
        else:
            priority = "None"

        return ScoredSolicitation(
            solicitation=sol,
            score=score,
            matched_materials=list(matched_materials),
            matched_txdot_items=list(matched_txdot_items),
            priority=priority
        )

    def match_batch(self, solicitations: List[Solicitation]) -> List[ScoredSolicitation]:
        """
        Score multiple solicitations.

        Returns:
            List of ScoredSolicitation objects, sorted by score (highest first)
        """
        scored = [self.score_solicitation(sol) for sol in solicitations]
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored

    def filter_by_priority(
        self,
        scored_solicitations: List[ScoredSolicitation],
        min_priority: str = "Low"
    ) -> List[ScoredSolicitation]:
        """
        Filter scored solicitations by minimum priority.

        Args:
            min_priority: "High", "Medium", "Low", or "None"

        Returns:
            Filtered list
        """
        priority_order = {"High": 3, "Medium": 2, "Low": 1, "None": 0}
        min_level = priority_order[min_priority]

        return [
            s for s in scored_solicitations
            if priority_order[s.priority] >= min_level
        ]


def solicitation_from_dict(d: Dict) -> Solicitation:
    """Convert dict to Solicitation (handles datetime parsing)."""
    if isinstance(d['deadline'], str):
        d['deadline'] = datetime.fromisoformat(d['deadline'])
    if isinstance(d['discovered_date'], str):
        d['discovered_date'] = datetime.fromisoformat(d['discovered_date'])
    return Solicitation(**d)


if __name__ == '__main__':
    # Test matcher with sample solicitation
    catalog_path = Path(__file__).parent / "catalog.json"
    matcher = BidMatcher(catalog_path)

    # Sample solicitation
    sample = Solicitation(
        source="Test",
        county="Bosque",
        title="Road Base Material - TxDOT Item 247",
        description="Seeking bids for Grade 1 Flex Base and Type A Crushed Limestone for FM 219 repairs",
        deadline=datetime.now() + timedelta(days=10),
        url="https://example.com",
        contact_email="[email protected]",
        contact_phone="(254) 435-2201",
        discovered_date=datetime.now()
    )

    scored = matcher.score_solicitation(sample)
    print(f"Score: {scored.score} ({scored.priority} priority)")
    print(f"Matched materials: {', '.join(scored.matched_materials[:5])}")
    print(f"Matched TxDOT items: {', '.join(scored.matched_txdot_items)}")
