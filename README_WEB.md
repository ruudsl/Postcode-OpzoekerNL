# 🌐 PDOK Postcode Opzoeker - Web Interface

Een moderne, gebruiksvriendelijke web applicatie voor het opzoeken van postcodes via de PDOK Locatieserver API.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🎨 **Moderne UI** - Responsive design met gradient styling
- 📁 **Drag & Drop Upload** - Sleep bestanden naar de browser
- ✍️ **Handmatige Invoer** - Voer adressen direct in
- ⏱️ **Real-time Progress** - Live voortgang via Server-Sent Events
- 📊 **Statistieken Dashboard** - Overzicht van resultaten
- 💾 **Download Resultaten** - CSV en TXT formaat
- 🔒 **Veilig & Betrouwbaar** - Gebruikt officiële Nederlandse overheidsdata
- 📱 **Mobile Friendly** - Werkt op alle apparaten

## 🚀 Snelstart

### Installatie

```bash
# Kloon of download de repository
cd /path/to/project

# Installeer dependencies
pip install -r requirements.txt

# Start de server
python app.py
```

De applicatie draait nu op: **http://localhost:5000**

### Docker (Optioneel)

```bash
# Bouw de container
docker build -t postcode-lookup .

# Run de container
docker run -p 5000:5000 postcode-lookup
```

## 📖 Gebruik

### Optie 1: Bestand Uploaden

1. Klik op de **"📁 Bestand Uploaden"** tab
2. Sleep een `.txt` bestand naar de upload zone (of klik om te selecteren)
3. Het bestand wordt automatisch verwerkt
4. Download de resultaten als CSV of TXT

**Bestandsformaat:**
```
Barrierweg 1, EINDHOVEN
Pasqualinistraat 10, EINDHOVEN
Dam 1, AMSTERDAM
Coolsingel 40, ROTTERDAM
```

### Optie 2: Handmatig Invoeren

1. Klik op de **"✍️ Handmatig Invoeren"** tab
2. Voer adressen in (één per regel)
3. Klik op **"🔍 Zoek Postcodes"**
4. Download de resultaten

## 🏗️ Project Structuur

```
.
├── app.py                      # Flask backend applicatie
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Frontend HTML/CSS/JS
├── static/                    # Statische bestanden (toekomstig)
│   ├── css/
│   └── js/
├── uploads/                   # Geüploade bestanden (tijdelijk)
├── results/                   # Gegenereerde resultaten
└── README_WEB.md              # Deze documentatie
```

## 🔧 API Endpoints

### `POST /api/upload`
Upload een tekstbestand met adressen

**Request:**
- `file`: `.txt` bestand (max 16MB)

**Response:**
```json
{
  "job_id": "uuid-v4-string"
}
```

### `POST /api/process-text`
Verwerk direct ingevoerde adressen

**Request:**
```json
{
  "addresses": "Barrierweg 1, EINDHOVEN\nDam 1, AMSTERDAM"
}
```

**Response:**
```json
{
  "job_id": "uuid-v4-string"
}
```

### `GET /api/status/<job_id>`
Haal job status op

**Response:**
```json
{
  "id": "job-id",
  "status": "processing",
  "progress": 45,
  "processed": 45,
  "total": 100,
  "filename": "adressen.txt"
}
```

### `GET /api/stream/<job_id>`
Real-time progress updates via Server-Sent Events

**Response:** Streaming JSON events

### `GET /api/download/<job_id>/<file_type>`
Download resultaten
- `file_type`: `csv` of `txt`

### `GET /api/stats`
Algemene statistieken

**Response:**
```json
{
  "total_jobs": 42,
  "completed": 38,
  "processing": 2,
  "errors": 2
}
```

## ⚙️ Configuratie

Pas constanten aan in `app.py`:

```python
# API Settings
API_TIMEOUT_SECONDS = 10       # HTTP timeout
API_DELAY_SECONDS = 0.3        # Delay tussen requests (~200/min)
MAX_RETRIES = 3                # Max retries bij rate limiting

# Upload Settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max bestandsgrootte (16MB)
UPLOAD_FOLDER = Path("uploads")        # Upload directory
RESULTS_FOLDER = Path("results")       # Results directory
```

## 🎨 UI Features

### Responsive Design
- Desktop: Volledig dashboard met alle features
- Tablet: Aangepaste layout
- Mobile: Gestapelde weergave

### Real-time Updates
- Progress bar met percentage
- Live teller van verwerkte adressen
- Automatische refresh bij completion

### Statistieken Dashboard
- 📊 Totaal aantal adressen
- ✅ Gevonden postcodes (groen)
- ⚠️ Niet gevonden (oranje)
- ❌ Errors (rood)

### Preview Resultaten
- Toont eerste 10 resultaten inline
- Color-coded postcodes:
  - **Blauw**: Succesvol gevonden
  - **Oranje**: Niet gevonden
  - **Rood**: Error

## 🔒 Security Features

- ✅ Bestandsgrootte limiet (16MB)
- ✅ Alleen `.txt` bestanden toegestaan
- ✅ Unieke job IDs (UUID v4)
- ✅ Server-side validatie
- ✅ Timeout op alle HTTP requests
- ✅ Rate limiting bescherming
- ✅ Input sanitization

## 🚀 Production Deployment

### Met Gunicorn

```bash
# Installeer Gunicorn
pip install gunicorn

# Run productie server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Met Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name postcodes.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Environment Variables

```bash
export FLASK_ENV=production
export FLASK_APP=app.py
```

## 📊 Performance

### Capaciteit
- ~200 requests per minuut naar PDOK API (veilig)
- Multiple concurrent jobs ondersteund
- Server-Sent Events voor real-time updates

### Optimalisaties
- In-memory cache voor duplicaat adressen
- Asynchrone job processing (threads)
- Geen database nodig (file-based)

## 🐛 Troubleshooting

### Port al in gebruik
```bash
# Linux/Mac: Zoek proces op port 5000
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <pid> /F
```

### Upload directory niet beschrijfbaar
```bash
chmod 755 uploads results
```

### PDOK API niet bereikbaar
- Check internet verbinding
- Controleer firewall instellingen
- PDOK gebruikt HTTPS (poort 443)

### Progress niet zichtbaar
- Browser ondersteunt geen Server-Sent Events (gebruik moderne browser)
- Fallback naar polling wordt automatisch geactiveerd

## 📝 Changelog

### v1.0.0 (2024-01-13)
- ✨ Initiële release
- 🎨 Moderne gradient UI
- 📁 Drag & drop upload
- ✍️ Handmatige invoer optie
- ⏱️ Real-time progress updates
- 📊 Statistieken dashboard
- 💾 CSV en TXT downloads

## 🤝 Contributing

Suggesties en verbeteringen zijn welkom! Maak een issue of pull request aan.

## 📜 License

Dit project is open source en beschikbaar onder de MIT License.

## 👏 Credits

- **PDOK Locatieserver API**: Nederlandse overheid
- **Flask**: Web framework
- **Modern UI**: Custom CSS met gradient designs

## 🔗 Links

- [PDOK Locatieserver Documentatie](https://www.pdok.nl/restful-api/-/article/pdok-locatieserver)
- [Flask Documentatie](https://flask.palletsprojects.com/)
- [Python Requests](https://requests.readthedocs.io/)

---

**Gemaakt met ❤️ voor eenvoudige postcode lookup**
