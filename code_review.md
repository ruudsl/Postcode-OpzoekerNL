# Code Review: PDOK Postcode Opzoeker

## 🔴 Kritieke Problemen

### 1. Import Conflict in main()
**Locatie:** regel 114-118
```python
try:
    import requests
except ImportError:
    print("❌ De 'requests' library is niet geïnstalleerd.")
```
**Probleem:** `requests` wordt al bovenaan het bestand geïmporteerd (regel 1). Als het niet geïnstalleerd is, crasht het script al bij het starten. Deze check is nutteloos.

**Fix:** Verwijder deze check of verplaats alle imports naar binnen de main functie.

---

### 2. Import binnen functie
**Locatie:** regel 36
```python
import re
```
**Probleem:** Import statement staat binnen een functie. Dit is inefficiënt en niet volgens Python best practices.

**Fix:** Verplaats naar de top van het bestand.

---

### 3. Geen timeout op HTTP requests
**Locatie:** regel 22
```python
response = requests.get(base_url, params=params)
```
**Probleem:** Geen timeout gespecificeerd. Het script kan oneindig hangen bij trage verbindingen.

**Fix:**
```python
response = requests.get(base_url, params=params, timeout=10)
```

---

## 🟡 Belangrijke Verbeteringen

### 4. Te brede exception handling
**Locatie:** regel 42-43
```python
except Exception as e:
    return f"Error: {str(e)}"
```
**Probleem:** Vangt ALLE exceptions, inclusief KeyboardInterrupt, SystemExit, etc. Moeilijk te debuggen.

**Fix:** Specificeer welke exceptions je verwacht:
```python
except (requests.RequestException, KeyError, ValueError) as e:
    return f"Error: {str(e)}"
```

---

### 5. Inconsistente postcode formatting
**Locatie:** regel 38
```python
return match.group(1).replace(' ', '')
```
**Probleem:** Postcodes worden soms wel, soms niet met spatie teruggegeven.

**Fix:** Consistente formatting toepassen op beide returns:
```python
if 'postcode' in result:
    postcode = result['postcode'].replace(' ', '')
    return postcode
```

---

### 6. Geen rate limit handling
**Locatie:** regel 22-25
**Probleem:** PDOK API heeft rate limits. Geen handling voor 429 (Too Many Requests) errors.

**Fix:** Check response status en voeg retry logic toe:
```python
if response.status_code == 429:
    time.sleep(2)
    # Retry logic
elif response.status_code == 200:
    # Process response
```

---

### 7. Sleep tijd te kort
**Locatie:** regel 70
```python
time.sleep(0.1)
```
**Probleem:** 0.1 seconde = 600 requests per minuut. Dit kan rate limits triggeren.

**Fix:** Verhoog naar minimaal 0.2-0.5 seconden:
```python
time.sleep(0.3)  # ~200 requests per minuut
```

---

## 🟢 Suggesties voor Verbetering

### 8. Hardcoded bestandsnamen
**Locatie:** regel 107-108
```python
input_file = 'adressen.txt'
output_file = f'postcodes_resultaat_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
```
**Suggestie:** Gebruik argparse voor command-line argumenten:
```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Input bestand met adressen')
parser.add_argument('-o', '--output', help='Output CSV bestand')
```

---

### 9. Geen input validatie
**Locatie:** clean_address() functie
**Suggestie:** Valideer of input lijkt op een Nederlands adres:
```python
def validate_dutch_address(address):
    """Simpele check of het lijkt op een Nederlands adres"""
    # Moet minimaal cijfers en letters bevatten
    import re
    if not re.search(r'\d+', address):  # Geen huisnummer
        return False
    if len(address) < 5:  # Te kort
        return False
    return True
```

---

### 10. Geen logging
**Suggestie:** Gebruik logging module voor betere debugging:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Verwerken: {address}")
logger.error(f"Error bij {address}: {e}")
```

---

### 11. Geen progress indicator voor grote bestanden
**Suggestie:** Gebruik tqdm voor een progress bar:
```python
from tqdm import tqdm

for i, address in enumerate(tqdm(addresses, desc="Postcodes ophalen"), 1):
    # ...
```

---

### 12. CSV delimiter niet expliciet
**Locatie:** regel 79
**Suggestie:** Specificeer expliciet:
```python
writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
```

---

## 🔵 Code Kwaliteit

### 13. Type hints ontbreken
**Suggestie:** Voeg type hints toe voor betere code documentatie:
```python
def clean_address(address_line: str) -> Optional[str]:
    """..."""

def get_postcode_pdok(address: str) -> str:
    """..."""
```

---

### 14. Magic numbers
**Locatie:** Diverse plekken
```python
rows: 1  # Waarom 1?
time.sleep(0.1)  # Waarom 0.1?
if len(not_found) <= 10:  # Waarom 10?
```
**Suggestie:** Gebruik constanten:
```python
MAX_RESULTS = 1
API_DELAY_SECONDS = 0.3
MAX_DISPLAY_NOT_FOUND = 10
```

---

### 15. Duplicaat code bij file writing
**Locatie:** regel 79-85 en 88-91
**Suggestie:** Maak aparte functies:
```python
def write_csv_results(results, output_file):
    """Schrijf resultaten naar CSV"""
    # ...

def write_postcode_list(results, output_file):
    """Schrijf alleen postcodes naar tekstbestand"""
    # ...
```

---

## 🔒 Security & Robustness

### 16. Geen encoding error handling
**Locatie:** regel 48, 78, 88
**Suggestie:** Voeg error handling toe:
```python
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        # ...
except UnicodeDecodeError:
    # Probeer andere encoding
    with open(input_file, 'r', encoding='latin-1') as f:
        # ...
```

---

### 17. Geen check of output bestand bestaat
**Suggestie:** Waarschuw gebruiker als bestand overschreven wordt:
```python
import os
if os.path.exists(output_file):
    response = input(f"{output_file} bestaat al. Overschrijven? (j/n): ")
    if response.lower() != 'j':
        return
```

---

## ✅ Positieve Punten

1. ✅ Goede gebruik van PDOK API (gratis, betrouwbaar)
2. ✅ Cache implementatie voor duplicaten
3. ✅ Duidelijke output en samenvatting
4. ✅ Goede documentatie strings
5. ✅ Timestamp in output bestandsnaam voorkomt overschrijven
6. ✅ Beide CSV en TXT output formaten

---

## 📊 Samenvatting Prioriteiten

### Must Fix (voor productie):
1. Verwijder dubbele import check
2. Voeg timeout toe aan requests
3. Verbeter exception handling
4. Verhoog sleep tijd

### Should Fix (voor betere kwaliteit):
5. Verplaats `import re` naar top
6. Maak postcode formatting consistent
7. Voeg rate limit handling toe
8. Voeg command-line argumenten toe

### Nice to Have:
9. Type hints
10. Logging i.p.v. prints
11. Progress bar
12. Input validatie
13. Constanten voor magic numbers

---

## 📝 Aanbevolen Refactored Versie

Ik kan een verbeterde versie maken met alle fixes toegepast. Wil je dat ik dat doe?
