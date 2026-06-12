#!/usr/bin/env python3
"""
PDOK Postcode Opzoeker - Web Interface
Flask web applicatie voor het opzoeken van postcodes via PDOK API
"""

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from queue import Queue
from threading import Thread

from flask import Flask, render_template, request, jsonify, send_file, Response
import requests

# ==================== CONSTANTEN ====================
PDOK_BASE_URL = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"
MAX_RESULTS = 1
API_TIMEOUT_SECONDS = 10
API_DELAY_SECONDS = 0.3
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

UPLOAD_FOLDER = Path("uploads")
RESULTS_FOLDER = Path("results")
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)

POSTCODE_PATTERN = re.compile(r'\b(\d{4}\s?[A-Z]{2})\b')

# ==================== FLASK APP ====================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.after_request
def set_security_headers(response):
    """Security headers voor alle responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Storage voor job status
jobs: Dict[str, Dict] = {}

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== UTILITY FUNCTIES ====================

def clean_address(address_line: str) -> Optional[str]:
    """Verwijdert extra spaties en maakt het adres schoon"""
    address = ' '.join(address_line.split())
    if not address or address.strip() == ',':
        return None
    return address


def validate_dutch_address(address: str) -> bool:
    """Valideert of het input lijkt op een geldig Nederlands adres"""
    if not re.search(r'\d+', address):
        return False
    if len(address) < 5:
        return False
    return True


def normalize_postcode(postcode: str) -> str:
    """Normaliseert postcode naar formaat: 1234AB"""
    return postcode.replace(' ', '').upper()


def get_postcode_pdok(address: str, retry_count: int = 0) -> str:
    """Haalt postcode op via PDOK Locatieserver"""
    try:
        params = {
            'q': address,
            'rows': MAX_RESULTS,
            'fq': 'type:adres'
        }

        response = requests.get(
            PDOK_BASE_URL,
            params=params,
            timeout=API_TIMEOUT_SECONDS
        )

        # Handle rate limiting
        if response.status_code == 429:
            if retry_count < MAX_RETRIES:
                wait_time = RETRY_DELAY_SECONDS * (retry_count + 1)
                time.sleep(wait_time)
                return get_postcode_pdok(address, retry_count + 1)
            else:
                return "Error: Rate limit"

        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()

            if data['response']['docs'] and len(data['response']['docs']) > 0:
                result = data['response']['docs'][0]

                if 'postcode' in result:
                    return normalize_postcode(result['postcode'])

                if 'weergavenaam' in result:
                    match = POSTCODE_PATTERN.search(result['weergavenaam'])
                    if match:
                        return normalize_postcode(match.group(1))

        return "Niet gevonden"

    except requests.exceptions.Timeout:
        return "Error: Timeout"
    except requests.exceptions.RequestException:
        return "Error: Network"
    except Exception:
        return "Error: Unknown"


def process_file_job(job_id: str, filepath: Path) -> None:
    """Verwerkt een bestand in een achtergrond thread"""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 0

        # Lees adressen
        addresses = []
        encodings = ['utf-8', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    for line in f:
                        cleaned = clean_address(line.strip())
                        if cleaned and validate_dutch_address(cleaned):
                            addresses.append(cleaned)
                break
            except UnicodeDecodeError:
                if encoding == encodings[-1]:
                    jobs[job_id]['status'] = 'error'
                    jobs[job_id]['error'] = 'Kon bestand niet lezen (encoding probleem)'
                    return
                continue

        if not addresses:
            jobs[job_id]['status'] = 'error'
            jobs[job_id]['error'] = 'Geen geldige adressen gevonden'
            return

        jobs[job_id]['total'] = len(addresses)

        # Verwerk adressen
        results = []
        cache = {}

        for i, address in enumerate(addresses, 1):
            if address in cache:
                postcode = cache[address]
            else:
                postcode = get_postcode_pdok(address)
                cache[address] = postcode
                time.sleep(API_DELAY_SECONDS)

            results.append({
                'regel_nummer': i,
                'adres': address,
                'postcode': postcode
            })

            jobs[job_id]['processed'] = i
            jobs[job_id]['progress'] = int((i / len(addresses)) * 100)

        # Sla resultaten op
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = RESULTS_FOLDER / f"postcodes_{job_id}_{timestamp}.csv"
        txt_file = RESULTS_FOLDER / f"postcodes_{job_id}_{timestamp}.txt"

        # Schrijf CSV
        import csv as csv_module
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv_module.DictWriter(f, fieldnames=['regel_nummer', 'adres', 'postcode'])
            writer.writeheader()
            for result in results:
                writer.writerow(result)

        # Schrijf TXT
        with open(txt_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(f"{result['postcode']}\n")

        # Update job status
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['csv_file'] = str(csv_file)
        jobs[job_id]['txt_file'] = str(txt_file)
        jobs[job_id]['results'] = results
        jobs[job_id]['summary'] = {
            'total': len(results),
            'found': sum(1 for r in results if not r['postcode'].startswith('Error') and r['postcode'] != 'Niet gevonden'),
            'not_found': sum(1 for r in results if r['postcode'] == 'Niet gevonden'),
            'errors': sum(1 for r in results if r['postcode'].startswith('Error'))
        }

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home pagina"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload en start verwerking van een bestand"""
    if 'file' not in request.files:
        return jsonify({'error': 'Geen bestand geüpload'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Geen bestand geselecteerd'}), 400

    if not file.filename.endswith('.txt'):
        return jsonify({'error': 'Alleen .txt bestanden zijn toegestaan'}), 400

    # Genereer unieke job ID
    job_id = str(uuid.uuid4())

    # Sla bestand op
    filename = f"{job_id}_{file.filename}"
    filepath = UPLOAD_FOLDER / filename
    file.save(filepath)

    # Maak job entry
    jobs[job_id] = {
        'id': job_id,
        'filename': file.filename,
        'status': 'queued',
        'progress': 0,
        'processed': 0,
        'total': 0,
        'created_at': datetime.now().isoformat()
    }

    # Start verwerking in achtergrond
    thread = Thread(target=process_file_job, args=(job_id, filepath))
    thread.daemon = True
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/process-text', methods=['POST'])
def process_text():
    """Verwerk direct ingevoerde adressen"""
    data = request.get_json()

    if not data or 'addresses' not in data:
        return jsonify({'error': 'Geen adressen opgegeven'}), 400

    addresses_text = data['addresses']
    addresses = []

    for line in addresses_text.split('\n'):
        cleaned = clean_address(line.strip())
        if cleaned and validate_dutch_address(cleaned):
            addresses.append(cleaned)

    if not addresses:
        return jsonify({'error': 'Geen geldige adressen gevonden'}), 400

    # Genereer job ID
    job_id = str(uuid.uuid4())

    # Maak tijdelijk bestand
    filepath = UPLOAD_FOLDER / f"{job_id}_manual.txt"
    with open(filepath, 'w', encoding='utf-8') as f:
        for addr in addresses:
            f.write(f"{addr}\n")

    # Maak job entry
    jobs[job_id] = {
        'id': job_id,
        'filename': 'Handmatig ingevoerd',
        'status': 'queued',
        'progress': 0,
        'processed': 0,
        'total': 0,
        'created_at': datetime.now().isoformat()
    }

    # Start verwerking
    thread = Thread(target=process_file_job, args=(job_id, filepath))
    thread.daemon = True
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/status/<job_id>')
def job_status(job_id):
    """Haal status van een job op"""
    if job_id not in jobs:
        return jsonify({'error': 'Job niet gevonden'}), 404

    job = jobs[job_id]
    return jsonify(job)


@app.route('/api/stream/<job_id>')
def stream_progress(job_id):
    """Server-Sent Events stream voor real-time progress"""
    def generate():
        if job_id not in jobs:
            yield f"data: {json.dumps({'error': 'Job niet gevonden'})}\n\n"
            return

        last_progress = -1
        while True:
            if job_id not in jobs:
                break

            job = jobs[job_id]
            current_progress = job.get('progress', 0)

            if current_progress != last_progress:
                yield f"data: {json.dumps(job)}\n\n"
                last_progress = current_progress

            if job['status'] in ['completed', 'error']:
                break

            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/download/<job_id>/<file_type>')
def download_file(job_id, file_type):
    """Download resultaat bestand"""
    if job_id not in jobs:
        return jsonify({'error': 'Job niet gevonden'}), 404

    job = jobs[job_id]

    if job['status'] != 'completed':
        return jsonify({'error': 'Job nog niet voltooid'}), 400

    if file_type == 'csv':
        filepath = job.get('csv_file')
    elif file_type == 'txt':
        filepath = job.get('txt_file')
    else:
        return jsonify({'error': 'Ongeldig bestandstype'}), 400

    if not filepath or not Path(filepath).exists():
        return jsonify({'error': 'Bestand niet gevonden'}), 404

    return send_file(
        filepath,
        as_attachment=True,
        download_name=Path(filepath).name
    )


@app.route('/api/stats')
def stats():
    """Algemene statistieken"""
    total_jobs = len(jobs)
    completed = sum(1 for j in jobs.values() if j['status'] == 'completed')
    processing = sum(1 for j in jobs.values() if j['status'] == 'processing')
    errors = sum(1 for j in jobs.values() if j['status'] == 'error')

    return jsonify({
        'total_jobs': total_jobs,
        'completed': completed,
        'processing': processing,
        'errors': errors
    })


# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("PDOK Postcode Opzoeker - Web Interface")
    print("=" * 60)
    print("\n🌐 Server draait op: http://localhost:5000")
    print("📝 Upload adressen.txt bestanden of voer adressen handmatig in")
    print("⏸️  Stop met Ctrl+C\n")

    # Debug alleen aan via expliciete env var (security fix uit audit)
    debug_mode = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
