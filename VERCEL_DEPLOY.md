# 🚀 Vercel Deployment Guide

Complete gids voor het deployen van de PDOK Postcode Opzoeker op Vercel.

## ⚠️ Belangrijke Beperkingen

Vercel gebruikt **serverless functions**, daarom heeft deze versie enkele beperkingen:

| Feature | Lokaal (app.py) | Vercel (api/index.py) |
|---------|-----------------|------------------------|
| **Max adressen** | Onbeperkt | 20 per keer (10s timeout) |
| **File upload** | ✅ Ja | ❌ Nee (alleen text input) |
| **Real-time progress** | ✅ SSE | ❌ Nee (synchroon) |
| **Background jobs** | ✅ Ja | ❌ Nee (direct response) |
| **Concurrent requests** | ✅ Ja | ✅ Ja |

Voor grote bestanden (50+ adressen), gebruik de CLI versie lokaal!

---

## 🚀 Deployment Stappen

### Optie 1: Via Vercel Dashboard (Eenvoudigst)

1. **Ga naar Vercel**: https://vercel.com/new

2. **Import repository**:
   - Klik "Import Git Repository"
   - Selecteer `ruudsl/test`
   - Of plak: `https://github.com/ruudsl/test`

3. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (blijf in root)
   - **Build Command**: (leeg laten)
   - **Output Directory**: (leeg laten)

4. **Environment Variables**: (niet nodig voor deze app)

5. **Deploy**: Klik "Deploy"

Vercel detecteert automatisch `vercel.json` en `api/index.py`!

---

### Optie 2: Via Vercel CLI

```bash
# Installeer Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy (vanuit project directory)
cd /path/to/test
vercel

# Of direct naar productie
vercel --prod
```

---

## 📁 Vercel Project Structuur

De Vercel versie gebruikt een aangepaste structuur:

```
test/
├── api/
│   ├── index.py              # Vercel serverless handler ✨
│   └── requirements.txt      # Python deps voor Vercel ✨
├── templates/
│   ├── index.html            # Originele template (lokaal)
│   └── index_vercel.html     # Vereenvoudigde template ✨
├── vercel.json               # Vercel configuratie ✨
├── app.py                    # Originele Flask app (lokaal)
└── ...
```

**Nieuw toegevoegd:**
- `vercel.json` - Vercel routing configuratie
- `api/index.py` - Serverless Flask wrapper
- `api/requirements.txt` - Dependencies voor Vercel
- `templates/index_vercel.html` - Simplified UI

---

## ⚙️ Vercel Configuratie

`vercel.json` legt uit hoe Vercel de app moet deployen:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

- **builds**: Compileert `api/index.py` als Python serverless function
- **routes**: Stuurt alle requests naar deze function

---

## 🔍 Verschillen: Lokaal vs Vercel

### Lokaal (app.py)
```python
# Background thread processing
thread = Thread(target=process_file_job)
thread.start()

# In-memory job tracking
jobs = {}

# File uploads
file.save(filepath)
```

### Vercel (api/index.py)
```python
# Synchronous processing
result = process_addresses_sync(addresses)
return jsonify(result)

# No state preservation
# No file uploads
# Direct response
```

---

## ✅ Test Na Deployment

### 1. Open de URL
Vercel geeft je een URL zoals:
```
https://test-xxx.vercel.app
```

### 2. Test met voorbeeldadressen
```
Dam 1, AMSTERDAM
Barrierweg 1, EINDHOVEN
Coolsingel 40, ROTTERDAM
```

### 3. Check de resultaten
- Postcodes verschijnen na ~5-10 seconden
- Download CSV/TXT werkt
- Statistieken kloppen

---

## 🐛 Troubleshooting

### Error: "FUNCTION_INVOCATION_FAILED"

**Oorzaak 1:** Template niet gevonden

**Fix:** Vercel moet templates vinden. Check of `templates/` in root staat.

**Oorzaak 2:** Dependencies niet geïnstalleerd

**Fix:** Check `api/requirements.txt` bestaat en is correct.

**Oorzaak 3:** Python syntax error

**Fix:** Test lokaal:
```bash
cd api
python3 index.py
```

---

### Error: "Module not found"

**Probleem:** Python packages niet geïnstalleerd

**Fix:** Voeg toe aan `api/requirements.txt`:
```
Flask==3.0.0
requests==2.31.0
```

---

### Error: "FUNCTION_INVOCATION_TIMEOUT"

**Probleem:** Verwerking duurt >10 seconden

**Oorzaak:** Te veel adressen (>20)

**Fix:** De UI limiteert tot 20, maar check input.

---

### Error: "404 Not Found"

**Probleem:** Route werkt niet

**Fix:** Check `vercel.json` routes:
```json
{
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

---

### Template rendering fails

**Probleem:** Flask kan `templates/` niet vinden

**Fix:** In `api/index.py`:
```python
app = Flask(__name__, template_folder='../templates')
```

Het `..` pad werkt op Vercel!

---

## 📊 Vercel Logs Bekijken

### Via Dashboard
1. Ga naar https://vercel.com/dashboard
2. Selecteer je project
3. Ga naar "Deployments"
4. Klik op een deployment
5. Klik "Functions" tab
6. Bekijk logs

### Via CLI
```bash
vercel logs
```

---

## 🎯 Performance Tips

### 1. Limiet aantal adressen
```python
if len(addresses) > 20:
    return jsonify({'error': 'Maximum 20 adressen'}), 400
```

### 2. Optimale API delay
```python
API_DELAY_SECONDS = 0.3  # ~200 req/min (veilig)
```

### 3. Timeout handling
```python
API_TIMEOUT_SECONDS = 10
```

### 4. Cache duplicaten
```python
cache = {}
if address in cache:
    postcode = cache[address]
```

---

## 🔒 Security

Vercel deployment is automatisch veilig:

- ✅ HTTPS automatisch
- ✅ DDoS protection
- ✅ Rate limiting (per function)
- ✅ Geen file system access
- ✅ Isolated functions

---

## 💰 Kosten

**Vercel Free Tier:**
- ✅ 100GB bandwidth/maand
- ✅ 100 deployments/dag
- ✅ Serverless Function Execution:
  - Free: 100 GB-Hours
  - ~20s per 20 adressen = ~0.006 GB-Hours
  - = ~16,000 lookups/maand gratis!

Voor meer: https://vercel.com/pricing

---

## 🔄 Updates Deployen

### Automatisch (aanbevolen)
Vercel monitort je GitHub repo:
1. Push naar GitHub
2. Vercel deploy automatisch
3. Nieuwe versie live!

```bash
git add .
git commit -m "Update feature X"
git push origin main
```

### Handmatig
```bash
vercel --prod
```

---

## 🌐 Custom Domain

1. Ga naar Project Settings
2. Domains tab
3. Add Domain
4. Voer je domain in (bijv. `postcodes.jouwdomein.nl`)
5. Volg DNS instructies
6. Klaar!

---

## 📈 Monitoring

Vercel Dashboard toont:
- Request count
- Error rate
- Function duration
- Bandwidth usage
- Geographic distribution

---

## 🎛️ Environment Variables

Als je API keys nodig hebt later:

1. Vercel Dashboard → Project → Settings
2. Environment Variables
3. Voeg toe:
   - Name: `API_KEY`
   - Value: `your-secret-key`
4. Redeploy

In code:
```python
import os
API_KEY = os.environ.get('API_KEY')
```

---

## ✨ Production Checklist

Voor je live gaat:

- [ ] Deployment succesvol
- [ ] Test met echte adressen
- [ ] CSV/TXT download werkt
- [ ] Error handling getest
- [ ] Logs bekeken (geen errors)
- [ ] Performance OK (<10s response)
- [ ] Mobile responsive checked
- [ ] Custom domain (optioneel)

---

## 🆚 Wanneer Welke Versie?

| Gebruik | Versie |
|---------|--------|
| **Snel testen, paar adressen** | ✅ Vercel |
| **Delen met anderen** | ✅ Vercel |
| **50+ adressen** | ❌ CLI lokaal |
| **Bulk processing** | ❌ CLI lokaal |
| **File uploads** | ❌ Lokale Flask |
| **Real-time progress** | ❌ Lokale Flask |
| **Altijd beschikbaar** | ✅ Vercel |

---

## 🎉 Klaar!

Je Vercel deployment is nu live:

```
https://jouw-project.vercel.app
```

Test het, deel het, en geniet! 🚀

---

## 📞 Hulp Nodig?

- Vercel Docs: https://vercel.com/docs
- Flask op Vercel: https://vercel.com/guides/using-flask-with-vercel
- Deze repo: https://github.com/ruudsl/test

**Error blijven?** Check de Vercel logs - daar staat precies wat er fout gaat!
