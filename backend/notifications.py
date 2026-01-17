"""
Email Notification System
Sends alerts for price changes, option expiries, new bids, etc.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
import logging
from jinja2 import Template
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending notifications
    """

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@bcmce.org")
        self.from_name = "BCMCE Platform"

    def send_email(self, to_email: str, subject: str, html_body: str,
                   text_body: Optional[str] = None) -> bool:
        """
        Send email

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)

        Returns:
            bool: True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text and HTML parts
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))

            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_bulk_email(self, recipients: List[str], subject: str,
                       html_body: str) -> int:
        """
        Send email to multiple recipients

        Args:
            recipients: List of email addresses
            subject: Email subject
            html_body: HTML email body

        Returns:
            int: Number of successfully sent emails
        """
        sent_count = 0

        for email in recipients:
            if self.send_email(email, subject, html_body):
                sent_count += 1

        return sent_count


class NotificationTemplates:
    """
    Email templates for various notifications
    """

    @staticmethod
    def price_change_alert(material_name: str, supplier_name: str,
                          old_price: Decimal, new_price: Decimal) -> dict:
        """
        Price change alert email

        Returns:
            dict: {subject, html_body, text_body}
        """
        change_percent = float((new_price - old_price) / old_price * 100)
        direction = "increased" if new_price > old_price else "decreased"

        html_template = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #1e3c72; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .price-box { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #1e3c72; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>BCMCE Price Alert</h1>
                </div>
                <div class="content">
                    <h2>Price Change Notification</h2>
                    <p>The price for <strong>{{ material_name }}</strong> from <strong>{{ supplier_name }}</strong> has {{ direction }}.</p>

                    <div class="price-box">
                        <p><strong>Previous Price:</strong> ${{ old_price }}/ton</p>
                        <p><strong>New Price:</strong> ${{ new_price }}/ton</p>
                        <p><strong>Change:</strong> {{ change_percent }}%</p>
                    </div>

                    <p>This may be a good time to review your option contracts and procurement plans.</p>

                    <p><a href="https://williambevans.github.io/BCMCE/">View Live Pricing</a></p>
                </div>
                <div class="footer">
                    <p>BCMCE - Bosque County Mineral & Commodities Exchange</p>
                    <p>{{ timestamp }}</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        html_body = template.render(
            material_name=material_name,
            supplier_name=supplier_name,
            old_price=float(old_price),
            new_price=float(new_price),
            change_percent=abs(round(change_percent, 2)),
            direction=direction,
            timestamp=datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")
        )

        text_body = f"""
        BCMCE Price Alert

        The price for {material_name} from {supplier_name} has {direction}.

        Previous Price: ${old_price}/ton
        New Price: ${new_price}/ton
        Change: {abs(round(change_percent, 2))}%

        View live pricing at: https://williambevans.github.io/BCMCE/
        """

        return {
            "subject": f"Price Alert: {material_name} - {direction.title()}",
            "html_body": html_body,
            "text_body": text_body
        }

    @staticmethod
    def option_expiry_alert(contract_number: str, material_name: str,
                           quantity: Decimal, expiration_date: str,
                           days_remaining: int) -> dict:
        """
        Option contract expiry alert

        Returns:
            dict: {subject, html_body, text_body}
        """
        html_template = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #dc3545; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .alert-box { background: #fff3cd; padding: 15px; margin: 15px 0; border-left: 4px solid #ffc107; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Option Contract Expiring Soon</h1>
                </div>
                <div class="content">
                    <h2>Action Required</h2>
                    <p>Your option contract is expiring soon and requires your attention.</p>

                    <div class="alert-box">
                        <p><strong>Contract Number:</strong> {{ contract_number }}</p>
                        <p><strong>Material:</strong> {{ material_name }}</p>
                        <p><strong>Quantity:</strong> {{ quantity }} tons</p>
                        <p><strong>Expiration Date:</strong> {{ expiration_date }}</p>
                        <p><strong>Days Remaining:</strong> {{ days_remaining }}</p>
                    </div>

                    <p>Please review this contract and decide whether to exercise it or let it expire.</p>

                    <p><a href="https://williambevans.github.io/BCMCE/">View Contract Details</a></p>
                </div>
                <div class="footer">
                    <p>BCMCE - Bosque County Mineral & Commodities Exchange</p>
                    <p>{{ timestamp }}</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        html_body = template.render(
            contract_number=contract_number,
            material_name=material_name,
            quantity=float(quantity),
            expiration_date=expiration_date,
            days_remaining=days_remaining,
            timestamp=datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")
        )

        text_body = f"""
        BCMCE Option Contract Expiring Soon

        Contract Number: {contract_number}
        Material: {material_name}
        Quantity: {quantity} tons
        Expiration Date: {expiration_date}
        Days Remaining: {days_remaining}

        Please review this contract and decide whether to exercise it or let it expire.

        View contract details at: https://williambevans.github.io/BCMCE/
        """

        return {
            "subject": f"⚠️ Option Expiring: {contract_number} ({days_remaining} days)",
            "html_body": html_body,
            "text_body": text_body
        }

    @staticmethod
    def new_bid_notification(requirement_number: str, material_name: str,
                            supplier_name: str, quoted_price: Decimal,
                            quantity: Decimal) -> dict:
        """
        New bid received notification

        Returns:
            dict: {subject, html_body, text_body}
        """
        html_template = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #28a745; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .bid-box { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Bid Received</h1>
                </div>
                <div class="content">
                    <h2>Bid Submission</h2>
                    <p>A new bid has been submitted for your material requirement.</p>

                    <div class="bid-box">
                        <p><strong>Requirement:</strong> {{ requirement_number }}</p>
                        <p><strong>Material:</strong> {{ material_name }}</p>
                        <p><strong>Supplier:</strong> {{ supplier_name }}</p>
                        <p><strong>Quoted Price:</strong> ${{ quoted_price }}/ton</p>
                        <p><strong>Quantity:</strong> {{ quantity }} tons</p>
                        <p><strong>Total Value:</strong> ${{ total_value }}</p>
                    </div>

                    <p>Please review this bid in your dashboard.</p>

                    <p><a href="https://williambevans.github.io/BCMCE/">Review Bid</a></p>
                </div>
                <div class="footer">
                    <p>BCMCE - Bosque County Mineral & Commodities Exchange</p>
                    <p>{{ timestamp }}</p>
                </div>
            </div>
        </body>
        </html>
        """

        total_value = float(quoted_price * quantity)

        template = Template(html_template)
        html_body = template.render(
            requirement_number=requirement_number,
            material_name=material_name,
            supplier_name=supplier_name,
            quoted_price=float(quoted_price),
            quantity=float(quantity),
            total_value=total_value,
            timestamp=datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")
        )

        text_body = f"""
        BCMCE New Bid Received

        Requirement: {requirement_number}
        Material: {material_name}
        Supplier: {supplier_name}
        Quoted Price: ${quoted_price}/ton
        Quantity: {quantity} tons
        Total Value: ${total_value}

        Please review this bid in your dashboard at: https://williambevans.github.io/BCMCE/
        """

        return {
            "subject": f"New Bid: {requirement_number} - {supplier_name}",
            "html_body": html_body,
            "text_body": text_body
        }


# Global email service instance
email_service = EmailService()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def send_price_change_alert(to_email: str, material_name: str,
                           supplier_name: str, old_price: Decimal,
                           new_price: Decimal) -> bool:
    """Send price change alert email"""
    template = NotificationTemplates.price_change_alert(
        material_name, supplier_name, old_price, new_price
    )
    return email_service.send_email(
        to_email,
        template["subject"],
        template["html_body"],
        template["text_body"]
    )


def send_option_expiry_alert(to_email: str, contract_number: str,
                            material_name: str, quantity: Decimal,
                            expiration_date: str, days_remaining: int) -> bool:
    """Send option expiry alert email"""
    template = NotificationTemplates.option_expiry_alert(
        contract_number, material_name, quantity,
        expiration_date, days_remaining
    )
    return email_service.send_email(
        to_email,
        template["subject"],
        template["html_body"],
        template["text_body"]
    )


def send_new_bid_notification(to_email: str, requirement_number: str,
                              material_name: str, supplier_name: str,
                              quoted_price: Decimal, quantity: Decimal) -> bool:
    """Send new bid notification email"""
    template = NotificationTemplates.new_bid_notification(
        requirement_number, material_name, supplier_name,
        quoted_price, quantity
    )
    return email_service.send_email(
        to_email,
        template["subject"],
        template["html_body"],
        template["text_body"]
    )


if __name__ == "__main__":
    print("BCMCE Email Notification System")
    print("=" * 50)
    print(f"SMTP Host: {email_service.smtp_host}")
    print(f"SMTP Port: {email_service.smtp_port}")
    print(f"From Email: {email_service.from_email}")
    print("\nEmail service initialized successfully")
