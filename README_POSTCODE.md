# PDOK Postcode Opzoeker - Verbeterde Versie

## 📋 Overzicht

Dit project bevat een code review en verbeterde versie van een Python script dat postcodes ophaalt via de PDOK Locatieserver API (Nederlandse overheidsdata).

## 📁 Bestanden

- **`code_review.md`** - Uitgebreide code review van de originele code met 17 geïdentificeerde issues
- **`postcode_lookup_improved.py`** - Volledig verbeterde versie met alle fixes toegepast
- **`IMPROVEMENTS.md`** - Gedetailleerde vergelijking van wat er verbeterd is
- **`adressen_test.txt`** - Test bestand met 10 Nederlandse adressen

## 🚀 Snelstart

### Installatie

```bash
# Minimaal (alleen requests nodig)
pip install requests

# Aanbevolen (met progress bar)
pip install requests tqdm
```

### Gebruik

```bash
# Basis gebruik
python postcode_lookup_improved.py adressen.txt

# Met custom output bestand
python postcode_lookup_improved.py adressen.txt -o mijn_resultaat.csv

# Verbose mode (debug logging)
python postcode_lookup_improved.py adressen.txt --verbose

# Zonder progress bar
python postcode_lookup_improved.py adressen.txt --no-progress

# Help
python postcode_lookup_improved.py --help
```

### Test het script

```bash
# Gebruik het meegeleverde test bestand
python postcode_lookup_improved.py adressen_test.txt -o test_resultaat.csv
```

## 🔧 Belangrijkste Verbeteringen

### 🔴 Kritieke Fixes

1. **HTTP Timeout toegevoegd** (10 seconden) - voorkomt oneindig hangen
2. **Rate limiting handling** - Retry logic voor 429 (Too Many Requests) errors
3. **Specifieke exception handling** - Vangt alleen verwachte exceptions
4. **Consistente postcode formatting** - Altijd formaat `1234AB` (zonder spatie)
5. **API delay verhoogd** - Van 0.1s naar 0.3s (~200 req/min, veilig voor API)

### 🟢 Extra Features

6. **Command-line argumenten** - Geen hardcoded bestandsnamen meer
7. **Type hints** - Volledige type annotaties voor betere code documentatie
8. **Logging** - Proper logging ipv print statements
9. **Input validatie** - Controleert of adressen geldig lijken
10. **Progress bar** - Optioneel via tqdm (met fallback)
11. **Encoding fallbacks** - Probeert meerdere encodings (utf-8, latin-1, cp1252)
12. **Overschrijf waarschuwing** - Vraagt bevestiging als output bestand bestaat
13. **Constanten** - Alle magic numbers zijn nu benoemde constanten
14. **Betere error messages** - Specifieke errors voor verschillende situaties

## 📊 Vergelijking

| Feature | Origineel | Verbeterd |
|---------|-----------|-----------|
| HTTP Timeout | ❌ Nee | ✅ 10 seconden |
| Rate Limiting | ❌ Nee | ✅ Retry met exponential backoff |
| Exception Handling | ❌ Te breed (`except Exception`) | ✅ Specifieke exceptions |
| Postcode Format | ❌ Inconsistent | ✅ Consistent (1234AB) |
| API Delay | ⚠️ 0.1s (600/min, te snel) | ✅ 0.3s (200/min, veilig) |
| Input Validatie | ❌ Nee | ✅ Valideert adressen |
| Type Hints | ❌ Nee | ✅ Volledig |
| Logging | ❌ Alleen prints | ✅ Proper logging met levels |
| CLI Arguments | ❌ Hardcoded | ✅ argparse |
| Progress Bar | ❌ Nee | ✅ Optioneel (tqdm) |
| Encoding | ❌ Alleen UTF-8 | ✅ Meerdere fallbacks |

## 📖 Documentatie

Zie de volgende bestanden voor meer details:

- **`code_review.md`** - Volledige analyse van alle gevonden problemen
- **`IMPROVEMENTS.md`** - Voor/na vergelijking met code voorbeelden

## 🎯 Code Kwaliteit Verbeteringen

- ✅ Alle imports bovenaan bestand
- ✅ Functies zijn kleiner en doen één ding (Single Responsibility)
- ✅ Constanten voor alle magic numbers
- ✅ Uitgebreide docstrings met type hints
- ✅ Proper error handling met specifieke exceptions
- ✅ Logging met verschillende levels (INFO, WARNING, ERROR, DEBUG)
- ✅ Code structuur volgens Python best practices

## 🔒 Security & Robustness

- ✅ Timeout op alle HTTP requests
- ✅ Rate limiting met retry logic
- ✅ Input validatie
- ✅ Meerdere encoding fallbacks
- ✅ Graceful error handling
- ✅ Geen credentials in code
- ✅ Gebruikt officiële overheids-API (PDOK)

## 📝 Voorbeeld Input

Het `adressen.txt` bestand moet één adres per regel bevatten:

```
Barrierweg 1, EINDHOVEN
Pasqualinistraat 10, EINDHOVEN
Dam 1, AMSTERDAM
Coolsingel 40, ROTTERDAM
```

## 📤 Output

Het script genereert twee bestanden:

1. **CSV bestand** (`postcodes_resultaat_TIMESTAMP.csv`):
   ```csv
   regel_nummer,adres,postcode
   1,Barrierweg 1, EINDHOVEN,5629CD
   2,Dam 1, AMSTERDAM,1012JS
   ```

2. **Tekstbestand** (`postcodes_resultaat_TIMESTAMP_postcodes.txt`):
   ```
   5629CD
   1012JS
   ```

## 🛠️ Technische Details

- **Python versie**: 3.7+
- **Dependencies**: requests (verplicht), tqdm (optioneel)
- **API**: PDOK Locatieserver v3.1 (gratis, geen API key nodig)
- **Rate limit**: ~200 requests per minuut (veilig)
- **Timeout**: 10 seconden per request
- **Max retries**: 3 (bij rate limiting)

## ⚙️ Configuratie

Constanten kunnen aangepast worden bovenaan `postcode_lookup_improved.py`:

```python
MAX_RESULTS = 1                    # Aantal resultaten per zoekopdracht
API_TIMEOUT_SECONDS = 10           # HTTP timeout
API_DELAY_SECONDS = 0.3            # Delay tussen requests
MAX_RETRIES = 3                    # Max retries bij rate limiting
RETRY_DELAY_SECONDS = 2            # Delay tussen retries
MAX_DISPLAY_NOT_FOUND = 10         # Max niet-gevonden adressen om te tonen
```

## 🐛 Error Handling

Het script handelt de volgende situaties af:

- **Timeout**: Max 10 seconden per request
- **Rate limiting (429)**: Automatische retry met exponential backoff
- **Network errors**: Duidelijke error messages
- **Invalid encoding**: Probeert meerdere encodings
- **Missing file**: Duidelijke error message
- **Permission errors**: Duidelijke error message
- **Keyboard interrupt (Ctrl+C)**: Graceful shutdown
- **Invalid addresses**: Warning maar gaat door met volgende

## 📜 License

Dit is voorbeeldcode voor educatieve doeleinden.

## 👤 Credits

- PDOK Locatieserver API (Nederlandse overheid): https://api.pdok.nl/
- Verbeterde versie: Code review en refactoring
