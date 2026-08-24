"""Run every Telos test suite and report a single verdict.

    railway run python tests/run_all.py

Needs the same environment the app needs (DATABASE_URL, STRIPE_*), because the
integration suites talk to the real Neon database. They create their own rows
and delete them in a finally block — no suite leaves anything behind.

test_canonical_host.py sets CANONICAL_HOST itself, so it must run in its own
process; that's why each suite is a subprocess rather than an import.

Every other suite assumes CANONICAL_HOST is empty (the Flask test client's
default Host header is "localhost", so a real value like "telosapp.co.uk"
makes the canonical-redirect hook 301 every request, which the test client
then refuses to follow). `railway run` injects the real production value
into this whole process tree, so it's stripped back out here for every
suite except the one that wants it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SUITES = [
    ("prediction engine (pure)", "test_prediction.py"),
    ("prediction integration",   "test_prediction_integration.py"),
    ("canonical host / HTTPS",   "test_canonical_host.py"),
    ("mobile-first + mark entry", "test_mobile_first.py"),
    ("password reset",           "test_password_reset.py"),
    ("pricing + Stripe webhook", "test_pricing.py"),
    ("PWA — manifest, sw, offline", "test_pwa.py"),
    ("prescription engine (pure)", "test_prescription.py"),
    ("prescription integration",   "test_prescription_integration.py"),
    ("trend deltas + history",     "test_trend_deltas.py"),
    ("share cards (pure)",         "test_share_cards.py"),
]


def main():
    results = []
    for label, filename in SUITES:
        path = os.path.join(HERE, filename)
        if not os.path.exists(path):
            results.append((label, "MISSING"))
            continue
        env = os.environ.copy()
        if filename != "test_canonical_host.py":
            env.pop("CANONICAL_HOST", None)
        proc = subprocess.run([sys.executable, path], capture_output=True, text=True, env=env)
        ok = proc.returncode == 0
        results.append((label, "PASS" if ok else "FAIL"))
        if not ok:
            print(f"\n===== {label} ({filename}) =====")
            print(proc.stdout[-4000:])
            print(proc.stderr[-2000:])

    print("\n" + "=" * 52)
    for label, status in results:
        print(f"  {status:8} {label}")
    print("=" * 52)

    bad = [l for l, s in results if s != "PASS"]
    print("ALL SUITES PASS" if not bad else f"PROBLEMS: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
