#!/usr/bin/env python3
"""
PDOK Postcode Opzoeker - Vercel Serverless Version
Simplified version for serverless deployment
"""

import json
import re
import time
from io import StringIO
from flask import Flask, render_template, request, jsonify, Response
import requests

# ==================== CONSTANTEN ====================
PDOK_BASE_URL = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"
MAX_RESULTS = 1
API_TIMEOUT_SECONDS = 10
API_DELAY_SECONDS = 0.3
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
POSTCODE_PATTERN = re.compile(r'\b(\d{4}\s?[A-Z]{2})\b')

# ==================== FLASK APP ====================
app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max for serverless

# ==================== UTILITY FUNCTIES ====================

def clean_address(address_line: str):
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


def process_addresses_sync(addresses: list) -> dict:
    """Verwerkt adressen synchroon (voor serverless)"""
    results = []
    cache = {}

    for i, address in enumerate(addresses, 1):
        if address in cache:
            postcode = cache[address]
        else:
            postcode = get_postcode_pdok(address)
            cache[address] = postcode
            if i < len(addresses):  # Don't sleep after last address
                time.sleep(API_DELAY_SECONDS)

        results.append({
            'regel_nummer': i,
            'adres': address,
            'postcode': postcode
        })

    summary = {
        'total': len(results),
        'found': sum(1 for r in results if not r['postcode'].startswith('Error') and r['postcode'] != 'Niet gevonden'),
        'not_found': sum(1 for r in results if r['postcode'] == 'Niet gevonden'),
        'errors': sum(1 for r in results if r['postcode'].startswith('Error'))
    }

    return {
        'results': results,
        'summary': summary
    }


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home pagina"""
    return render_template('index_vercel.html')


@app.route('/api/process', methods=['POST'])
def process():
    """Verwerk adressen (synchroon voor serverless)"""
    try:
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

        # Limit aantal adressen voor serverless (max 10 seconden execution time)
        if len(addresses) > 20:
            return jsonify({'error': 'Maximum 20 adressen tegelijk (serverless limiet)'}), 400

        # Process synchroon
        result = process_addresses_sync(addresses)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'platform': 'vercel'})


# ==================== VERCEL HANDLER ====================
# Vercel verwacht een 'app' object
# Flask app wordt automatisch gedetecteerd
