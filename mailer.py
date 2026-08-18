"""Outbound email.

Resend is used because the v2 spec picks it (Phase 8's parent report will want
the same transport). It's called over plain HTTPS rather than adding an SDK —
one endpoint, no dependency.

If RESEND_API_KEY is unset the message is logged instead of sent, and
send_email returns False. Callers must not change their user-visible behaviour
based on that return value: "we sent you a link if that address exists" has to
read identically whether or not mail is configured, or the page becomes an
account-existence oracle.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

log = logging.getLogger(__name__)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "Telos <noreply@telosapp.co.uk>")
MAIL_ENABLED = bool(RESEND_API_KEY)


def send_email(to: str, subject: str, text: str, html: str | None = None) -> bool:
    """Return True only if the provider accepted the message."""
    if not RESEND_API_KEY:
        log.warning("MAIL NOT CONFIGURED — would have sent to %s: %s\n%s",
                    to, subject, text)
        return False

    payload = {"from": MAIL_FROM, "to": [to], "subject": subject, "text": text}
    if html:
        payload["html"] = html

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Cloudflare fronts api.resend.com and blocks the default
            # "Python-urllib/3.x" agent with a 403 / "error code: 1010"
            # that looks exactly like an auth failure. Identify properly.
            "User-Agent": "Telos/1.0 (+https://telosapp.co.uk)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        log.error("Resend rejected the message (%s): %s", e.code, e.read()[:400])
    except Exception as e:                                    # network, DNS, timeout
        log.error("Could not reach Resend: %s", e)
    return False
