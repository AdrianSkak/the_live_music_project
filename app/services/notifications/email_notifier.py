from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage


@dataclass(frozen=True, slots=True)
class EmailConfig:
    smtp_host: str
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    sender: str
    recipients: list[str]
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> "EmailConfig":
        recipients = [
            value.strip()
            for value in os.getenv("ALERT_EMAIL_TO", "").split(",")
            if value.strip()
        ]

        return cls(
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=os.getenv("SMTP_USERNAME") or None,
            smtp_password=os.getenv("SMTP_PASSWORD") or None,
            sender=os.getenv("ALERT_EMAIL_FROM", ""),
            recipients=recipients,
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"},
        )

    def validate(self) -> None:
        missing = []
        if not self.smtp_host:
            missing.append("SMTP_HOST")
        if not self.sender:
            missing.append("ALERT_EMAIL_FROM")
        if not self.recipients:
            missing.append("ALERT_EMAIL_TO")

        if missing:
            raise ValueError(f"Missing email configuration: {', '.join(missing)}")


def build_email_message(
    config: EmailConfig,
    subject: str,
    body: str,
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = config.sender
    message["To"] = ", ".join(config.recipients)
    message["Subject"] = subject
    message.set_content(body)
    return message


def send_email(config: EmailConfig, subject: str, body: str) -> None:
    config.validate()
    message = build_email_message(config, subject, body)

    with smtplib.SMTP(config.smtp_host, config.smtp_port) as smtp:
        if config.use_tls:
            smtp.starttls()
        if config.smtp_username and config.smtp_password:
            smtp.login(config.smtp_username, config.smtp_password)
        smtp.send_message(message)
