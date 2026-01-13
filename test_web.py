#!/usr/bin/env python3
"""
Test script voor PDOK Postcode Opzoeker Web Interface
Voert basis tests uit om te controleren of alles werkt
"""

import requests
import time
import json
from pathlib import Path

BASE_URL = "http://localhost:5000"

def test_home_page():
    """Test of de home pagina bereikbaar is"""
    print("🔍 Test 1: Home page...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("   ✅ Home page loaded successfully")
            return True
        else:
            print(f"   ❌ Error: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_upload_file():
    """Test file upload endpoint"""
    print("\n2. Test bestand upload...")

    # Create test file
    test_file = Path("test_upload.txt")
    test_file.write_text("Dam 1, AMSTERDAM\nBarrierweg 1, EINDHOVEN")

    try:
        with open(test_file, 'rb') as f:
            response = requests.post(
                f'{BASE_URL}/api/upload',
                files={'file': ('test.txt', f, 'text/plain')}
            )

        if response.status_code == 200:
            job_id = response.json()['job_id']
            print(f"✅ Upload gelukt! Job ID: {job_id}")
            return job_id
        else:
            print(f"❌ Upload mislukt: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error bij upload: {e}")
        return None


def test_process_text():
    """Test handmatige invoer"""
    print("\n2️⃣  Test: Handmatige invoer...")

    addresses = """Barrierweg 1, EINDHOVEN
Dam 1, AMSTERDAM
Coolsingel 40, ROTTERDAM"""

    response = requests.post(
        f"{BASE_URL}/api/process-text",
        json={'addresses': addresses},
        timeout=5
    )

    if response.status_code == 200:
        job_id = response.json()['job_id']
        print(f"   ✓ Job aangemaakt: {job_id}")
        return job_id
    else:
        print(f"   ❌ Fout bij verwerken: {response.text}")
        return None


def test_job_status(job_id):
    """Test job status endpoint"""
    print(f"\n3. Status ophalen van job {job_id}...")

    # Poll status een paar keer
    for i in range(5):
        response = requests.get(f'http://localhost:5000/api/status/{job_id}')

        if response.status_code == 200:
            job = response.json()
            print(f"   Status: {job['status']}")
            print(f"   Progress: {job.get('progress', 0)}%")
            print(f"   Verwerkt: {job.get('processed', 0)}/{job.get('total', 0)}")

            if job['status'] == 'completed':
                print("\n✅ Verwerking voltooid!")
                return job
            elif job['status'] == 'error':
                print(f"\n❌ Error: {job.get('error', 'Unknown')}")
                return None

        time.sleep(1)

    print("\n⚠️  Job nog niet voltooid na 60 seconden")
    return None

def download_results(job_id, file_type='csv'):
    """Download resultaten"""
    url = f"{BASE_URL}/api/download/{job_id}/{file_type}"
    response = requests.get(url)

    if response.status_code == 200:
        filename = f"test_result.{file_type}"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✓ {file_type.upper()} bestand opgeslagen: {filename}")
        return True
    else:
        print(f"❌ Download mislukt: {response.status_code}")
        return False


def main():
    """Hoofdprogramma voor testen"""
    print("=" * 60)
    print("PDOK Postcode Opzoeker - Web Interface Test")
    print("=" * 60)
    print()

    # Test of server draait
    print("1. Controleren of server draait...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is bereikbaar")
            stats = response.json()
            print(f"   Statistieken: {stats}")
        else:
            print("   ❌ Server antwoordt niet correct")
            return
    except Exception as e:
        print(f"❌ Kan geen verbinding maken met server op {BASE_URL}")
        print(f"   Zorg dat de server draait: python app.py")
        print(f"   Error: {e}")
        return

    # Test handmatige invoer
    print("\n2️⃣  Test: Handmatige invoer...")
    test_addresses = """Barrierweg 1, EINDHOVEN
Dam 1, AMSTERDAM
Coolsingel 40, ROTTERDAM"""

    response = requests.post(
        f"{BASE_URL}/api/process-text",
        json={'addresses': test_addresses},
        timeout=5
    )

    if response.status_code == 200:
        data = response.json()
        job_id = data['job_id']
        print(f"   ✓ Job created: {job_id}")

        # Wait for completion
        print("   Waiting for completion...")
        max_wait = 60
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            time.sleep(1)
            status_response = requests.get(f"{base_url}/api/status/{job_id}")
            job = status_response.json()

            if job['status'] == 'completed':
                print(f"   ✓ Job completed!")
                print(f"   Found: {job['summary']['found']}/{job['summary']['total']}")
                break
            elif job['status'] == 'error':
                print(f"   ✗ Error: {job.get('error', 'Unknown')}")
                break

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

    return True


def test_all():
    """Run all tests"""
    print("=" * 60)
    print("PDOK Postcode Lookup - Web Interface Tests")
    print("=" * 60)
    print()

    results = {
        'Server Health': test_server_health(),
        'API Stats': test_api_stats(),
        'File Upload': test_file_upload(),
        'Manual Input': test_manual_input()
    }

    print()
    print("=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")

    total = len(results)
    passed = sum(results.values())
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

    return passed == total


if __name__ == '__main__':
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000/', timeout=2)
        print("✓ Server is running\n")
    except requests.exceptions.ConnectionError:
        print("✗ Server is NOT running!")
        print("\nPlease start the server first:")
        print("  python app.py")
        print("\nor:")
        print("  ./start_web.sh")
        print()
        sys.exit(1)

    # Run tests
    success = test_all()
    sys.exit(0 if success else 1)
