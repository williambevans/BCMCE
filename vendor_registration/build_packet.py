#!/usr/bin/env python3
"""
Hamilton Hayduke Holdings Co. - Vendor Registration Packet Generator

Generates county-specific vendor registration packets with strict compliance:
- Refuses to generate if required [PENDING] fields exist
- No fictional data - all fields must be filled by human
- Honest CIQ Ch. 176 disclosure based on actual relationships
- Print-ready PDF packets for manual delivery (no auto-submission)

Usage:
    python build_packet.py --county bosque
    python build_packet.py --county hill --validate-only
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas


class PendingFieldError(Exception):
    """Raised when required fields contain [PENDING] placeholder."""
    pass


class VendorPacketGenerator:
    def __init__(self, profile_path: Path, county: str):
        self.profile_path = profile_path
        self.county = county.lower()
        self.profile = self._load_profile()
        self.county_template_dir = Path(__file__).parent / f"templates/counties/{self.county}"

    def _load_profile(self) -> Dict[str, Any]:
        """Load and parse company profile JSON."""
        with open(self.profile_path, 'r') as f:
            return json.load(f)

    def validate_no_pending(self) -> List[str]:
        """
        Check for [PENDING] fields in profile.
        Returns list of field paths that are pending.
        """
        pending_fields = []

        def check_dict(d: Dict, path: str = ""):
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str) and "[PENDING]" in value:
                    pending_fields.append(current_path)
                elif isinstance(value, dict):
                    check_dict(value, current_path)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            check_dict(item, f"{current_path}[{i}]")
                        elif isinstance(item, str) and "[PENDING]" in item:
                            pending_fields.append(f"{current_path}[{i}]")

        check_dict(self.profile)
        return pending_fields

    def generate_packet(self, output_path: Path, validate_only: bool = False) -> None:
        """
        Generate complete vendor registration packet.

        Raises:
            PendingFieldError: If any required fields are [PENDING]
        """
        # Strict validation - refuse to generate with pending fields
        pending = self.validate_no_pending()
        if pending:
            error_msg = "GENERATION BLOCKED: Required fields are [PENDING]:\n"
            for field in pending:
                error_msg += f"  - {field}\n"
            error_msg += "\nFill all required fields in company_profile.json before generating packets."
            raise PendingFieldError(error_msg)

        if validate_only:
            print(f"✓ Validation passed for {self.county.upper()} county packet")
            print(f"  Company: {self.profile['company_name']}")
            print(f"  EIN: {self.profile['ein']}")
            print(f"  Principal: {self.profile['principal']['name']}")
            return

        # Build PDF packet
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
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#d4af37'),
            spaceAfter=12,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#d4af37'),
            spaceAfter=10,
            spaceBefore=16
        )

        # Cover page
        story.extend(self._generate_cover_page(styles, title_style))
        story.append(PageBreak())

        # Vendor information form
        story.extend(self._generate_vendor_form(styles, heading_style))
        story.append(PageBreak())

        # W-9 placeholder
        story.extend(self._generate_w9_page(styles, heading_style))
        story.append(PageBreak())

        # Certificate of Insurance placeholder
        story.extend(self._generate_coi_page(styles, heading_style))
        story.append(PageBreak())

        # Conflict of Interest Questionnaire (Form CIQ)
        story.extend(self._generate_ciq_page(styles, heading_style))
        story.append(PageBreak())

        # Form 1295 instructions
        story.extend(self._generate_form1295_page(styles, heading_style))
        story.append(PageBreak())

        # Debarment certification
        story.extend(self._generate_debarment_page(styles, heading_style))
        story.append(PageBreak())

        # References
        story.extend(self._generate_references_page(styles, heading_style))
        story.append(PageBreak())

        # Signature page
        story.extend(self._generate_signature_page(styles, heading_style))

        # Build PDF
        doc.build(story)
        print(f"✓ Generated packet: {output_path}")
        print(f"  County: {self.county.upper()}")
        print(f"  Pages: ~{len([s for s in story if isinstance(s, PageBreak)]) + 1}")

    def _generate_cover_page(self, styles, title_style) -> List:
        """Generate cover letter."""
        elements = []

        # Header
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(self.profile['company_name'], title_style))
        elements.append(Paragraph(
            f"{self.profile['address']['street']}<br/>"
            f"{self.profile['address']['city']}, {self.profile['address']['state']} {self.profile['address']['zip']}<br/>"
            f"{self.profile['email']}",
            ParagraphStyle('address', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)
        ))
        elements.append(Spacer(1, 0.5*inch))

        # Date
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(date_str, styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))

        # County addressing
        county_name = self.county.title()
        elements.append(Paragraph(
            f"{county_name} County Purchasing Department<br/>"
            f"{county_name} County, Texas",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.25*inch))

        # Body
        body_text = f"""
        <b>RE: Vendor Registration – Hamilton Hayduke Holdings Co.</b><br/><br/>

        Dear {county_name} County Purchasing Officer,<br/><br/>

        Hamilton Hayduke Holdings Co. respectfully submits this vendor registration packet for consideration
        under Tex. Loc. Gov't Code Ch. 262 (county purchasing). We are a registered Texas business entity
        providing materials meeting TxDOT specifications for county infrastructure projects.<br/><br/>

        <b>Our Services:</b><br/>
        We source TxDOT-specification materials from Material Producer List (MPL) approved facilities and
        bid county procurement contracts for aggregates, asphalt, concrete, drainage materials, and erosion
        control products.<br/><br/>

        <b>This Packet Includes:</b><br/>
        • Vendor Information Form<br/>
        • IRS Form W-9<br/>
        • Certificate of Insurance<br/>
        • Conflict of Interest Questionnaire (Ch. 176 Form CIQ)<br/>
        • Form 1295 Certificate of Interested Parties (per-contract basis)<br/>
        • Debarment Certification<br/>
        • Business References<br/><br/>

        We request addition to {county_name} County's vendor list for materials procurement solicitations.
        We commit to competitive pricing, TxDOT specification compliance, and timely delivery.<br/><br/>

        Thank you for your consideration. Please contact us with any questions.<br/><br/>

        Respectfully submitted,<br/><br/>

        {self.profile['principal']['name']}<br/>
        {self.profile['principal']['title']}<br/>
        {self.profile['company_name']}
        """

        elements.append(Paragraph(body_text, styles['Normal']))

        return elements

    def _generate_vendor_form(self, styles, heading_style) -> List:
        """Generate vendor information form."""
        elements = []

        elements.append(Paragraph("Vendor Information Form", heading_style))
        elements.append(Spacer(1, 0.2*inch))

        # Company info table
        data = [
            ["Legal Business Name:", self.profile['company_name']],
            ["DBA (if applicable):", self.profile.get('dba') or "N/A"],
            ["Federal EIN:", self.profile['ein']],
            ["TX SOS File Number:", self.profile['sos_file_number']],
            ["TX Comptroller TIN:", self.profile['tx_comptroller_tin']],
            ["", ""],
            ["Business Address:", f"{self.profile['address']['street']}"],
            ["", f"{self.profile['address']['city']}, {self.profile['address']['state']} {self.profile['address']['zip']}"],
            ["", ""],
            ["Phone:", self.profile['phone']],
            ["Email:", self.profile['email']],
            ["Website:", self.profile['website']],
            ["", ""],
            ["Primary Contact:", self.profile['principal']['name']],
            ["Title:", self.profile['principal']['title']],
            ["Contact Email:", self.profile['principal']['email']],
            ["Contact Phone:", self.profile['principal']['phone']],
        ]

        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # NAICS codes
        elements.append(Paragraph("<b>NAICS Codes:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        naics_text = "<br/>".join([f"• {code}" for code in self.profile['naics_codes']])
        elements.append(Paragraph(naics_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        # Services
        elements.append(Paragraph("<b>Services Provided:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        services_text = "<br/>".join([f"• {svc}" for svc in self.profile['services']])
        elements.append(Paragraph(services_text, styles['Normal']))

        return elements

    def _generate_w9_page(self, styles, heading_style) -> List:
        """Generate W-9 placeholder page."""
        elements = []

        elements.append(Paragraph("IRS Form W-9", heading_style))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "<b>Request for Taxpayer Identification Number and Certification</b>",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "A completed IRS Form W-9 is attached on the following page.",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.1*inch))

        elements.append(Paragraph(
            "<i>Note: Attach signed W-9 form before submitting this packet.</i>",
            ParagraphStyle('note', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
        ))

        return elements

    def _generate_coi_page(self, styles, heading_style) -> List:
        """Generate Certificate of Insurance placeholder."""
        elements = []

        elements.append(Paragraph("Certificate of Insurance", heading_style))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "<b>Required Coverage:</b>",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.1*inch))

        coverage = [
            "• General Liability Insurance",
            "• Workers' Compensation Insurance",
            "• Commercial Auto Liability Insurance"
        ]
        elements.append(Paragraph("<br/>".join(coverage), styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "<i>Note: Certificate of Insurance will be provided upon award of contract. "
            "Coverage amounts will meet or exceed county requirements.</i>",
            ParagraphStyle('note', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
        ))

        return elements

    def _generate_ciq_page(self, styles, heading_style) -> List:
        """
        Generate Conflict of Interest Questionnaire (Form CIQ) per Ch. 176.

        CRITICAL: This form requires honest disclosure of relationships with local
        government officers as defined in Tex. Loc. Gov't Code §176.001(1).

        For Bosque County specifically:
        - Principal (Biri) is a constituent and active complainant on county matters
        - Principal is NOT an officer, employee, or family member of a county officer
        - No business or financial relationship exists with county officials
        - Therefore: "No relationship requiring disclosure under §176.003"

        This reasoning is documented in company_profile.json and must be preserved.
        """
        elements = []

        elements.append(Paragraph("Conflict of Interest Questionnaire", heading_style))
        elements.append(Paragraph(
            "Form CIQ — Texas Local Government Code Chapter 176",
            ParagraphStyle('subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
        ))
        elements.append(Spacer(1, 0.2*inch))

        # CIQ disclosure
        ciq_data = self.profile['ciq_176']

        elements.append(Paragraph("<b>Disclosure Statement:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(ciq_data['relationship'], styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        # Reasoning (for internal documentation)
        elements.append(Paragraph("<b>Basis for Disclosure:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(ciq_data['reason'], styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))

        # Legal reference
        elements.append(Paragraph(
            "<b>Legal Standard:</b><br/>"
            "Tex. Loc. Gov't Code §176.003 requires disclosure of employment or business relationships "
            "with local government officers, or family relationships with officers. A 'local government officer' "
            "is defined in §176.001(1) as an officer, employee, or member of governing body. "
            "Constituents and complainants are not officers under this definition.",
            ParagraphStyle('legal', parent=styles['Normal'], fontSize=9)
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Signature block
        elements.append(Paragraph("<b>Vendor Certification:</b>", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(
            f"I, {self.profile['principal']['name']}, certify that the disclosure above is true and "
            f"complete to the best of my knowledge.",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.3*inch))

        sig_data = [
            ["Signature:", "_" * 40, "Date:", "_" * 20],
            ["", "", "", ""],
            ["Printed Name:", self.profile['principal']['name'], "", ""],
            ["Title:", self.profile['principal']['title'], "", ""],
        ]

        sig_table = Table(sig_data, colWidths=[1.2*inch, 2.5*inch, 0.6*inch, 1.2*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(sig_table)

        return elements

    def _generate_form1295_page(self, styles, heading_style) -> List:
        """Generate Form 1295 instructions page."""
        elements = []

        elements.append(Paragraph("Form 1295 Certificate of Interested Parties", heading_style))
        elements.append(Paragraph(
            "Texas Ethics Commission — Per-Contract Requirement",
            ParagraphStyle('subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
        ))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "<b>Notice:</b> Form 1295 is required for each contract or contract amendment with a "
            "governmental entity. This form will be completed on a per-contract basis upon award.",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "<b>Filing Process:</b><br/>"
            "1. Upon contract award, vendor completes Form 1295 online at www.ethics.state.tx.us<br/>"
            "2. Form is submitted electronically and acknowledgment receipt is generated<br/>"
            "3. Vendor provides acknowledgment receipt with contract execution documents<br/>"
            "4. County files acknowledgment with county clerk within 30 days of execution",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "<i>Hamilton Hayduke Holdings Co. will complete Form 1295 for each awarded contract "
            "in compliance with Tex. Gov't Code §2252.908.</i>",
            ParagraphStyle('note', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
        ))

        return elements

    def _generate_debarment_page(self, styles, heading_style) -> List:
        """Generate debarment certification."""
        elements = []

        elements.append(Paragraph("Debarment and Suspension Certification", heading_style))
        elements.append(Spacer(1, 0.2*inch))

        cert_text = f"""
        <b>Certification:</b><br/><br/>

        {self.profile['company_name']} certifies that neither the company nor its principals are presently
        debarred, suspended, proposed for debarment, declared ineligible, or voluntarily excluded from
        participation in transactions by any federal, state, or local governmental entity.<br/><br/>

        The vendor further certifies that it is not presently debarred, suspended, or otherwise excluded
        from or ineligible for participation in federal assistance programs under Executive Order 12549,
        "Debarment and Suspension."<br/><br/>

        <b>Vendor Acknowledgment:</b><br/>
        The vendor agrees to notify {self.county.title()} County immediately if this certification becomes
        untrue at any time during the period of any contract or vendor relationship.
        """

        elements.append(Paragraph(cert_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))

        # Signature block
        sig_data = [
            ["Signature:", "_" * 40, "Date:", "_" * 20],
            ["", "", "", ""],
            ["Printed Name:", self.profile['principal']['name'], "", ""],
            ["Title:", self.profile['principal']['title'], "", ""],
            ["Company:", self.profile['company_name'], "", ""],
        ]

        sig_table = Table(sig_data, colWidths=[1.2*inch, 2.5*inch, 0.6*inch, 1.2*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(sig_table)

        return elements

    def _generate_references_page(self, styles, heading_style) -> List:
        """Generate business references page."""
        elements = []

        elements.append(Paragraph("Business References", heading_style))
        elements.append(Spacer(1, 0.2*inch))

        for i, ref in enumerate(self.profile['references'], 1):
            elements.append(Paragraph(f"<b>Reference {i}:</b>", styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

            ref_data = [
                ["Name:", ref['name']],
                ["Organization:", ref['organization']],
                ["Phone:", ref['phone']],
                ["Email:", ref['email']],
                ["Relationship:", ref['relationship']],
            ]

            ref_table = Table(ref_data, colWidths=[1.5*inch, 4*inch])
            ref_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(ref_table)
            elements.append(Spacer(1, 0.2*inch))

        return elements

    def _generate_signature_page(self, styles, heading_style) -> List:
        """Generate final signature and certification page."""
        elements = []

        elements.append(Paragraph("Vendor Certification and Signature", heading_style))
        elements.append(Spacer(1, 0.2*inch))

        cert_text = f"""
        <b>Vendor Certification:</b><br/><br/>

        I certify that I am authorized to submit this vendor registration on behalf of {self.profile['company_name']}
        and that all information provided in this packet is true, complete, and accurate to the best of my knowledge.<br/><br/>

        I understand that {self.county.title()} County relies on this information for vendor qualification and that
        any material misrepresentation may result in disqualification or contract termination.<br/><br/>

        I acknowledge that vendor registration does not guarantee contract award and that all contracts will be
        awarded in accordance with Tex. Loc. Gov't Code Ch. 262 and county purchasing policies.<br/><br/>

        I agree to comply with all applicable federal, state, and local laws, regulations, and ordinances in the
        performance of any contract awarded by {self.county.title()} County.
        """

        elements.append(Paragraph(cert_text, styles['Normal']))
        elements.append(Spacer(1, 0.4*inch))

        # Signature block
        sig_data = [
            ["Authorized Signature:", "_" * 40, "Date:", "_" * 20],
            ["", "", "", ""],
            ["Printed Name:", self.profile['principal']['name'], "", ""],
            ["", "", "", ""],
            ["Title:", self.profile['principal']['title'], "", ""],
            ["", "", "", ""],
            ["Company:", self.profile['company_name'], "", ""],
        ]

        sig_table = Table(sig_data, colWidths=[1.5*inch, 2.8*inch, 0.6*inch, 1.2*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(sig_table)

        # Footer note
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f"<i>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))

        return elements


def main():
    parser = argparse.ArgumentParser(
        description="Generate vendor registration packet for county procurement"
    )
    parser.add_argument(
        '--county',
        required=True,
        help='County name (e.g., bosque, hill, erath)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Validate profile without generating PDF'
    )

    args = parser.parse_args()

    # Paths
    script_dir = Path(__file__).parent
    profile_path = script_dir / "company_profile.json"
    packets_dir = script_dir / "packets"
    packets_dir.mkdir(exist_ok=True)

    # Output filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"{args.county.lower()}_HHH_VendorRegistration_{date_str}.pdf"
    output_path = packets_dir / output_filename

    try:
        generator = VendorPacketGenerator(profile_path, args.county)
        generator.generate_packet(output_path, validate_only=args.validate_only)

        if not args.validate_only:
            print(f"\n{'='*60}")
            print("MANUAL DELIVERY REQUIRED")
            print(f"{'='*60}")
            print(f"Print and deliver to {args.county.title()} County Purchasing.")
            print("NO AUTO-SUBMISSION. Human review and delivery only.")
            print(f"{'='*60}\n")

    except PendingFieldError as e:
        print(f"\n❌ {e}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error generating packet: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__':
    main()
