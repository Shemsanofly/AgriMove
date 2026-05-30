"""Africa's Talking SMS — sandbox (AgriMove AI).

Uses the official africastalking SDK (same as AT docs) with a small patch so
HTTP works on Windows where `requests` SSL fails against api.sandbox.africastalking.com.
"""

from __future__ import print_function

import json
import re
from datetime import datetime
from pathlib import Path

import urllib3
from dotenv import load_dotenv

_ENV_FILE = Path(__file__).resolve().parent / ".env"
_HTTP = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", timeout=urllib3.Timeout(connect=10, read=30))

SIMULATOR_URL = "https://simulator.africastalking.com:1517/"
SANDBOX_SMS_OUTBOX_URL = "https://account.africastalking.com/apps/sandbox/sms/outbox"
SANDBOX_REGISTER_PHONE_URL = "https://account.africastalking.com/apps/sandbox/sms/phone-numbers"

_AT_PHONE_RE = re.compile(r"^\+\d{1,3}\d{3,}$")
_REQUESTS_PATCHED = False


def _load_at_credentials():
    """Read Africa's Talking credentials from the project .env file."""
    username = "sandbox"
    api_key = ""
    sender_id = None

    if not _ENV_FILE.exists():
        return username, api_key, sender_id

    for line in _ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key == "AT_USERNAME" and value:
            username = value
        elif key == "AT_API_KEY" and value:
            api_key = value
        elif key == "AT_SENDER_ID" and value:
            sender_id = value

    load_dotenv(_ENV_FILE, override=True)
    return username, api_key, sender_id


def _patch_requests_for_at():
    """Route Africa's Talking API calls through urllib3 (fixes Windows SSL errors)."""
    global _REQUESTS_PATCHED
    if _REQUESTS_PATCHED:
        return

    import requests
    from urllib.parse import urlencode

    _orig_post = requests.post
    _orig_get = requests.get

    def _wrap_response(r):
        class Response:
            status_code = r.status
            text = r.data.decode("utf-8", errors="replace")
            headers = r.headers

            def json(self):
                return json.loads(self.text)

        return Response()

    def _post(url, headers=None, data=None, **kwargs):
        if "africastalking.com" in str(url):
            h = dict(headers or {})
            if isinstance(data, dict):
                body = urlencode(data)
                h.setdefault("Content-Type", "application/x-www-form-urlencoded")
                r = _HTTP.request("POST", url, headers=h, body=body)
            else:
                r = _HTTP.request("POST", url, headers=h, body=data)
            return _wrap_response(r)
        return _orig_post(url, headers=headers, data=data, **kwargs)

    def _get(url, headers=None, params=None, **kwargs):
        if "africastalking.com" in str(url):
            h = dict(headers or {})
            r = _HTTP.request("GET", url, headers=h, fields=params or {})
            return _wrap_response(r)
        return _orig_get(url, headers=headers, params=params, **kwargs)

    requests.post = _post
    requests.get = _get
    _REQUESTS_PATCHED = True


def verify_at_credentials():
    """Check if Africa's Talking accepts the credentials in .env."""
    username, api_key, _ = _load_at_credentials()
    if not api_key:
        return False, "AT_API_KEY missing in .env"

    base = (
        "https://api.sandbox.africastalking.com/version1"
        if username == "sandbox"
        else "https://api.africastalking.com/version1"
    )
    try:
        response = _HTTP.request(
            "GET",
            base + "/user",
            headers={"Accept": "application/json", "apiKey": api_key},
            fields={"username": username},
        )
        if response.status == 200:
            return True, "Credentials valid"
        return False, f"HTTP {response.status}: {response.data.decode('utf-8', errors='replace')}"
    except Exception as exc:
        return False, str(exc)


class SMS:
    """Africa's Talking bulk SMS client — matches official AT sample code."""

    def __init__(self):
        _patch_requests_for_at()
        self.username, self.api_key, self.sender_id = _load_at_credentials()
        self.sms = None
        self.ready = False

        if not self.api_key:
            print("AT_API_KEY is not set in .env")
            return

        try:
            import africastalking

            africastalking.initialize(self.username, self.api_key)
            self.sms = africastalking.SMS
            self.ready = True
            print("Africa's Talking SMS SDK initialized (username: %s)." % self.username)
        except Exception as exc:
            print("Africa's Talking SDK init failed: %s" % exc)

    def send(self, message, recipients, sender_id=None):
        if isinstance(recipients, str):
            recipients = [recipients]

        if not self.ready or not self.sms:
            return {
                "success": False,
                "mode": "africas_talking",
                "recipients": recipients,
                "message": message,
                "error": "SMS not ready — set AT_USERNAME=sandbox and AT_API_KEY in .env",
            }

        for phone in recipients:
            if not _AT_PHONE_RE.match(phone):
                return {
                    "success": False,
                    "mode": "africas_talking",
                    "recipients": recipients,
                    "message": message,
                    "error": "Invalid phone number: %s" % phone,
                }

        sender = sender_id or self.sender_id
        try:
            if sender:
                response = self.sms.send(message, recipients, sender)
            else:
                response = self.sms.send(message, recipients)
            print(response)
            return {
                "success": True,
                "mode": "africas_talking",
                "recipients": recipients,
                "message": message,
                "provider_response": str(response),
                "raw": response,
            }
        except Exception as exc:
            err = str(exc)
            print("Encountered an error while sending: %s" % err)
            return {
                "success": False,
                "mode": "africas_talking",
                "recipients": recipients,
                "message": message,
                "error": err,
            }


_sms = SMS()
sms_client = _sms.sms if _sms.ready else None
sms_status = {
    "enabled": _sms.ready,
    "username": _sms.username,
    "mode": "africas_talking" if _sms.ready else "unconfigured",
    "message": "Africa's Talking SMS SDK initialized successfully." if _sms.ready else "Configure .env",
    "simulator_url": SIMULATOR_URL,
    "sandbox_outbox_url": SANDBOX_SMS_OUTBOX_URL,
    "register_phone_url": SANDBOX_REGISTER_PHONE_URL,
    "credentials_valid": False,
}


def check_simulator_reachable(timeout_seconds=5):
    import socket

    try:
        socket.create_connection(("simulator.africastalking.com", 1517), timeout=timeout_seconds)
        return True
    except OSError:
        return False


def init_sms_client():
    global _sms, sms_client, sms_status
    _sms = SMS()
    sms_client = _sms.sms if _sms.ready else None
    valid, verify_msg = verify_at_credentials()
    sms_status.update(
        {
            "enabled": _sms.ready and valid,
            "username": _sms.username,
            "mode": "africas_talking" if (_sms.ready and valid) else "unconfigured",
            "message": "Africa's Talking SMS ready." if valid else verify_msg,
            "credentials_valid": valid,
        }
    )


def normalize_phone(phone):
    if not phone:
        return None
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    if cleaned.startswith("+"):
        return cleaned
    if cleaned.startswith("255"):
        return f"+{cleaned}"
    if cleaned.startswith("0"):
        return f"+255{cleaned[1:]}"
    if len(cleaned) == 9:
        return f"+255{cleaned}"
    return f"+{cleaned}"


def _parse_at_status(raw_result):
    if not raw_result.get("success"):
        return "failed", raw_result.get("error", "")
    raw = raw_result.get("raw") or raw_result.get("provider_response", "")
    if isinstance(raw, dict):
        sms_data = raw.get("SMSMessageData", {})
        recipients = sms_data.get("Recipients") or []
        if recipients:
            recipient_status = recipients[0].get("status", "")
            status = "sent" if recipient_status.lower() == "success" else recipient_status.lower() or "failed"
            return status, str(raw)
    return "sent", str(raw)


def _is_auth_error(error_text):
    if not error_text:
        return False
    lowered = str(error_text).lower()
    return any(
        token in lowered
        for token in ("401", "authentication", "invalid api", "api key", "unauthorized")
    )


def send_sms(phone, message, request_id=None, conn=None):
    normalized = normalize_phone(phone)
    if not normalized:
        return {"success": False, "mode": sms_status["mode"], "error": "Invalid phone number"}

    result = _sms.send(message, [normalized])

    # If AT rejects the API key, still log for demo/testing (fix key for real sandbox SMS)
    if not result.get("success") and _is_auth_error(result.get("error", "")):
        status, provider_response = "simulated", "API key rejected by Africa's Talking (401). Regenerate key in sandbox dashboard."
        if conn is not None:
            conn.execute(
                """
                INSERT INTO sms_logs (phone, message, status, provider_response, request_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized,
                    message,
                    status,
                    provider_response,
                    request_id,
                    datetime.utcnow().isoformat(timespec="seconds"),
                ),
            )
        return {
            "success": False,
            "mode": "africas_talking",
            "phone": normalized,
            "message": message,
            "provider_response": provider_response,
            "error": result.get("error"),
            "auth_failed": True,
        }

    status, provider_response = _parse_at_status(result)

    if conn is not None:
        conn.execute(
            """
            INSERT INTO sms_logs (phone, message, status, provider_response, request_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                normalized,
                message,
                status,
                provider_response,
                request_id,
                datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )

    return {
        "success": result.get("success", False),
        "mode": result.get("mode", "africas_talking"),
        "phone": normalized,
        "message": message,
        "provider_response": provider_response,
        "error": result.get("error"),
    }


def send_bulk_sms(phones, message, request_id=None, conn=None):
    normalized = [normalize_phone(p) for p in phones if normalize_phone(p)]
    if not normalized:
        return {"success": False, "error": "No valid phone numbers"}

    result = _sms.send(message, normalized)
    status, provider_response = _parse_at_status(result)

    if conn is not None:
        for phone in normalized:
            conn.execute(
                """
                INSERT INTO sms_logs (phone, message, status, provider_response, request_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    phone,
                    message,
                    status,
                    provider_response,
                    request_id,
                    datetime.utcnow().isoformat(timespec="seconds"),
                ),
            )

    return {
        "success": result.get("success", False),
        "mode": result.get("mode", "africas_talking"),
        "phones": normalized,
        "message": message,
        "provider_response": provider_response,
        "error": result.get("error"),
    }


def farmer_transport_sms(lang, request_id, name, pickup, destination, goods_type, quantity, driver_name=None, eta=None):
    if lang == "sw":
        if driver_name and eta:
            return (
                f"AgriMove: Habari {name}, ombi lako #{request_id} limepokelewa. "
                f"Dereva {driver_name} ameteuliwa. ETA: dakika {eta}. "
                f"Mzigo: {quantity} {goods_type}. Kutoka {pickup} hadi {destination}."
            )
        return (
            f"AgriMove: Habari {name}, ombi lako #{request_id} limepokelewa. "
            f"Tunatafuta dereva. Mzigo: {quantity} {goods_type}. "
            f"Kutoka {pickup} hadi {destination}. Utapata SMS utakapopatikana dereva."
        )
    if driver_name and eta:
        return (
            f"AgriMove: Hi {name}, request #{request_id} received. "
            f"Driver {driver_name} assigned. ETA: {eta} mins. "
            f"Load: {quantity} {goods_type}. {pickup} to {destination}."
        )
    return (
        f"AgriMove: Hi {name}, request #{request_id} received. "
        f"Searching for a driver. Load: {quantity} {goods_type}. "
        f"{pickup} to {destination}. You will receive SMS when a driver is matched."
    )


def payment_escrow_farmer_sms(lang, amount_tzs, buyer_name, ref):
    amount = f"{int(amount_tzs):,}"
    if lang == "sw":
        return (
            f"AgriMove Malipo Salama: TSh {amount} kutoka kwa {buyer_name} "
            f"imepokelewa na kuwekwa dhamana. Ref: {ref}."
        )
    return (
        f"AgriMove Secure Pay: TSh {amount} from {buyer_name} "
        f"received and held in escrow. Ref: {ref}."
    )


def payment_escrow_buyer_sms(lang, amount_tzs, farmer_name, ref):
    amount = f"{int(amount_tzs):,}"
    if lang == "sw":
        return (
            f"AgriMove Malipo Salama: Malipo yako ya TSh {amount} kwa {farmer_name} "
            f"yamewekwa dhamana salama. Ref: {ref}."
        )
    return (
        f"AgriMove Secure Pay: Your payment of TSh {amount} to {farmer_name} "
        f"is secured in escrow. Ref: {ref}."
    )


def payment_release_farmer_sms(lang, amount_tzs, ref):
    amount = f"{int(amount_tzs):,}"
    if lang == "sw":
        return (
            f"AgriMove Malipo Salama: TSh {amount} zimeachiwa kutoka dhamana "
            f"na kutumwa kwenye M-Pesa yako. Ref: {ref}."
        )
    return (
        f"AgriMove Secure Pay: TSh {amount} released from escrow to your M-Pesa. Ref: {ref}."
    )


def payment_release_buyer_sms(lang, amount_tzs, farmer_name, ref):
    amount = f"{int(amount_tzs):,}"
    if lang == "sw":
        return (
            f"AgriMove Malipo Salama: Malipo ya TSh {amount} kwa {farmer_name} "
            f"imekamilika na kutolewa kutoka dhamana. Ref: {ref}."
        )
    return (
        f"AgriMove Secure Pay: Payment of TSh {amount} to {farmer_name} "
        f"completed and released from escrow. Ref: {ref}."
    )
