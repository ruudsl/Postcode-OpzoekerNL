# PDOK Postcode Opzoeker - Complete Suite

Een complete toolkit voor het opzoeken van Nederlandse postcodes via de PDOK Locatieserver API (overheidsdata).

## 📦 Wat zit er in dit project?

Dit project bevat **3 verschillende tools**:

1. **🌐 Web Interface** (`app.py`) - Moderne browser-based applicatie
2. **💻 CLI Tool - Verbeterd** (`postcode_lookup_improved.py`) - Command-line interface met alle fixes
3. **📝 Todo CLI** (`todo.py`) - Bonus: Task management tool

## 🚀 Snelstart

### Web Interface (Aanbevolen)

De gemakkelijkste manier om te starten:

```bash
# Installeer dependencies
pip install -r requirements.txt

# Start de web server
python app.py

# Of gebruik het start script
./start_web.sh
```

Open je browser naar: **http://localhost:5000**

### Command-Line Tool

Voor terminal gebruikers:

```bash
# Basis gebruik
python postcode_lookup_improved.py adressen.txt

# Met opties
python postcode_lookup_improved.py adressen.txt -o output.csv --verbose

# Help
python postcode_lookup_improved.py --help
```

---

## 📚 Documentatie

- **[README_WEB.md](README_WEB.md)** - Volledige web interface documentatie
- **[README_POSTCODE.md](README_POSTCODE.md)** - CLI tool documentatie
- **[code_review.md](code_review.md)** - Uitgebreide code review (17 gevonden issues)
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Voor/na vergelijking van alle fixes

---

## 🌐 Web Interface Features

- ✨ **Moderne UI** - Responsive gradient design
- 📁 **Drag & Drop** - Sleep bestanden naar de browser
- ✍️ **Handmatige invoer** - Type adressen direct in
- ⏱️ **Real-time progress** - Live updates via Server-Sent Events
- 📊 **Dashboard** - Statistieken en overzichten
- 💾 **Downloads** - CSV en TXT formaten
- 🔒 **Veilig** - Input validatie en rate limiting

### Screenshot Concept

```
┌──────────────────────────────────────────────────┐
│  📮 PDOK Postcode Opzoeker                      │
│  Zoek eenvoudig postcodes op via overheidsdata  │
├──────────────────────────────────────────────────┤
│                                                  │
│  [📁 Bestand Uploaden] [✍️ Handmatig Invoeren] │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │        📤 Sleep bestand hierheen          │ │
│  │     of klik om te selecteren              │ │
│  │    Alleen .txt bestanden (max 16MB)       │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  Progress: ████████████░░░░░░  75%              │
│  Verwerkt: 75 / 100 adressen                    │
│                                                  │
│  ┌─────────┬──────────┬────────────┬─────────┐ │
│  │ Totaal  │ Gevonden │ Niet Found │ Errors  │ │
│  │   100   │    94    │     4      │    2    │ │
│  └─────────┴──────────┴────────────┴─────────┘ │
│                                                  │
│  [📊 Download CSV]  [📄 Download TXT]          │
└──────────────────────────────────────────────────┘
```

---

## 💻 CLI Tool Features

De verbeterde command-line versie bevat alle fixes:

- ✅ HTTP timeout (10 seconden)
- ✅ Rate limiting met retry logic
- ✅ Specifieke exception handling
- ✅ Consistente postcode formatting
- ✅ Input validatie
- ✅ Type hints
- ✅ Proper logging
- ✅ Command-line argumenten
- ✅ Progress bar (optioneel via tqdm)
- ✅ Multiple encoding support

---

## 🏗️ Project Structuur

```
.
├── app.py                          # Flask web applicatie
├── postcode_lookup_improved.py     # CLI tool (verbeterd)
├── todo.py                         # Bonus: Todo CLI
├── requirements.txt                # Python dependencies
│
├── templates/
│   └── index.html                  # Web UI
│
├── static/                         # Frontend assets
│   ├── css/
│   └── js/
│
├── uploads/                        # Temp uploads (auto-created)
├── results/                        # Generated results (auto-created)
│
├── Dockerfile                      # Docker container
├── docker-compose.yml              # Docker Compose config
├── start_web.sh                    # Quick start script
│
├── README.md                       # Dit bestand
├── README_WEB.md                   # Web interface docs
├── README_POSTCODE.md              # CLI docs
├── code_review.md                  # Code review (17 issues)
├── IMPROVEMENTS.md                 # Improvements details
│
└── adressen_test.txt              # Test data (10 adressen)
```

---

## 🔧 Installatie

### Methode 1: Quick Start (Linux/Mac)

```bash
./start_web.sh
```

### Methode 2: Handmatig

```bash
# Maak virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# of
venv\Scripts\activate     # Windows

# Installeer dependencies
pip install -r requirements.txt

# Start web interface
python app.py

# Of gebruik CLI tool
python postcode_lookup_improved.py adressen.txt
```

### Methode 3: Docker

```bash
# Met docker-compose (eenvoudigst)
docker-compose up

# Of met docker
docker build -t postcode-lookup .
docker run -p 5000:5000 postcode-lookup
```

---

## 📝 Gebruik

### Web Interface

1. **Start de server**: `python app.py`
2. **Open browser**: http://localhost:5000
3. **Upload of typ adressen**
4. **Download resultaten**

### CLI Tool

```bash
# Basis
python postcode_lookup_improved.py adressen.txt

# Custom output
python postcode_lookup_improved.py adressen.txt -o mijn_output.csv

# Verbose mode
python postcode_lookup_improved.py adressen.txt -v

# Zonder progress bar
python postcode_lookup_improved.py adressen.txt --no-progress
```

### Input Formaat

Beide tools verwachten hetzelfde formaat:

```
Barrierweg 1, EINDHOVEN
Pasqualinistraat 10, EINDHOVEN
Dam 1, AMSTERDAM
Coolsingel 40, ROTTERDAM
```

### Output Formaten

**CSV:**
```csv
regel_nummer,adres,postcode
1,Barrierweg 1, EINDHOVEN,5629CD
2,Dam 1, AMSTERDAM,1012JS
```

**TXT:**
```
5629CD
1012JS
```

---

## 🔍 Code Review & Improvements

Dit project bevat een uitgebreide code review van een originele PDOK postcode lookup script.

### Gevonden Issues (17 totaal)

#### 🔴 Kritiek (7)
1. Geen HTTP timeout → Kan oneindig hangen
2. Geen rate limiting → API kan blokkeren
3. Te brede exception handling → Moeilijk debuggen
4. Import conflict → Dubbele import check
5. Inconsistente postcode formatting → Verschillende formaten
6. Te korte API delay (0.1s → 600 req/min)
7. Import in functie → Inefficiënt

#### 🟢 Verbeteringen (10)
8. Hardcoded bestandsnamen
9. Geen input validatie
10. Geen logging (alleen prints)
11. Geen progress bar
12. Magic numbers
13. Geen type hints
14. Geen encoding fallbacks
15. Geen overschrijf waarschuwing
16. Code structuur
17. Error messages niet specifiek

Alle issues zijn opgelost in `postcode_lookup_improved.py`!

---

## 📊 Vergelijking: Voor vs Na

| Feature | Voor | Na (Verbeterd) | Na (Web) |
|---------|------|----------------|----------|
| HTTP Timeout | ❌ | ✅ 10s | ✅ 10s |
| Rate Limiting | ❌ | ✅ Retry 3x | ✅ Retry 3x |
| API Delay | 0.1s (te snel) | 0.3s (veilig) | 0.3s (veilig) |
| Exception Handling | Generic | Specifiek | Specifiek |
| Input Validatie | ❌ | ✅ | ✅ |
| Type Hints | ❌ | ✅ 100% | ✅ 100% |
| Logging | Prints | Proper logging | Proper logging |
| UI | Terminal | Terminal | Browser ✨ |
| Progress | Tekst | Progress bar | Real-time ✨ |
| Download | Lokaal | Lokaal | Browser ✨ |
| Multiple files | ❌ | ❌ | ✅ Jobs ✨ |

---

## 🚀 Deployment

### Productie met Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Met Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name postcodes.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Heroku

```bash
# Procfile
web: gunicorn app:app

# Deploy
heroku create mijn-postcode-app
git push heroku main
```

---

## 🔒 Security

- ✅ Bestandsgrootte limiet (16MB)
- ✅ Alleen .txt bestanden toegestaan
- ✅ Server-side input validatie
- ✅ Timeout op alle HTTP requests
- ✅ Rate limiting bescherming
- ✅ Unieke job IDs (UUID v4)
- ✅ Geen credentials in code
- ✅ HTTPS naar PDOK API

---

## 📈 Performance

- **API Rate**: ~200 requests/minuut (veilig voor PDOK)
- **Concurrent Jobs**: Meerdere uploads tegelijk mogelijk
- **Max File Size**: 16MB (configureerbaar)
- **Caching**: In-memory voor duplicaat adressen
- **Real-time Updates**: Via Server-Sent Events

---

## 🤝 Contributing

Issues en pull requests zijn welkom!

### Development Setup

```bash
git clone <repo>
cd postcode-lookup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## 📜 License

MIT License - Vrij te gebruiken

---

## 🙏 Credits

- **PDOK Locatieserver**: Nederlandse overheid
- **Flask**: Web framework
- **Requests**: HTTP library

---

## 📞 Support

Vragen? Zie de documentatie:
- Web Interface: [README_WEB.md](README_WEB.md)
- CLI Tool: [README_POSTCODE.md](README_POSTCODE.md)
- Code Review: [code_review.md](code_review.md)

---

**Gemaakt met ❤️ voor eenvoudige Nederlandse postcode lookup**
