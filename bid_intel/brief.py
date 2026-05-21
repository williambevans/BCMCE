#!/usr/bin/env python3
"""
Daily Bid Intelligence Brief generator.

Generates:
1. PDF brief: briefs/YYYY-MM-DD_BidBrief.pdf
2. Latest HTML: briefs/latest.html (for GitHub Pages)
3. Archive JSON: briefs/YYYY-MM-DD_data.json

Brief includes:
- High/Medium priority solicitations
- Match scores and analysis
- Recommended materials to quote
- Next actions
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from matcher import BidMatcher, ScoredSolicitation, Solicitation


class BriefGenerator:
    """Generates daily bid intelligence briefs."""

    def __init__(self, briefs_dir: Path):
        self.briefs_dir = briefs_dir
        self.briefs_dir.mkdir(exist_ok=True)

    def generate_brief(
        self,
        scored_solicitations: List[ScoredSolicitation],
        date: datetime = None
    ) -> None:
        """
        Generate brief in PDF and HTML formats.

        Args:
            scored_solicitations: List of scored solicitations
            date: Brief date (defaults to today)
        """
        date = date or datetime.now()
        date_str = date.strftime("%Y-%m-%d")

        # Filter for relevant solicitations (Medium+ priority)
        relevant = [s for s in scored_solicitations if s.priority in ["High", "Medium"]]

        # Generate PDF
        pdf_path = self.briefs_dir / f"{date_str}_BidBrief.pdf"
        self._generate_pdf(relevant, pdf_path, date)

        # Generate HTML
        html_path = self.briefs_dir / "latest.html"
        self._generate_html(relevant, html_path, date)

        # Save data JSON
        json_path = self.briefs_dir / f"{date_str}_data.json"
        self._save_json(relevant, json_path)

        print(f"✓ Generated brief: {date_str}")
        print(f"  PDF: {pdf_path}")
        print(f"  HTML: {html_path}")
        print(f"  Solicitations: {len(relevant)} (High: {sum(1 for s in relevant if s.priority == 'High')})")

    def _generate_pdf(
        self,
        solicitations: List[ScoredSolicitation],
        output_path: Path,
        date: datetime
    ) -> None:
        """Generate PDF brief."""
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'BriefTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#d4af37'),
            spaceAfter=6,
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'BriefSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#d4af37'),
            spaceAfter=10,
            spaceBefore=16
        )

        # Header
        story.append(Paragraph("Hamilton Hayduke Holdings Co.", title_style))
        story.append(Paragraph("Daily Bid Intelligence Brief", subtitle_style))
        story.append(Paragraph(
            date.strftime("%A, %B %d, %Y"),
            subtitle_style
        ))
        story.append(Spacer(1, 0.3*inch))

        # Executive summary
        high_count = sum(1 for s in solicitations if s.priority == "High")
        medium_count = sum(1 for s in solicitations if s.priority == "Medium")

        summary_text = f"""
        <b>Summary:</b> {len(solicitations)} relevant procurement opportunities identified.<br/>
        • <b>{high_count} High Priority</b> (Score ≥ 80) — Auto-draft recommended<br/>
        • <b>{medium_count} Medium Priority</b> (Score 60-79) — Review recommended<br/>
        """

        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # High priority solicitations
        if high_count > 0:
            story.append(Paragraph("High Priority Opportunities", heading_style))

            for sol_scored in [s for s in solicitations if s.priority == "High"]:
                story.extend(self._format_solicitation(sol_scored, styles))
                story.append(Spacer(1, 0.2*inch))

        # Medium priority solicitations
        if medium_count > 0:
            story.append(Paragraph("Medium Priority Opportunities", heading_style))

            for sol_scored in [s for s in solicitations if s.priority == "Medium"]:
                story.extend(self._format_solicitation(sol_scored, styles))
                story.append(Spacer(1, 0.2*inch))

        # No opportunities message
        if len(solicitations) == 0:
            story.append(Paragraph(
                "<i>No relevant procurement opportunities identified for this period.</i>",
                styles['Normal']
            ))

        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"<i>Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</i>",
            ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))

        doc.build(story)

    def _format_solicitation(self, scored: ScoredSolicitation, styles) -> List:
        """Format single solicitation for PDF."""
        elements = []
        sol = scored.solicitation

        # Title and score
        title_text = f"<b>{sol.title}</b> (Score: {scored.score})"
        elements.append(Paragraph(title_text, styles['Heading3']))

        # Metadata table
        deadline_str = sol.deadline.strftime("%B %d, %Y") if sol.deadline else "Not specified"
        days_until = (sol.deadline - datetime.now()).days if sol.deadline else 0

        meta_data = [
            ["County:", sol.county, "Source:", sol.source],
            ["Deadline:", f"{deadline_str} ({days_until} days)", "Priority:", scored.priority],
        ]

        meta_table = Table(meta_data, colWidths=[1*inch, 2.2*inch, 1*inch, 2.2*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 0.1*inch))

        # Description
        if sol.description:
            elements.append(Paragraph(f"<b>Description:</b> {sol.description[:300]}...", styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

        # Matched materials
        if scored.matched_materials:
            materials_text = ", ".join(scored.matched_materials[:10])
            if len(scored.matched_materials) > 10:
                materials_text += f" (+{len(scored.matched_materials) - 10} more)"
            elements.append(Paragraph(f"<b>Matched Materials:</b> {materials_text}", styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

        # URL
        elements.append(Paragraph(f"<b>URL:</b> <link href='{sol.url}'>{sol.url}</link>", styles['Normal']))

        # Action recommendation
        if scored.priority == "High":
            action = "RECOMMEND: Auto-draft response packet for review"
        else:
            action = "RECOMMEND: Review solicitation details and consider bidding"

        elements.append(Spacer(1, 0.05*inch))
        elements.append(Paragraph(
            f"<i>{action}</i>",
            ParagraphStyle('action', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#d4af37'))
        ))

        return elements

    def _generate_html(
        self,
        solicitations: List[ScoredSolicitation],
        output_path: Path,
        date: datetime
    ) -> None:
        """Generate HTML brief for GitHub Pages."""
        high_count = sum(1 for s in solicitations if s.priority == "High")
        medium_count = sum(1 for s in solicitations if s.priority == "Medium")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Latest Bid Intelligence Brief | Hamilton Hayduke Holdings Co.</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=Montserrat:wght@200;300;400&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'Montserrat', sans-serif;
      background: #0a0a0a;
      color: #f5f5f5;
      padding: 40px 20px;
    }}
    .container {{
      max-width: 1000px;
      margin: 0 auto;
    }}
    .header {{
      text-align: center;
      margin-bottom: 40px;
      padding-bottom: 20px;
      border-bottom: 1px solid rgba(212, 175, 55, 0.3);
    }}
    .company-name {{
      font-family: 'Cormorant Garamond', serif;
      font-size: 36px;
      color: #d4af37;
      margin-bottom: 10px;
    }}
    .brief-title {{
      font-size: 18px;
      color: #888888;
      text-transform: uppercase;
      letter-spacing: 2px;
    }}
    .date {{
      font-size: 14px;
      color: #666666;
      margin-top: 10px;
    }}
    .summary {{
      background: rgba(212, 175, 55, 0.1);
      border-left: 3px solid #d4af37;
      padding: 20px;
      margin-bottom: 40px;
    }}
    .section-title {{
      font-family: 'Cormorant Garamond', serif;
      font-size: 24px;
      color: #d4af37;
      margin: 30px 0 20px;
    }}
    .solicitation {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(212, 175, 55, 0.2);
      padding: 20px;
      margin-bottom: 20px;
    }}
    .sol-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 15px;
    }}
    .sol-title {{
      font-size: 16px;
      font-weight: 400;
      color: #f5f5f5;
      flex: 1;
    }}
    .score {{
      background: #d4af37;
      color: #0a0a0a;
      padding: 4px 12px;
      font-weight: 500;
      font-size: 13px;
      border-radius: 3px;
    }}
    .sol-meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 10px;
      margin-bottom: 15px;
      font-size: 13px;
      color: #888888;
    }}
    .sol-meta strong {{
      color: #d4af37;
    }}
    .description {{
      font-size: 14px;
      line-height: 1.6;
      color: #cccccc;
      margin-bottom: 15px;
    }}
    .matched-materials {{
      font-size: 13px;
      color: #888888;
      margin-bottom: 10px;
    }}
    .action {{
      font-size: 12px;
      color: #d4af37;
      font-style: italic;
      margin-top: 10px;
    }}
    .no-results {{
      text-align: center;
      padding: 60px 20px;
      color: #666666;
    }}
    .footer {{
      text-align: center;
      margin-top: 60px;
      padding-top: 20px;
      border-top: 1px solid rgba(212, 175, 55, 0.2);
      font-size: 11px;
      color: #666666;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="company-name">Hamilton Hayduke Holdings Co.</div>
      <div class="brief-title">Daily Bid Intelligence Brief</div>
      <div class="date">{date.strftime("%A, %B %d, %Y")}</div>
    </div>

    <div class="summary">
      <strong>Summary:</strong> {len(solicitations)} relevant procurement opportunities identified.<br/>
      • <strong>{high_count} High Priority</strong> (Score ≥ 80) — Auto-draft recommended<br/>
      • <strong>{medium_count} Medium Priority</strong> (Score 60-79) — Review recommended
    </div>
"""

        # High priority solicitations
        high_sols = [s for s in solicitations if s.priority == "High"]
        if high_sols:
            html += '    <h2 class="section-title">High Priority Opportunities</h2>\n'
            for scored in high_sols:
                html += self._format_solicitation_html(scored)

        # Medium priority solicitations
        medium_sols = [s for s in solicitations if s.priority == "Medium"]
        if medium_sols:
            html += '    <h2 class="section-title">Medium Priority Opportunities</h2>\n'
            for scored in medium_sols:
                html += self._format_solicitation_html(scored)

        # No results
        if not solicitations:
            html += '    <div class="no-results">No relevant procurement opportunities identified for this period.</div>\n'

        # Footer
        html += f"""
    <div class="footer">
      Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}<br/>
      Hamilton Hayduke Holdings Co. | Automated Bid Intelligence
    </div>
  </div>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html)

    def _format_solicitation_html(self, scored: ScoredSolicitation) -> str:
        """Format single solicitation for HTML."""
        sol = scored.solicitation

        deadline_str = sol.deadline.strftime("%B %d, %Y") if sol.deadline else "Not specified"
        days_until = (sol.deadline - datetime.now()).days if sol.deadline else 0

        materials_text = ", ".join(scored.matched_materials[:10])
        if len(scored.matched_materials) > 10:
            materials_text += f" (+{len(scored.matched_materials) - 10} more)"

        action = "RECOMMEND: Auto-draft response packet for review" if scored.priority == "High" else "RECOMMEND: Review solicitation details and consider bidding"

        html = f"""
    <div class="solicitation">
      <div class="sol-header">
        <div class="sol-title">{sol.title}</div>
        <div class="score">Score: {scored.score}</div>
      </div>
      <div class="sol-meta">
        <div><strong>County:</strong> {sol.county}</div>
        <div><strong>Source:</strong> {sol.source}</div>
        <div><strong>Deadline:</strong> {deadline_str} ({days_until} days)</div>
        <div><strong>Priority:</strong> {scored.priority}</div>
      </div>
"""

        if sol.description:
            desc_preview = sol.description[:300]
            if len(sol.description) > 300:
                desc_preview += "..."
            html += f'      <div class="description">{desc_preview}</div>\n'

        if scored.matched_materials:
            html += f'      <div class="matched-materials"><strong>Matched Materials:</strong> {materials_text}</div>\n'

        html += f'      <div><a href="{sol.url}" style="color: #d4af37; text-decoration: none;">{sol.url}</a></div>\n'
        html += f'      <div class="action">{action}</div>\n'
        html += '    </div>\n'

        return html

    def _save_json(self, solicitations: List[ScoredSolicitation], output_path: Path) -> None:
        """Save solicitations as JSON for archival."""
        data = {
            "date": datetime.now().isoformat(),
            "count": len(solicitations),
            "solicitations": [
                {
                    "title": s.solicitation.title,
                    "county": s.solicitation.county,
                    "source": s.solicitation.source,
                    "deadline": s.solicitation.deadline.isoformat() if s.solicitation.deadline else None,
                    "url": s.solicitation.url,
                    "score": s.score,
                    "priority": s.priority,
                    "matched_materials": s.matched_materials,
                    "matched_txdot_items": s.matched_txdot_items
                }
                for s in solicitations
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == '__main__':
    # Test brief generation with sample data
    from matcher import Solicitation
    from datetime import timedelta

    sample_sol = Solicitation(
        source="Test",
        county="Bosque",
        title="Road Base Material - TxDOT Item 247",
        description="Seeking bids for Grade 1 Flex Base and Type A Crushed Limestone",
        deadline=datetime.now() + timedelta(days=10),
        url="https://example.com",
        contact_email="test@example.com",
        contact_phone="(254) 555-0000",
        discovered_date=datetime.now()
    )

    catalog_path = Path(__file__).parent / "catalog.json"
    matcher = BidMatcher(catalog_path)
    scored = matcher.score_solicitation(sample_sol)

    briefs_dir = Path(__file__).parent / "briefs"
    generator = BriefGenerator(briefs_dir)
    generator.generate_brief([scored])
