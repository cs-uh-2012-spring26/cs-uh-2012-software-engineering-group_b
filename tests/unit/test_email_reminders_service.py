"""Unit tests for the email reminder service.

These tests isolate service-layer behavior from API endpoints by mocking
network calls and asserting deterministic orchestration logic.
"""

from urllib.error import HTTPError, URLError

import pytest

from app.db.fitness_classes import DATETIME, TITLE, TRAINER_NAME
from app.services import email_reminders as svc


class _FakeResponse:
    """Small fake for SendGrid SDK responses."""

    def __init__(self, status: int):
        self.status_code = status


def test_build_reminder_message_uses_class_fields():
    """Subject/body should contain title, datetime, and trainer name."""
    subject, body = svc._build_reminder_message(
        {
            TITLE: "Morning Yoga",
            DATETIME: "2036-02-20T09:00:00Z",
            TRAINER_NAME: "Alex Trainer",
        }
    )

    assert subject == "Reminder: Morning Yoga starts soon"
    assert "Morning Yoga" in body
    assert "2036-02-20T09:00:00Z" in body
    assert "Alex Trainer" in body


def test_sendgrid_api_key_missing_raises(monkeypatch):
    """Service should fail fast if SendGrid key is missing."""
    monkeypatch.delenv("SENDGRID_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SENDGRID_API_KEY is required"):
        svc._sendgrid_api_key()


def test_normalize_recipients_deduplicates_and_sorts():
    """Normalization should trim, deduplicate, and sort recipients."""
    recipients = svc._normalize_recipients([
        "  z@example.com ",
        "a@example.com",
        "z@example.com",
        "",
        "   ",
    ])

    assert recipients == ["a@example.com", "z@example.com"]


def test_sendgrid_send_email_success(mocker):
    """SendGrid helper should call SDK client once for successful send."""
    mocked_client_cls = mocker.patch("app.services.email_reminders.SendGridAPIClient")
    mocked_client = mocked_client_cls.return_value
    mocked_client.send.return_value = _FakeResponse(202)

    svc._sendgrid_send_email(
        api_key="SG.fake",
        sender_email="noreply@coachly.dev",
        recipient_email="member@example.com",
        subject="Reminder",
        body="Body",
    )

    mocked_client_cls.assert_called_once_with("SG.fake")
    mocked_client.send.assert_called_once()


def test_sendgrid_send_email_rejected_status(mocker):
    """Non-accepted HTTP status from SendGrid should raise runtime error."""
    mocked_client_cls = mocker.patch("app.services.email_reminders.SendGridAPIClient")
    mocked_client = mocked_client_cls.return_value
    mocked_client.send.return_value = _FakeResponse(500)

    with pytest.raises(RuntimeError, match="SendGrid rejected email with status 500"):
        svc._sendgrid_send_email(
            api_key="SG.fake",
            sender_email="noreply@coachly.dev",
            recipient_email="member@example.com",
            subject="Reminder",
            body="Body",
        )


def test_send_class_reminders_empty_recipients_short_circuit(mocker):
    """No recipients should return early without reading API key."""
    mocked_key = mocker.patch("app.services.email_reminders._sendgrid_api_key")

    result = svc.send_class_reminders(recipient_emails=[], fitness_class={})

    assert result == {"sent_count": 0, "recipients": []}
    mocked_key.assert_not_called()


def test_send_class_reminders_success_with_env_sender(monkeypatch, mocker):
    """Service should send once per unique recipient using env sender fallback."""
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.fake")
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "noreply@coachly.dev")
    mocked_send = mocker.patch("app.services.email_reminders._sendgrid_send_email")

    result = svc.send_class_reminders(
        recipient_emails=[" b@example.com ", "a@example.com", "a@example.com"],
        fitness_class={TITLE: "Yoga", DATETIME: "2036-02-20T09:00:00Z", TRAINER_NAME: "Alex"},
    )

    assert result == {"sent_count": 2, "recipients": ["a@example.com", "b@example.com"]}
    assert mocked_send.call_count == 2

    first_call = mocked_send.call_args_list[0].args
    assert first_call[0] == "SG.fake"
    assert first_call[1] == "noreply@coachly.dev"


def test_send_class_reminders_wraps_http_errors(monkeypatch, mocker):
    """HTTP errors from SendGrid helper should be wrapped consistently."""
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.fake")
    mocker.patch(
        "app.services.email_reminders._sendgrid_send_email",
        side_effect=HTTPError("https://api.sendgrid.com", 429, "Rate limited", hdrs=None, fp=None),
    )

    with pytest.raises(RuntimeError, match=r"Unable to send reminder email\(s\)"):
        svc.send_class_reminders(
            recipient_emails=["member@example.com"],
            fitness_class={TITLE: "Yoga", DATETIME: "2036-02-20T09:00:00Z", TRAINER_NAME: "Alex"},
        )


def test_send_class_reminders_wraps_url_errors(monkeypatch, mocker):
    """Network-level URL errors should be wrapped as runtime errors."""
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.fake")
    mocker.patch(
        "app.services.email_reminders._sendgrid_send_email",
        side_effect=URLError("network down"),
    )

    with pytest.raises(RuntimeError, match=r"Unable to send reminder email\(s\)"):
        svc.send_class_reminders(
            recipient_emails=["member@example.com"],
            fitness_class={TITLE: "Yoga", DATETIME: "2036-02-20T09:00:00Z", TRAINER_NAME: "Alex"},
        )

def test_resolve_sender_email_explicit():
    """Should use explicit sender_email when provided."""
    result = svc._resolve_sender_email("explicit@example.com")
    assert result == "explicit@example.com"


def test_resolve_sender_email_env_fallback(monkeypatch):
    """Should use env SENDGRID_FROM_EMAIL when explicit is None."""
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "env@example.com")
    
    result = svc._resolve_sender_email(None)
    assert result == "env@example.com"


def test_resolve_sender_email_default(monkeypatch):
    """Should use default when explicit and env are None."""
    monkeypatch.delenv("SENDGRID_FROM_EMAIL", raising=False)
    
    result = svc._resolve_sender_email(None)
    assert result == "noreply@coachly.dev"

def test_send_single_class_reminder_success(monkeypatch, mocker):
    """send_single_class_reminder should send email and return normalized recipient."""
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.fake")
    mocked_send = mocker.patch("app.services.email_reminders._sendgrid_send_email")
    
    result = svc.send_single_class_reminder(
        recipient_email="  user@example.com  ",
        fitness_class={TITLE: "Yoga", DATETIME: "2036-02-20T09:00:00Z", TRAINER_NAME: "Alex"},
    )
    
    assert result == "user@example.com"
    mocked_send.assert_called_once()


def test_send_single_class_reminder_invalid_recipient(monkeypatch):
    """send_single_class_reminder raises when recipient is empty/invalid."""
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.fake")
    
    with pytest.raises(RuntimeError, match="Recipient email is required"):
        svc.send_single_class_reminder(
            recipient_email="   ",
            fitness_class={TITLE: "Yoga", DATETIME: "2036-02-20T09:00:00Z", TRAINER_NAME: "Alex"},
        )