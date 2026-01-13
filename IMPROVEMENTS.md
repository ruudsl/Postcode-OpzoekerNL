# Verbeteringen in postcode_lookup_improved.py

## 🔴 Kritieke Fixes Toegepast

### 1. ✅ Import Conflict Opgelost
**Was:**
```python
import requests  # Top van bestand

# Later in main():
try:
    import requests  # Dubbele check die nooit werkt
except ImportError:
    print("requests niet geïnstalleerd")
```

**Nu:**
```python
import requests  # Alleen bovenaan
# Geen dubbele check meer - als het niet werkt crasht het direct bij import
```

---

### 2. ✅ Timeout Toegevoegd aan HTTP Requests
**Was:**
```python
response = requests.get(base_url, params=params)  # Kan oneindig hangen
```

**Nu:**
```python
response = requests.get(
    PDOK_BASE_URL,
    params=params,
    timeout=API_TIMEOUT_SECONDS  # = 10 seconden
)
```

---

### 3. ✅ Import uit Functie Verplaatst
**Was:**
```python
def get_postcode_pdok(address):
    # ...
    import re  # Import in functie (inefficiënt)
```

**Nu:**
```python
import re  # Bovenaan bestand
```

---

### 4. ✅ Specifieke Exception Handling
**Was:**
```python
except Exception as e:  # Vangt ALLES
    return f"Error: {str(e)}"
```

**Nu:**
```python
except requests.exceptions.Timeout:
    logger.error(f"Timeout bij ophalen van {address}")
    return "Error: Timeout"
except requests.exceptions.RequestException as e:
    logger.error(f"Request error bij {address}: {e}")
    return f"Error: {type(e).__name__}"
except (KeyError, ValueError) as e:
    logger.error(f"Parse error bij {address}: {e}")
    return "Error: Parse fout"
```

---

### 5. ✅ Consistente Postcode Formatting
**Was:**
```python
if 'postcode' in result:
    return result['postcode']  # Mogelijk met spatie

# Later:
return match.group(1).replace(' ', '')  # Zonder spatie
```

**Nu:**
```python
def normalize_postcode(postcode: str) -> str:
    """Normaliseert postcode naar formaat: 1234AB (zonder spatie)"""
    return postcode.replace(' ', '').upper()

# Overal consistent gebruikt:
if 'postcode' in result:
    return normalize_postcode(result['postcode'])
if match:
    return normalize_postcode(match.group(1))
```

---

### 6. ✅ Rate Limit Handling Toegevoegd
**Was:**
```python
response = requests.get(base_url, params=params)
if response.status_code == 200:
    # Verwerk response
# Geen handling voor 429 (Too Many Requests)
```

**Nu:**
```python
if response.status_code == 429:
    if retry_count < MAX_RETRIES:
        wait_time = RETRY_DELAY_SECONDS * (retry_count + 1)
        logger.warning(f"Rate limit bereikt, wacht {wait_time}s...")
        time.sleep(wait_time)
        return get_postcode_pdok(address, retry_count + 1)
    else:
        return "Error: Rate limit (te veel verzoeken)"

response.raise_for_status()  # Check andere HTTP errors
```

---

### 7. ✅ Sleep Tijd Verhoogd
**Was:**
```python
time.sleep(0.1)  # 0.1s = ~600 requests/minuut (te snel!)
```

**Nu:**
```python
API_DELAY_SECONDS = 0.3  # ~200 requests/minuut (veilig)
time.sleep(API_DELAY_SECONDS)
```

---

## 🟢 Extra Verbeteringen

### 8. ✅ Command-Line Argumenten
**Was:**
```python
input_file = 'adressen.txt'  # Hardcoded
output_file = f'postcodes_resultaat_{timestamp}.csv'  # Geen controle
```

**Nu:**
```python
import argparse

parser = argparse.ArgumentParser(description='PDOK Postcode Opzoeker')
parser.add_argument('input_file', type=Path, help='Input bestand')
parser.add_argument('-o', '--output', type=Path, help='Output CSV')
parser.add_argument('--no-progress', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')

# Gebruik:
# python postcode_lookup_improved.py adressen.txt
# python postcode_lookup_improved.py adressen.txt -o mijn_output.csv
# python postcode_lookup_improved.py adressen.txt --verbose
```

---

### 9. ✅ Type Hints Toegevoegd
**Was:**
```python
def clean_address(address_line):
    """..."""

def get_postcode_pdok(address):
    """..."""
```

**Nu:**
```python
def clean_address(address_line: str) -> Optional[str]:
    """..."""

def get_postcode_pdok(address: str, retry_count: int = 0) -> str:
    """..."""

def process_addresses_pdok(input_file: Path, output_file: Path,
                           show_progress: bool = True) -> List[Dict]:
    """..."""
```

---

### 10. ✅ Logging in plaats van Prints
**Was:**
```python
print(f"Bezig met inlezen van {input_file}...")
print(f"[{i}/{len(addresses)}] Verwerken: {address}")
```

**Nu:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

logger.info(f"Bezig met inlezen van {input_file}...")
logger.info(f"[{i}/{len(addresses)}] Verwerken: {address}")
logger.error(f"Error bij {address}: {e}")
logger.warning(f"Rate limit bereikt")
```

**Voordeel:** Logging kan op/uit gezet worden, heeft timestamps, en kan naar file geschreven worden.

---

### 11. ✅ Constanten voor Magic Numbers
**Was:**
```python
params = {'rows': 1}  # Waarom 1?
time.sleep(0.1)  # Waarom 0.1?
if len(not_found) <= 10:  # Waarom 10?
```

**Nu:**
```python
# Constanten bovenaan bestand
MAX_RESULTS = 1
API_TIMEOUT_SECONDS = 10
API_DELAY_SECONDS = 0.3
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
MAX_DISPLAY_NOT_FOUND = 10

# Gebruik in code
params = {'rows': MAX_RESULTS}
time.sleep(API_DELAY_SECONDS)
if len(not_found) <= MAX_DISPLAY_NOT_FOUND:
```

---

### 12. ✅ Input Validatie Toegevoegd
**Nieuw:**
```python
def validate_dutch_address(address: str) -> bool:
    """Valideert of het input lijkt op een geldig Nederlands adres"""
    # Moet minimaal cijfers bevatten (huisnummer)
    if not re.search(r'\d+', address):
        logger.warning(f"Adres bevat geen huisnummer: {address}")
        return False

    # Moet minimale lengte hebben
    if len(address) < 5:
        logger.warning(f"Adres is te kort: {address}")
        return False

    return True
```

---

### 13. ✅ Encoding Error Handling
**Was:**
```python
with open(input_file, 'r', encoding='utf-8') as f:
    # Crasht als bestand niet UTF-8 is
```

**Nu:**
```python
def load_addresses(input_file: Path) -> List[str]:
    """Laadt adressen met meerdere encoding pogingen"""
    encodings = ['utf-8', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            logger.info(f"Probeer bestand in te lezen met encoding: {encoding}")
            with open(input_file, 'r', encoding=encoding) as f:
                # ...
            logger.info(f"Bestand succesvol ingelezen met {encoding}")
            break
        except UnicodeDecodeError:
            if encoding == encodings[-1]:
                raise
            logger.warning(f"Encoding {encoding} werkt niet, probeer volgende...")
            continue
```

---

### 14. ✅ Progress Bar (met fallback)
**Nieuw:**
```python
# Probeer tqdm te importeren voor progress bar
try:
    from tqdm import tqdm
    iterator = tqdm(enumerate(addresses, 1), total=len(addresses),
                   desc="Postcodes ophalen", disable=not show_progress)
except ImportError:
    logger.info("Tip: Installeer 'tqdm' voor een progress bar (pip install tqdm)")
    iterator = enumerate(addresses, 1)
```

**Gebruik:**
```bash
# Met tqdm geïnstalleerd:
Postcodes ophalen: 100%|████████████| 150/150 [00:45<00:00,  3.33it/s]

# Zonder tqdm:
[1/150] Verwerken: Barrierweg 1, EINDHOVEN
[2/150] Verwerken: ...
```

---

### 15. ✅ Output Bestand Overschrijf Waarschuwing
**Nieuw:**
```python
if output_file.exists():
    response = input(f"\n⚠️  {output_file} bestaat al. Overschrijven? (j/n): ")
    if response.lower() not in ['j', 'ja', 'y', 'yes']:
        logger.info("Gestopt door gebruiker")
        return
```

---

### 16. ✅ Betere Error Messages
**Was:**
```python
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
```

**Nu:**
```python
except FileNotFoundError as e:
    logger.error(f"❌ Bestand niet gevonden: {e}")
except PermissionError as e:
    logger.error(f"❌ Geen toegang tot bestand: {e}")
except KeyboardInterrupt:
    logger.warning("\n\n⚠️  Gestopt door gebruiker (Ctrl+C)")
except Exception as e:
    logger.error(f"❌ Onverwachte error: {e}", exc_info=args.verbose)
```

---

### 17. ✅ Code Structuur Verbeteringen
- Functies zijn kleiner en doen één ding
- `write_csv_results()` en `write_postcode_list()` zijn aparte functies
- `print_summary()` is een aparte functie
- `load_addresses()` is een aparte functie
- Betere scheiding van concerns

---

## 📊 Vergelijking

| Feature | Origineel | Verbeterd |
|---------|-----------|-----------|
| HTTP Timeout | ❌ Nee | ✅ 10 seconden |
| Rate Limiting | ❌ Nee | ✅ Retry logic met exponential backoff |
| Exception Handling | ❌ Te breed | ✅ Specifieke exceptions |
| Postcode Format | ❌ Inconsistent | ✅ Consistent (1234AB) |
| API Delay | ⚠️ 0.1s (te snel) | ✅ 0.3s (veilig) |
| Input Validatie | ❌ Nee | ✅ Valideert adressen |
| Type Hints | ❌ Nee | ✅ Volledig |
| Logging | ❌ Alleen prints | ✅ Proper logging |
| CLI Arguments | ❌ Hardcoded | ✅ argparse |
| Progress Bar | ❌ Nee | ✅ Optional tqdm |
| Encoding | ❌ Alleen UTF-8 | ✅ Meerdere fallbacks |
| Overschrijf Check | ❌ Nee | ✅ Vraagt bevestiging |
| Code Documentatie | ⚠️ Basic | ✅ Uitgebreid met types |
| Error Messages | ⚠️ Generic | ✅ Specifiek en duidelijk |

---

## 🚀 Gebruik

### Basis gebruik:
```bash
python postcode_lookup_improved.py adressen.txt
```

### Met custom output:
```bash
python postcode_lookup_improved.py adressen.txt -o mijn_resultaat.csv
```

### Verbose mode (debug logging):
```bash
python postcode_lookup_improved.py adressen.txt --verbose
```

### Zonder progress bar:
```bash
python postcode_lookup_improved.py adressen.txt --no-progress
```

### Help:
```bash
python postcode_lookup_improved.py --help
```

---

## 📦 Dependencies

**Minimaal (werkt zonder extra packages):**
```bash
# Alleen Python 3.7+ standard library + requests
pip install requests
```

**Aanbevolen (met progress bar):**
```bash
pip install requests tqdm
```

---

## ✅ Testen

Om de verbeterde versie te testen, maak een test bestand:

```bash
# adressen_test.txt
Barrierweg 1, EINDHOVEN
Pasqualinistraat 10, EINDHOVEN
Dam 1, AMSTERDAM
```

Dan run:
```bash
python postcode_lookup_improved.py adressen_test.txt -v
```
