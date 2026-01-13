#!/usr/bin/env python3
"""
PDOK Postcode Opzoeker - Verbeterde Versie
Haalt postcodes op via PDOK Locatieserver (Nederlandse overheid)

Verbeteringen:
- Type hints voor betere code documentatie
- Proper exception handling met specifieke exceptions
- Rate limiting en retry logic
- Timeout op HTTP requests
- Logging ipv prints
- Command-line argumenten
- Input validatie
- Constanten voor magic numbers
- Consistente postcode formatting
"""

import argparse
import csv
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

import requests

# ==================== CONSTANTEN ====================
PDOK_BASE_URL = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"
MAX_RESULTS = 1
API_TIMEOUT_SECONDS = 10
API_DELAY_SECONDS = 0.3  # ~200 requests per minuut (veilig voor rate limits)
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
MAX_DISPLAY_NOT_FOUND = 10

# Postcode regex patroon (4 cijfers + 2 letters, optionele spatie)
POSTCODE_PATTERN = re.compile(r'\b(\d{4}\s?[A-Z]{2})\b')

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ==================== FUNCTIES ====================

def clean_address(address_line: str) -> Optional[str]:
    """
    Verwijdert extra spaties en maakt het adres schoon

    Args:
        address_line: Ruw adres uit input bestand

    Returns:
        Schoon adres of None als het leeg/ongeldig is
    """
    address = ' '.join(address_line.split())
    if not address or address.strip() == ',':
        return None
    return address


def validate_dutch_address(address: str) -> bool:
    """
    Valideert of het input lijkt op een geldig Nederlands adres

    Args:
        address: Te valideren adres

    Returns:
        True als het adres geldig lijkt
    """
    # Moet minimaal cijfers bevatten (huisnummer)
    if not re.search(r'\d+', address):
        logger.warning(f"Adres bevat geen huisnummer: {address}")
        return False

    # Moet minimale lengte hebben
    if len(address) < 5:
        logger.warning(f"Adres is te kort: {address}")
        return False

    return True


def normalize_postcode(postcode: str) -> str:
    """
    Normaliseert postcode naar formaat: 1234AB (zonder spatie)

    Args:
        postcode: Postcode in willekeurig formaat

    Returns:
        Genormaliseerde postcode
    """
    return postcode.replace(' ', '').upper()


def get_postcode_pdok(address: str, retry_count: int = 0) -> str:
    """
    Haalt postcode op via PDOK Locatieserver (Nederlandse overheid)

    Args:
        address: Het adres om op te zoeken
        retry_count: Aantal retries tot nu toe (voor rate limiting)

    Returns:
        Postcode of error message
    """
    try:
        # Parameters voor de query
        params = {
            'q': address,
            'rows': MAX_RESULTS,
            'fq': 'type:adres'  # Zoek alleen naar adressen
        }

        # Maak request met timeout
        response = requests.get(
            PDOK_BASE_URL,
            params=params,
            timeout=API_TIMEOUT_SECONDS
        )

        # Handle rate limiting (429 Too Many Requests)
        if response.status_code == 429:
            if retry_count < MAX_RETRIES:
                wait_time = RETRY_DELAY_SECONDS * (retry_count + 1)
                logger.warning(f"Rate limit bereikt, wacht {wait_time}s...")
                time.sleep(wait_time)
                return get_postcode_pdok(address, retry_count + 1)
            else:
                return "Error: Rate limit (te veel verzoeken)"

        # Check for other HTTP errors
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()

            if data['response']['docs'] and len(data['response']['docs']) > 0:
                # Haal eerste resultaat op
                result = data['response']['docs'][0]

                # Zoek postcode in het resultaat
                if 'postcode' in result:
                    return normalize_postcode(result['postcode'])

                # Soms staat het in weergavenaam
                if 'weergavenaam' in result:
                    match = POSTCODE_PATTERN.search(result['weergavenaam'])
                    if match:
                        return normalize_postcode(match.group(1))

        return "Niet gevonden"

    except requests.exceptions.Timeout:
        logger.error(f"Timeout bij ophalen van {address}")
        return "Error: Timeout"
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error bij {address}: {e}")
        return f"Error: {type(e).__name__}"
    except (KeyError, ValueError) as e:
        logger.error(f"Parse error bij {address}: {e}")
        return "Error: Parse fout"
    except Exception as e:
        logger.error(f"Onverwachte error bij {address}: {e}")
        return f"Error: {type(e).__name__}"


def load_addresses(input_file: Path) -> List[str]:
    """
    Laadt adressen uit input bestand met meerdere encoding pogingen

    Args:
        input_file: Pad naar input bestand

    Returns:
        Lijst met schone adressen
    """
    addresses = []
    encodings = ['utf-8', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            logger.info(f"Probeer bestand in te lezen met encoding: {encoding}")
            with open(input_file, 'r', encoding=encoding) as f:
                for line in f:
                    cleaned = clean_address(line.strip())
                    if cleaned and validate_dutch_address(cleaned):
                        addresses.append(cleaned)
            logger.info(f"Bestand succesvol ingelezen met {encoding}")
            break
        except UnicodeDecodeError:
            if encoding == encodings[-1]:
                raise
            logger.warning(f"Encoding {encoding} werkt niet, probeer volgende...")
            continue

    return addresses


def write_csv_results(results: List[Dict], output_file: Path) -> None:
    """
    Schrijf resultaten naar CSV bestand

    Args:
        results: Lijst met resultaten
        output_file: Pad naar output CSV
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['regel_nummer', 'adres', 'postcode']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    logger.info(f"✓ CSV bestand opgeslagen: {output_file}")


def write_postcode_list(results: List[Dict], output_file: Path) -> None:
    """
    Schrijf alleen postcodes naar tekstbestand

    Args:
        results: Lijst met resultaten
        output_file: Pad naar output tekstbestand
    """
    postcode_file = output_file.parent / f"{output_file.stem}_postcodes.txt"
    with open(postcode_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"{result['postcode']}\n")
    logger.info(f"✓ Postcode lijst opgeslagen: {postcode_file}")


def print_summary(results: List[Dict], cache: Dict[str, str]) -> None:
    """
    Print samenvatting van de resultaten

    Args:
        results: Lijst met resultaten
        cache: Cache dictionary met verwerkte adressen
    """
    print("\n" + "=" * 60)
    print("SAMENVATTING:")
    print(f"Totaal verwerkt: {len(results)} adressen")
    print(f"Unieke adressen: {len(cache)}")

    found = sum(1 for r in results if r['postcode'] != 'Niet gevonden'
                and not r['postcode'].startswith('Error'))
    print(f"Postcodes gevonden: {found}")
    print(f"Niet gevonden/errors: {len(results) - found}")

    # Toon adressen die niet gevonden zijn
    not_found = [r for r in results if r['postcode'] == 'Niet gevonden']
    if not_found and len(not_found) <= MAX_DISPLAY_NOT_FOUND:
        print("\nNiet gevonden adressen:")
        for r in not_found:
            print(f"  - {r['adres']}")
    elif len(not_found) > MAX_DISPLAY_NOT_FOUND:
        print(f"\n{len(not_found)} adressen niet gevonden (zie CSV voor details)")


def process_addresses_pdok(input_file: Path, output_file: Path,
                           show_progress: bool = True) -> List[Dict]:
    """
    Hoofdfunctie die het bestand verwerkt met PDOK

    Args:
        input_file: Pad naar input bestand
        output_file: Pad naar output CSV bestand
        show_progress: Toon progress indicator

    Returns:
        Lijst met resultaten
    """
    logger.info(f"Bezig met inlezen van {input_file}...")

    addresses = load_addresses(input_file)

    logger.info(f"Gevonden: {len(addresses)} geldige adressen")
    logger.info("Postcodes ophalen via PDOK Locatieserver (Nederlandse overheid)...")
    print("-" * 60)

    results = []
    cache = {}  # Cache voor duplicaten

    # Probeer tqdm te importeren voor progress bar
    try:
        from tqdm import tqdm
        iterator = tqdm(enumerate(addresses, 1), total=len(addresses),
                       desc="Postcodes ophalen", disable=not show_progress)
    except ImportError:
        logger.info("Tip: Installeer 'tqdm' voor een progress bar (pip install tqdm)")
        iterator = enumerate(addresses, 1)

    for i, address in iterator:
        if not show_progress or 'tqdm' not in dir():
            logger.info(f"[{i}/{len(addresses)}] Verwerken: {address}")

        # Check cache voor duplicaten
        if address in cache:
            postcode = cache[address]
            if not show_progress or 'tqdm' not in dir():
                logger.info(f"    → Postcode (uit cache): {postcode}")
        else:
            postcode = get_postcode_pdok(address)
            cache[address] = postcode
            if not show_progress or 'tqdm' not in dir():
                logger.info(f"    → Postcode: {postcode}")

            # Kleine pauze tussen requests (rate limiting)
            time.sleep(API_DELAY_SECONDS)

        results.append({
            'regel_nummer': i,
            'adres': address,
            'postcode': postcode
        })

    print("-" * 60)

    # Schrijf resultaten
    logger.info(f"\nResultaten opslaan in {output_file}...")
    write_csv_results(results, output_file)
    write_postcode_list(results, output_file)

    # Print samenvatting
    print_summary(results, cache)

    # Toon eerste paar resultaten als preview
    if results:
        print("\nVoorbeeld resultaten:")
        for result in results[:5]:
            print(f"  {result['regel_nummer']}. {result['adres']} → {result['postcode']}")

        if len(results) > 5:
            print(f"  ... en {len(results)-5} meer")

    return results


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line argumenten

    Returns:
        Parsed argumenten
    """
    parser = argparse.ArgumentParser(
        description='PDOK Postcode Opzoeker - Haalt postcodes op via Nederlandse overheidsdata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Voorbeelden:
  %(prog)s adressen.txt
  %(prog)s adressen.txt -o resultaat.csv
  %(prog)s adressen.txt --no-progress
  %(prog)s adressen.txt --verbose
        """
    )

    parser.add_argument(
        'input_file',
        type=Path,
        help='Input bestand met adressen (één adres per regel)'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output CSV bestand (default: postcodes_resultaat_TIMESTAMP.csv)'
    )

    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Verberg progress indicator'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output (debug logging)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0 (Verbeterde versie)'
    )

    return parser.parse_args()


def main() -> None:
    """
    Hoofdprogramma
    """
    print("=" * 60)
    print("POSTCODE OPZOEKER - PDOK Locatieserver (Verbeterd)")
    print("=" * 60)
    print("Gebruikt Nederlandse overheidsdata\n")

    # Parse argumenten
    args = parse_arguments()

    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode ingeschakeld")

    # Bepaal output bestand
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f'postcodes_resultaat_{timestamp}.csv')

    # Check of input bestand bestaat
    if not args.input_file.exists():
        logger.error(f"❌ Error: Bestand '{args.input_file}' niet gevonden!")
        print("\nMaak een bestand met adressen zoals:")
        print("  Barrierweg 1, EINDHOVEN")
        print("  Pasqualinistraat 10, EINDHOVEN")
        return

    # Waarschuw als output bestand al bestaat
    if output_file.exists():
        response = input(f"\n⚠️  {output_file} bestaat al. Overschrijven? (j/n): ")
        if response.lower() not in ['j', 'ja', 'y', 'yes']:
            logger.info("Gestopt door gebruiker")
            return

    try:
        # Verwerk de adressen
        process_addresses_pdok(
            args.input_file,
            output_file,
            show_progress=not args.no_progress
        )

        print("\n✓ Klaar!")

    except FileNotFoundError as e:
        logger.error(f"❌ Bestand niet gevonden: {e}")
    except PermissionError as e:
        logger.error(f"❌ Geen toegang tot bestand: {e}")
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Gestopt door gebruiker (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Onverwachte error: {e}", exc_info=args.verbose)


if __name__ == "__main__":
    main()
