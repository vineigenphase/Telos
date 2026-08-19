import os
"""Password reset flow: behaviour + the security properties that matter."""
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402
from db import get_db  # noqa: E402
from werkzeug.security import check_password_hash, generate_password_hash  # noqa: E402

app = A.app
app.debug = False
fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


c = app.test_client()
uid = None
orig_hash = None
try:
    # Throwaway account so the owner's password is never touched.
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?,?,?)",
            ("reset-test@telos.local", "resettest", generate_password_hash("OriginalPw1!")))
        uid = cur.lastrowid
        orig_hash = db.execute("SELECT password_hash FROM users WHERE id=?", (uid,)).fetchone()["password_hash"]

    # 1. Unknown address gets the same answer as a known one (no account oracle)
    r1 = c.post("/forgot", data={"email": "definitely-not-a-user@telos.local"}, follow_redirects=True)
    r2 = c.post("/forgot", data={"email": "reset-test@telos.local"}, follow_redirects=True)
    check("unknown email -> 200", r1.status_code, 200)
    check("known email -> 200", r2.status_code, 200)
    check("identical response body (no account oracle)", r1.data == r2.data, True)

    # 2. A token row exists, and only its hash is stored
    with get_db() as db:
        row = db.execute("SELECT id, token_hash, used_at, expires_at FROM password_resets "
                         "WHERE user_id=? ORDER BY id DESC LIMIT 1", (uid,)).fetchone()
    check("token row created", row is not None, True)
    check("token_hash is a sha256 hex digest", len(row["token_hash"]), 64)
    check("token starts unused", row["used_at"], None)

    # We can't read the raw token (that's the point), so mint a known one.
    with get_db() as db:
        raw = A._issue_reset(db, uid, "127.0.0.1")
    check("raw token is not what's stored", A._hash_token(raw) != raw, True)
    with get_db() as db:
        stored = db.execute("SELECT token_hash FROM password_resets WHERE user_id=? "
                            "ORDER BY id DESC LIMIT 1", (uid,)).fetchone()["token_hash"]
    check("stored hash matches sha256(raw)", stored, A._hash_token(raw))

    # 3. Issuing a new token kills the older unused one
    with get_db() as db:
        older = db.execute("SELECT used_at FROM password_resets WHERE id=?", (row["id"],)).fetchone()
    check("previous unused token invalidated", older["used_at"] is not None, True)

    # 4. A bad token is rejected
    r = c.get("/reset/not-a-real-token", follow_redirects=True)
    check("garbage token rejected", b"expired or already been used" in r.data, True)

    # 5. The real link renders the form
    r = c.get(f"/reset/{raw}")
    check("valid token renders form", r.status_code, 200)
    check("form asks for confirmation", b'name="confirm"' in r.data, True)
    check("reset page is noindex", b'name="robots" content="noindex"' in r.data, True)

    # 6. Validation
    r = c.post(f"/reset/{raw}", data={"password": "short", "confirm": "short"})
    check("rejects <8 chars", b"at least 8 characters" in r.data, True)
    r = c.post(f"/reset/{raw}", data={"password": "LongEnough1!", "confirm": "Different1!"})
    check("rejects mismatch", b"don&#39;t match" in r.data or b"don't match" in r.data, True)
    with get_db() as db:
        h = db.execute("SELECT password_hash FROM users WHERE id=?", (uid,)).fetchone()["password_hash"]
    check("password unchanged after failed attempts", h == orig_hash, True)

    # 7. Happy path
    r = c.post(f"/reset/{raw}", data={"password": "BrandNewPw9!", "confirm": "BrandNewPw9!"},
               follow_redirects=True)
    check("reset succeeds", b"Password updated" in r.data, True)
    with get_db() as db:
        h = db.execute("SELECT password_hash FROM users WHERE id=?", (uid,)).fetchone()["password_hash"]
    check("new password works", check_password_hash(h, "BrandNewPw9!"), True)
    check("old password no longer works", check_password_hash(h, "OriginalPw1!"), False)

    # 8. Single use
    r = c.get(f"/reset/{raw}", follow_redirects=True)
    check("token can't be reused", b"expired or already been used" in r.data, True)

    # 9. Expiry is enforced
    with get_db() as db:
        raw2 = A._issue_reset(db, uid, None)
        db.execute("UPDATE password_resets SET expires_at=? WHERE user_id=? AND used_at IS NULL",
                   (datetime.now(timezone.utc) - timedelta(minutes=1), uid))
    r = c.get(f"/reset/{raw2}", follow_redirects=True)
    check("expired token rejected", b"expired or already been used" in r.data, True)

    # 10. Login actually works with the new password
    r = c.post("/login", data={"email": "reset-test@telos.local", "password": "BrandNewPw9!"},
               follow_redirects=False)
    check("can log in after reset", r.status_code, 302)

    # 11. The login page offers the link (fresh client — c is logged in by now,
    # so /login would just redirect to the dashboard)
    anon = app.test_client()
    check("login page links to /forgot", b'href="/forgot"' in anon.get("/login").data, True)
    check("/forgot renders for anonymous", anon.get("/forgot").status_code, 200)
finally:
    if uid:
        with get_db() as db:
            db.execute("DELETE FROM password_resets WHERE user_id=?", (uid,))
            db.execute("DELETE FROM users WHERE id=?", (uid,))
        print(f"cleaned up test user {uid}")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
