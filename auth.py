"""
Access control — the single source of truth for paid (Pro) access.

user_is_pro() is deliberately generous around billing hiccups: `past_due` keeps
access (Stripe retries a failed card for ~2 weeks; a student mid-revision should
not be locked out), and access is kept until `current_period_end` actually
passes. Only `canceled` / `unpaid` cut access.
"""
from datetime import datetime, timezone
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def utcnow():
    return datetime.now(timezone.utc)


def user_is_pro(user) -> bool:
    """Single source of truth for paid access."""
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "grandfathered", False):
        return True
    if getattr(user, "subscription_status", None) not in ("active", "trialing", "past_due"):
        return False
    # grace: keep access until the paid period actually ends
    cpe = getattr(user, "current_period_end", None)
    return cpe is None or cpe > utcnow()


def _slug(feature):
    return "-".join("".join(c if c.isalnum() else " " for c in feature.lower()).split())


def requires_pro(feature="This feature"):
    """Gate an entire route behind Pro. Redirects to /subscription with a flash
    naming the feature and a ?from=<slug> param for conversion tracking.

    For inline teasers within an otherwise-free page, use the
    _upgrade_prompt.html partial instead — never a bare 403.
    """
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not user_is_pro(current_user):
                flash(f"{feature} is a Telos Pro feature — upgrade to unlock it.", "error")
                return redirect(url_for("subscription", **{"from": _slug(feature)}))
            return view(*args, **kwargs)
        return wrapped
    return decorator
