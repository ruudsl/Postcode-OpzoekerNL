#!/usr/bin/env python3
"""
Test script voor PDOK Postcode Opzoeker Web Interface
Test zowel de lokale versie (app.py) als de serverless versie (api/index.py)

Gebruik:
    python test_web.py                          # test http://localhost:5000
    python test_web.py https://example.app      # test een deployment
"""

import sys
import time

import requests

BASE_URL = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else "http://localhost:5000"
TIMEOUT = 10

TEST_ADDRESSES = """Dam 1, AMSTERDAM
Barrierweg 1, EINDHOVEN
Coolsingel 40, ROTTERDAM"""


def test_homepage() -> bool:
    """Home pagina laadt en bevat de app"""
    r = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
    assert r.status_code == 200, f"Status {r.status_code}"
    assert "ostcode" in r.text, "Pagina bevat geen postcode-content"
    return True


def test_health() -> bool:
    """Health endpoint (alleen serverless versie heeft deze)"""
    r = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
    if r.status_code == 404:
        print("   (overgeslagen: /api/health bestaat alleen in serverless versie)")
        return True
    assert r.status_code == 200, f"Status {r.status_code}"
    assert r.json().get('status') == 'ok'
    return True


def test_seo_routes() -> bool:
    """SEO routes: robots.txt, sitemap.xml, llms.txt (serverless versie)"""
    for path, marker in [('/robots.txt', 'User-agent'),
                         ('/sitemap.xml', '<urlset'),
                         ('/llms.txt', 'Postcode')]:
        r = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
        if r.status_code == 404:
            print(f"   (overgeslagen: {path} alleen in serverless versie)")
            continue
        assert r.status_code == 200, f"{path}: status {r.status_code}"
        assert marker in r.text, f"{path}: verwachte inhoud ontbreekt"
    return True


def test_process_sync() -> bool:
    """Synchrone verwerking (serverless: /api/process)"""
    r = requests.post(f"{BASE_URL}/api/process",
                      json={'addresses': TEST_ADDRESSES},
                      timeout=60)
    if r.status_code == 404:
        print("   (overgeslagen: /api/process alleen in serverless versie)")
        return True
    assert r.status_code == 200, f"Status {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert 'results' in data and 'summary' in data
    assert data['summary']['total'] == 3
    print(f"   Gevonden: {data['summary']['found']}/3")
    return True


def test_process_async() -> bool:
    """Asynchrone verwerking met job polling (lokale versie: /api/process-text)"""
    r = requests.post(f"{BASE_URL}/api/process-text",
                      json={'addresses': TEST_ADDRESSES},
                      timeout=TIMEOUT)
    if r.status_code == 404:
        print("   (overgeslagen: /api/process-text alleen in lokale versie)")
        return True
    assert r.status_code == 200, f"Status {r.status_code}"
    job_id = r.json()['job_id']

    deadline = time.time() + 60
    while time.time() < deadline:
        job = requests.get(f"{BASE_URL}/api/status/{job_id}", timeout=TIMEOUT).json()
        if job['status'] == 'completed':
            print(f"   Gevonden: {job['summary']['found']}/{job['summary']['total']}")
            return True
        if job['status'] == 'error':
            raise AssertionError(f"Job error: {job.get('error')}")
        time.sleep(1)
    raise AssertionError("Job niet voltooid binnen 60s")


def test_validation_errors() -> bool:
    """Foutafhandeling: lege input en ongeldige adressen"""
    endpoint = None
    for candidate in ('/api/process', '/api/process-text'):
        r = requests.post(f"{BASE_URL}{candidate}", json={'addresses': ''}, timeout=TIMEOUT)
        if r.status_code != 404:
            endpoint = candidate
            break
    assert endpoint, "Geen process endpoint gevonden"

    # Lege input → 400
    r = requests.post(f"{BASE_URL}{endpoint}", json={'addresses': ''}, timeout=TIMEOUT)
    assert r.status_code == 400, f"Lege input gaf {r.status_code}, verwacht 400"

    # Ongeldige adressen (geen huisnummer) → 400
    r = requests.post(f"{BASE_URL}{endpoint}",
                      json={'addresses': 'dit is geen adres\nook dit niet'},
                      timeout=TIMEOUT)
    assert r.status_code == 400, f"Ongeldige input gaf {r.status_code}, verwacht 400"
    return True


def test_security_headers() -> bool:
    """Security headers aanwezig"""
    r = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
    assert r.headers.get('X-Content-Type-Options') == 'nosniff', \
        "X-Content-Type-Options header ontbreekt"
    assert r.headers.get('X-Frame-Options') == 'DENY', \
        "X-Frame-Options header ontbreekt"
    return True


def main() -> int:
    print("=" * 60)
    print(f"Postcode Opzoeker - Web Interface Tests")
    print(f"Target: {BASE_URL}")
    print("=" * 60)

    # Eerst checken of de server bereikbaar is
    try:
        requests.get(f"{BASE_URL}/", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Server niet bereikbaar op {BASE_URL}")
        print("   Start eerst: python app.py")
        return 1

    tests = [
        ("Homepage", test_homepage),
        ("Health endpoint", test_health),
        ("SEO routes", test_seo_routes),
        ("Verwerking (sync)", test_process_sync),
        ("Verwerking (async)", test_process_async),
        ("Validatie errors", test_validation_errors),
        ("Security headers", test_security_headers),
    ]

    passed = 0
    failed = []

    for name, fn in tests:
        print(f"\n▶ {name}...")
        try:
            fn()
            print(f"  ✅ PASSED")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            failed.append(name)
        except Exception as e:
            print(f"  ❌ ERROR: {type(e).__name__}: {e}")
            failed.append(name)

    print("\n" + "=" * 60)
    print(f"Resultaat: {passed}/{len(tests)} tests geslaagd")
    if failed:
        print(f"Gefaald: {', '.join(failed)}")
    print("=" * 60)

    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
