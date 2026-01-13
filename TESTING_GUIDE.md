# 🧪 Web Interface - Test Guide

Complete gids voor het testen van de PDOK Postcode Opzoeker web interface.

## 🚀 Quick Start Testing

### Stap 1: Start de Server

Kies één van deze methodes:

```bash
# Methode A: Quick start script (aanbevolen)
./start_web.sh

# Methode B: Direct starten
pip install -r requirements.txt
python app.py

# Methode C: Docker
docker-compose up
```

Je zou dit moeten zien:
```
============================================================
PDOK Postcode Opzoeker - Web Interface
============================================================

🌐 Server draait op: http://localhost:5000
📝 Upload adressen.txt bestanden of voer adressen handmatig in
⏸️  Stop met Ctrl+C

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### Stap 2: Open in Browser

Open je browser en ga naar: **http://localhost:5000**

Je zou een mooie paarse/blauwe gradient interface moeten zien met:
- Header "📮 PDOK Postcode Opzoeker"
- Twee tabs: "📁 Bestand Uploaden" en "✍️ Handmatig Invoeren"

---

## 🧪 Test Scenario's

### Test 1: Handmatige Invoer (Eenvoudigst)

1. **Klik op "✍️ Handmatig Invoeren" tab**

2. **Type enkele test adressen** (kopieer deze):
   ```
   Dam 1, AMSTERDAM
   Barrierweg 1, EINDHOVEN
   Coolsingel 40, ROTTERDAM
   ```

3. **Klik "🔍 Zoek Postcodes"**

4. **Je zou moeten zien:**
   - Progress bar die beweegt (0% → 100%)
   - "Verwerkt: X / Y adressen"
   - Na voltooiing: Statistieken dashboard

5. **Check resultaten:**
   - Totaal: 3
   - Gevonden: (hopelijk 3, of 0 als PDOK niet bereikbaar)
   - Preview met postcodes

6. **Download:**
   - Klik "📊 Download CSV"
   - Klik "📄 Download TXT"
   - Check de bestanden

**Verwacht resultaat (als PDOK bereikbaar):**
```csv
regel_nummer,adres,postcode
1,Dam 1, AMSTERDAM,1012JS
2,Barrierweg 1, EINDHOVEN,5629CD
3,Coolsingel 40, ROTTERDAM,3012AA
```

---

### Test 2: Bestand Upload

1. **Maak test bestand** `test_adressen.txt`:
   ```
   Dam 1, AMSTERDAM
   Kalverstraat 92, AMSTERDAM
   Barrierweg 1, EINDHOVEN
   Coolsingel 40, ROTTERDAM
   Neude 11, UTRECHT
   ```

2. **Klik op "📁 Bestand Uploaden" tab**

3. **Sleep het bestand** naar de upload zone
   - Of klik en selecteer het bestand

4. **Je zou moeten zien:**
   - Direct verwerking start
   - Progress bar update
   - Real-time counter

5. **Wacht op voltooiing** (~2-3 seconden per adres)

6. **Check resultaten en download**

---

### Test 3: Error Handling

Test of de error handling werkt:

#### 3A: Geen adressen
1. Ga naar "✍️ Handmatig Invoeren"
2. Laat het veld leeg
3. Klik "🔍 Zoek Postcodes"
4. **Verwacht**: Rode error message "Voer minimaal één adres in"

#### 3B: Verkeerd bestandstype
1. Maak `test.pdf` aan
2. Probeer te uploaden
3. **Verwacht**: Error "Alleen .txt bestanden zijn toegestaan"

#### 3C: Ongeldige adressen
```
Dit is geen adres
Nog een rare regel
12345
```
**Verwacht**: "Geen geldige adressen gevonden"

---

### Test 4: Real-time Progress

1. **Maak een groter bestand** (50+ adressen):
   ```bash
   # Linux/Mac
   for i in {1..50}; do echo "Dam $i, AMSTERDAM"; done > big_test.txt
   ```

2. **Upload het bestand**

3. **Observeer:**
   - Progress bar update (elke seconde)
   - Counter update: "Verwerkt: 1/50", "2/50", etc.
   - Percentage groei

4. **Dit test:**
   - Server-Sent Events werken
   - Real-time updates
   - Thread processing

---

### Test 5: Multiple Jobs (Concurrent)

Test of meerdere uploads tegelijk werken:

1. **Open 2 browser tabs** naar http://localhost:5000

2. **Start in tab 1**: Upload `test1.txt`

3. **Start in tab 2**: Upload `test2.txt` (zonder te wachten)

4. **Beide jobs** zouden parallel moeten verwerken

5. **Check** dat beide voltooien met correcte resultaten

---

## 🔍 API Testing (Advanced)

Test de API endpoints direct met curl of Python:

### Test API Endpoints

```bash
# 1. Server health
curl http://localhost:5000/api/stats

# 2. Manual input
curl -X POST http://localhost:5000/api/process-text \
  -H "Content-Type: application/json" \
  -d '{"addresses": "Dam 1, AMSTERDAM\nBarrierweg 1, EINDHOVEN"}'

# Response: {"job_id": "some-uuid"}

# 3. Check status (gebruik job_id van boven)
curl http://localhost:5000/api/status/YOUR-JOB-ID

# 4. Stream progress (Server-Sent Events)
curl -N http://localhost:5000/api/stream/YOUR-JOB-ID

# 5. Download resultaten
curl http://localhost:5000/api/download/YOUR-JOB-ID/csv -o result.csv
```

### Test met Python Script

```bash
# Run de test suite
python test_web.py
```

Dit test automatisch:
- Server connectie
- File upload
- Manual input
- Status tracking
- Downloads

---

## 📱 Mobile Testing

Test de responsive design:

### Desktop Browser
1. Open http://localhost:5000
2. Resize browser venster
3. Check dat layout aanpast

### Chrome DevTools
1. Open DevTools (F12)
2. Click device toolbar (Ctrl+Shift+M)
3. Test verschillende apparaten:
   - iPhone SE (375px)
   - iPad (768px)
   - Desktop (1200px+)

**Verwacht:**
- Upload zone kleiner op mobile
- Buttons stacken verticaal
- Text leesbaar
- Tabs werken

---

## 🐛 Troubleshooting

### Server start niet

**Probleem:** Port 5000 al in gebruik
```bash
# Linux/Mac: Kill process op port 5000
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <pid> /F
```

**Probleem:** Flask niet geïnstalleerd
```bash
pip install -r requirements.txt
```

### Upload werkt niet

**Check 1:** Max file size (16MB)
```bash
ls -lh test_adressen.txt  # Should be < 16MB
```

**Check 2:** Bestand encoding
```bash
file test_adressen.txt  # Should be: UTF-8 text
```

**Fix encoding:**
```bash
iconv -f ISO-8859-1 -t UTF-8 input.txt > output.txt
```

### Progress blijft hangen

**Symptoom:** Progress blijft op 0% staan

**Mogelijke oorzaken:**
1. PDOK API niet bereikbaar (check internet)
2. Proxy blokkering
3. SSL certificaat issue

**Debug:**
```python
# In app.py, voeg toe:
import logging
logging.basicConfig(level=logging.DEBUG)
```

Dan zie je in terminal wat er gebeurt.

### Postcodes zijn allemaal "Error: ProxyError"

**Oorzaak:** Je zit achter een corporate proxy

**Fix:** Set proxy environment variables
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
python app.py
```

### Browser toont "ERR_CONNECTION_REFUSED"

**Oorzaak:** Server draait niet

**Fix:**
```bash
# Check of server draait
ps aux | grep "python app.py"

# Of test met curl
curl http://localhost:5000
```

---

## ✅ Checklist

Gebruik deze checklist om te verifiëren dat alles werkt:

### Basic Functionality
- [ ] Server start zonder errors
- [ ] Home page laadt in browser
- [ ] Beide tabs zijn zichtbaar
- [ ] Upload zone accepteert .txt bestanden
- [ ] Drag & drop werkt
- [ ] Manual input textarea werkt
- [ ] "Zoek Postcodes" button werkt

### Processing
- [ ] Progress bar update
- [ ] Counter toont X/Y adressen
- [ ] Processing voltooit zonder crash
- [ ] Resultaten worden getoond

### Results
- [ ] Statistieken dashboard toont cijfers
- [ ] Preview toont eerste resultaten
- [ ] Postcodes hebben correcte kleuren
- [ ] CSV download werkt
- [ ] TXT download werkt
- [ ] Downloaded files zijn correct

### Error Handling
- [ ] Lege input toont error
- [ ] Verkeerd bestandstype toont error
- [ ] Ongeldige adressen worden gehandled
- [ ] Network errors worden gehandled

### UI/UX
- [ ] Design ziet er goed uit
- [ ] Gradient kleuren werken
- [ ] Buttons hebben hover effect
- [ ] Responsive op mobile
- [ ] Tabs switchen soepel

### Advanced
- [ ] Multiple concurrent jobs werken
- [ ] Server-Sent Events werken
- [ ] API endpoints reageren correct
- [ ] No memory leaks (bij 100+ adressen)

---

## 📊 Expected Performance

Bij normale werking:

- **Upload tijd**: < 1 seconde
- **Processing**: ~0.3 seconden per adres
- **Total voor 10 adressen**: ~3-5 seconden
- **Memory usage**: < 100MB
- **CPU usage**: < 20% per job

---

## 🎯 Success Criteria

De web interface werkt correct als:

1. ✅ Server start zonder errors
2. ✅ UI is toegankelijk in browser
3. ✅ Beide input methodes werken
4. ✅ Progress updates real-time
5. ✅ Resultaten zijn accuraat
6. ✅ Downloads werken
7. ✅ Errors worden netjes getoond
8. ✅ Multiple jobs werken parallel
9. ✅ Responsive op alle devices

---

## 📝 Test Data

Gebruik deze Nederlandse adressen voor testen:

```
Dam 1, AMSTERDAM
Kalverstraat 92, AMSTERDAM
Coolsingel 40, ROTTERDAM
Lijnbaan 150, ROTTERDAM
Neude 11, UTRECHT
Oudegracht 245, UTRECHT
Barrierweg 1, EINDHOVEN
Grote Markt 1, GRONINGEN
Waagplein 1, ALKMAAR
Markt 1, DELFT
```

**Verwachte postcodes:**
- Dam 1, AMSTERDAM → 1012JS
- Barrierweg 1, EINDHOVEN → 5629CD
- Coolsingel 40, ROTTERDAM → 3012AA

---

## 💡 Tips

1. **Use Chrome/Firefox** - Beste developer tools
2. **Open Console** (F12) - Zie JavaScript errors
3. **Network tab** - Zie API calls
4. **Incognito mode** - Test zonder cache
5. **Small files eerst** - Test met 3-5 adressen
6. **Then scale up** - Test met 50-100 adressen

---

**Happy Testing! 🎉**

Als alles werkt, heb je een volledig functionele web applicatie voor Nederlandse postcode lookup!
