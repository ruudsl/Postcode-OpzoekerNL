#!/usr/bin/env python3
"""
PDOK Postcode Opzoeker - Vercel Serverless Version
Geoptimaliseerd voor performance, security en vindbaarheid (SEO + AI)
"""

import os
import re
import time
from datetime import datetime
from typing import Optional

from flask import Flask, render_template, request, jsonify, Response
import requests

# ==================== CONSTANTEN ====================
PDOK_BASE_URL = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"
MAX_RESULTS = 1
API_TIMEOUT_SECONDS = 10

# Configureerbaar via Vercel environment variables (geen redeploy van code nodig)
API_DELAY_SECONDS = float(os.environ.get('API_DELAY_SECONDS', '0.15'))
MAX_ADDRESSES = int(os.environ.get('MAX_ADDRESSES', '50'))

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
MAX_ADDRESS_LENGTH = 200
APP_VERSION = '2.0.0'

POSTCODE_PATTERN = re.compile(r'\b(\d{4}\s?[A-Z]{2})\b')

# Hergebruik één HTTP-sessie: connection pooling maakt elke lookup sneller
# en een nette User-Agent is goede API-etiquette richting PDOK
http = requests.Session()
http.headers.update({
    'User-Agent': f'PostcodeOpzoekerNL/{APP_VERSION} '
                  '(+https://github.com/ruudsl/Postcode-OpzoekerNL)'
})

# ==================== FLASK APP ====================
app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max for serverless


@app.after_request
def set_security_headers(response: Response) -> Response:
    """Security headers voor alle responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    return response


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
    if len(address) < 5 or len(address) > MAX_ADDRESS_LENGTH:
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

        response = http.get(
            PDOK_BASE_URL,
            params=params,
            timeout=API_TIMEOUT_SECONDS
        )

        if response.status_code == 429:
            if retry_count < MAX_RETRIES:
                wait_time = RETRY_DELAY_SECONDS * (retry_count + 1)
                time.sleep(wait_time)
                return get_postcode_pdok(address, retry_count + 1)
            return "Error: Rate limit"

        response.raise_for_status()

        data = response.json()
        docs = data.get('response', {}).get('docs', [])

        if docs:
            result = docs[0]

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
    except (KeyError, ValueError):
        return "Error: Parse"


def process_addresses_sync(addresses: list) -> dict:
    """Verwerkt adressen synchroon (voor serverless).

    Dedupliceert vooraf: elk uniek adres gaat maar één keer naar de API,
    en er wordt alleen gewacht tussen échte API-calls.
    """
    results = []
    cache: dict = {}
    unique_count = len(set(addresses))
    api_calls_done = 0

    for i, address in enumerate(addresses, 1):
        if address in cache:
            postcode = cache[address]
        else:
            # Alleen pauzeren tussen echte API-calls, niet vóór de eerste
            # en niet na cache-hits — dat scheelt seconden per batch
            if api_calls_done > 0:
                time.sleep(API_DELAY_SECONDS)
            postcode = get_postcode_pdok(address)
            cache[address] = postcode
            api_calls_done += 1

        results.append({
            'regel_nummer': i,
            'adres': address,
            'postcode': postcode
        })

    summary = {
        'total': len(results),
        'found': sum(1 for r in results
                     if not r['postcode'].startswith('Error')
                     and r['postcode'] != 'Niet gevonden'),
        'not_found': sum(1 for r in results if r['postcode'] == 'Niet gevonden'),
        'errors': sum(1 for r in results if r['postcode'].startswith('Error')),
        'duplicates': len(results) - unique_count
    }

    return {
        'results': results,
        'summary': summary
    }


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home pagina — geeft base_url en limiet door voor SEO-tags en UI-sync"""
    base_url = request.url_root.rstrip('/')
    return render_template(
        'index_vercel.html',
        base_url=base_url,
        max_addresses=MAX_ADDRESSES
    )


@app.route('/api/process', methods=['POST'])
def process():
    """Verwerk adressen (synchroon voor serverless)"""
    try:
        data = request.get_json(silent=True)

        if not data or 'addresses' not in data:
            return jsonify({'error': 'Geen adressen opgegeven'}), 400

        addresses_text = data['addresses']
        if not isinstance(addresses_text, str):
            return jsonify({'error': 'Ongeldig invoerformaat'}), 400

        addresses = []
        for line in addresses_text.split('\n'):
            cleaned = clean_address(line.strip())
            if cleaned and validate_dutch_address(cleaned):
                addresses.append(cleaned)

        if not addresses:
            return jsonify({
                'error': 'Geen geldige adressen gevonden. '
                         'Gebruik het formaat: Straatnaam 12, PLAATS'
            }), 400

        if len(addresses) > MAX_ADDRESSES:
            return jsonify({
                'error': f'Maximum {MAX_ADDRESSES} adressen tegelijk '
                         f'(je hebt er {len(addresses)}). '
                         'Voor grotere lijsten: gebruik de gratis CLI-versie.'
            }), 400

        result = process_addresses_sync(addresses)
        return jsonify(result)

    except Exception:
        # Geen interne details naar de client lekken
        return jsonify({'error': 'Er is een onverwachte fout opgetreden'}), 500


@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'platform': 'vercel',
        'version': APP_VERSION,
        'max_addresses': MAX_ADDRESSES
    })


# ==================== SEO & AI-VINDBAARHEID ====================

@app.route('/robots.txt')
def robots():
    """Robots.txt — expliciet toegankelijk voor zoekmachines én AI-crawlers"""
    base_url = request.url_root.rstrip('/')
    content = f"""User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: PerplexityBot
Allow: /

Sitemap: {base_url}/sitemap.xml
"""
    resp = Response(content, mimetype='text/plain')
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp


@app.route('/sitemap.xml')
def sitemap():
    """XML sitemap voor zoekmachines"""
    base_url = request.url_root.rstrip('/')
    today = datetime.utcnow().strftime('%Y-%m-%d')
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    resp = Response(content, mimetype='application/xml')
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp


@app.route('/llms.txt')
def llms_txt():
    """llms.txt — beschrijving voor AI-assistenten (Claude, ChatGPT, Perplexity, etc.)"""
    base_url = request.url_root.rstrip('/')
    content = f"""# Postcode Opzoeker NL

> Gratis online tool om Nederlandse postcodes op te zoeken op basis van
> adres (straatnaam + huisnummer + plaats). Gebruikt de officiële PDOK
> Locatieserver API van de Nederlandse overheid. Geen account of API key
> nodig. Tot {MAX_ADDRESSES} adressen tegelijk, met CSV- en TXT-export.

## Gebruik

- Web interface: {base_url}/
- Invoerformaat: "Straatnaam 12, PLAATSNAAM" (één adres per regel)
- Output: Nederlandse postcode in formaat 1234AB
- Export: CSV (regel, adres, postcode) en TXT (alleen postcodes)

## API

- POST {base_url}/api/process
  Body: {{"addresses": "Dam 1, AMSTERDAM\\nCoolsingel 40, ROTTERDAM"}}
  Response: {{"results": [...], "summary": {{...}}}}
- GET {base_url}/api/health — status en limieten

## Bron

- Data: PDOK Locatieserver (officiële Nederlandse overheidsdata)
- Broncode: https://github.com/ruudsl/Postcode-OpzoekerNL
- Licentie: MIT (open source)
- Voor bulk-verwerking (200+ adressen): gebruik de CLI-versie uit de repository
"""
    resp = Response(content, mimetype='text/plain')
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp


# Vercel detecteert het 'app' object automatisch
