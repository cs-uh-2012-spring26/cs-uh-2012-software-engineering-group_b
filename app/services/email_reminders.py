from os import environ

from sendgrid import SendGridAPIClient  # pyright: ignore[reportMissingImports]
from sendgrid.helpers.mail import Content, From, Mail, To  # pyright: ignore[reportMissingImports]

from app.db.fitness_classes import DATETIME, TITLE, TRAINER_NAME


def _build_reminder_message(fitness_class: dict) -> tuple[str, str]:
    """Build email subject/body from class metadata."""
    title = str(fitness_class.get(TITLE, "your upcoming class"))
    class_datetime = str(fitness_class.get(DATETIME, "soon"))
    trainer_name = str(fitness_class.get(TRAINER_NAME, "your trainer"))

    subject = f"Reminder: {title} starts soon"
    body = (
        "Hi there,\n\n"
        f"This is a reminder for your upcoming class: {title}.\n"
        f"Date & time: {class_datetime}\n"
        f"Trainer: {trainer_name}\n\n"
        "See you there!\n"
        "Coachly Team"
    )
    return subject, body


def _sendgrid_api_key() -> str:
    """Read and validate SendGrid API key from environment."""
    api_key = (environ.get("SENDGRID_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY is required")
    return api_key


def _normalize_recipients(recipient_emails: list[str]) -> list[str]:
    """Return unique, stripped recipient emails sorted for deterministic behavior."""
    recipients = [email.strip() for email in recipient_emails if isinstance(email, str) and email.strip()]
    return sorted(set(recipients))


def _resolve_sender_email(sender_email: str | None) -> str:
    """Resolve sender with explicit override, env fallback, then default."""
    return sender_email or environ.get("SENDGRID_FROM_EMAIL") or "noreply@coachly.dev"


def _sendgrid_send_email(api_key: str, sender_email: str, recipient_email: str, subject: str, body: str) -> None:
    """Send one email via SendGrid SDK."""
    message = Mail(
        from_email=From(sender_email),
        to_emails=To(recipient_email),
        subject=subject,
        plain_text_content=Content("text/plain", body),
    )

    response = SendGridAPIClient(api_key).send(message)
    status_code = getattr(response, "status_code", None)
    if status_code not in (200, 202):
        raise RuntimeError(f"SendGrid rejected email with status {status_code}")


def send_class_reminders(
    recipient_emails: list[str],
    fitness_class: dict,
    sender_email: str | None = None,
) -> dict:
    """Send one SendGrid email per recipient and return send summary."""
    # Keep orchestration here and delegate smaller concerns to helpers for easier testing.
    unique_recipients = _normalize_recipients(recipient_emails)

    if not unique_recipients:
        return {"sent_count": 0, "recipients": []}

    api_key = _sendgrid_api_key()
    sender = _resolve_sender_email(sender_email)
    subject, body = _build_reminder_message(fitness_class)

    sent_count = 0
    sent_recipients: list[str] = []

    try:
        for recipient in unique_recipients:
            _sendgrid_send_email(api_key, sender, recipient, subject, body)
            sent_count += 1
            sent_recipients.append(recipient)
    except Exception as exc:
        raise RuntimeError(f"Unable to send reminder email(s): {exc}") from exc

    return {"sent_count": sent_count, "recipients": sent_recipients}


def send_single_class_reminder(
    recipient_email: str,
    fitness_class: dict,
    sender_email: str | None = None,
) -> str:
    """Send one class reminder email and return the recipient email on success."""
    normalized_recipients = _normalize_recipients([recipient_email])
    if not normalized_recipients:
        raise RuntimeError("Recipient email is required")

    recipient = normalized_recipients[0]
    api_key = _sendgrid_api_key()
    sender = _resolve_sender_email(sender_email)
    subject, body = _build_reminder_message(fitness_class)
    _sendgrid_send_email(api_key, sender, recipient, subject, body)
    return recipient
