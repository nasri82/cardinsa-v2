from __future__ import annotations
import sys
import smtplib
from email.message import EmailMessage
from typing import Optional
from app.core.settings import settings

class Mailer:
    def send_email(self, *, to: str, subject: str, html: str, text: Optional[str] = None) -> None:
        raise NotImplementedError

class ConsoleMailer(Mailer):
    def send_email(self, *, to: str, subject: str, html: str, text: Optional[str] = None) -> None:
        print("=== EMAIL (ConsoleMailer) ===", file=sys.stderr)
        print(f"To: {to}", file=sys.stderr)
        print(f"Subject: {subject}", file=sys.stderr)
        if text:
            print(f"Text:\n{text}\n", file=sys.stderr)
        print(f"HTML:\n{html}\n", file=sys.stderr)
        print("=== END EMAIL ===", file=sys.stderr)

class SMTPMailer(Mailer):
    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.sender = settings.SMTP_SENDER
        self.use_tls = settings.SMTP_USE_TLS
        self.use_starttls = settings.SMTP_USE_STARTTLS

    def send_email(self, *, to: str, subject: str, html: str, text: Optional[str] = None) -> None:
        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = to
        msg["Subject"] = subject
        if text:
            msg.set_content(text)
            msg.add_alternative(html, subtype="html")
        else:
            msg.set_content("Your email client does not support HTML.")
            msg.add_alternative(html, subtype="html")

        if self.use_tls:
            with smtplib.SMTP_SSL(self.host, self.port) as smtp:
                if self.username:
                    smtp.login(self.username, self.password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(self.host, self.port) as smtp:
                if self.use_starttls:
                    smtp.starttls()
                if self.username:
                    smtp.login(self.username, self.password)
                smtp.send_message(msg)

def get_mailer() -> Mailer:
    """Return a real SMTP mailer if enabled, else a console printer for dev."""
    if getattr(settings, "SMTP_ENABLED", False):
        return SMTPMailer()
    return ConsoleMailer()
