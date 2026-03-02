# 📊 Vercel Address Limits - Configuration Guide

## 🎯 Current Limits

| Vercel Tier | Timeout | Max Addresses | Cost |
|-------------|---------|---------------|------|
| **Free** | 10s | 50 adressen | $0/maand |
| **Pro** | 60s | 200 adressen | $20/maand |
| **Enterprise** | 900s | 3000+ adressen | Custom |

---

## 🧮 How Limits Are Calculated

### Time per Address:
```
API Request:  ~0.3-0.5s
API Delay:    0.15s (rate limiting)
Total:        ~0.5s per adres
```

### Free Tier (10s timeout):
```
10 seconds ÷ 0.5s = ~20 adressen
With optimizations: 50 adressen (safe margin)
```

### Pro Tier (60s timeout):
```
60 seconds ÷ 0.5s = ~120 adressen
With optimizations: 200 adressen (safe margin)
```

---

## 🚀 Upgrade to 200 Addresses

### Option 1: Vercel Pro (Recommended)

**Benefits:**
- 60 second function timeout
- 200 addresses per request
- Better performance
- Priority support

**Cost:** $20/month per team member

**Steps:**
1. Go to: https://vercel.com/dashboard
2. Click "Upgrade to Pro"
3. Complete payment
4. **Update code** (see below)

**Code Changes:**
```python
# In api/index.py, change line ~22:
max_allowed = MAX_ADDRESSES_PRO  # Was: MAX_ADDRESSES_FREE
```

**Deploy:**
```bash
git add api/index.py
git commit -m "Increase limit to 200 addresses for Vercel Pro"
git push
```

Vercel auto-deploys and you're done!

---

### Option 2: Optimize Further (Free Tier)

You can squeeze more addresses by reducing the API delay:

**⚠️ Warning:** Risk of rate limiting from PDOK API

```python
# In api/index.py:
API_DELAY_SECONDS = 0.1  # Risky! Was 0.15
# This allows ~80 addresses in 10s
```

**Not recommended** - may trigger PDOK rate limits.

---

### Option 3: Use CLI for Large Batches (Free)

For 200+ addresses, use the local CLI:

```bash
# No limits, no timeouts!
python postcode_lookup_improved.py adressen.txt
```

**Benefits:**
- Unlimited addresses
- No timeout
- Faster (parallel possible)
- No cost

**Drawback:** Requires local setup

---

## 🔧 Configuration Guide

### For Vercel Free (50 addresses - Current Default)

No changes needed! Already optimized.

```python
# api/index.py
API_DELAY_SECONDS = 0.15
max_allowed = MAX_ADDRESSES_FREE  # 50 adressen
```

---

### For Vercel Pro (200 addresses)

**Step 1:** Upgrade to Vercel Pro

**Step 2:** Update code:
```python
# api/index.py - Find line ~22
MAX_ADDRESSES_FREE = 50
MAX_ADDRESSES_PRO = 200

# Find line ~170 (in process function)
max_allowed = MAX_ADDRESSES_PRO  # Change this!
```

**Step 3:** Update frontend warning:
```html
<!-- templates/index_vercel.html - line ~93 -->
⚠️ <strong>Serverless versie:</strong> Max 200 adressen per keer.
```

**Step 4:** Commit & deploy:
```bash
git add api/index.py templates/index_vercel.html
git commit -m "Upgrade to 200 address limit (Vercel Pro)"
git push
```

---

## 📈 Performance Tips

### 1. Optimize API Delay

Current: 0.15s (400 req/min) ← Safe
Minimum: 0.1s (600 req/min) ← Risky

**Change:**
```python
API_DELAY_SECONDS = 0.1  # More addresses, more risk
```

### 2. Parallel Processing (Advanced)

Use `asyncio` for parallel requests:

```python
import asyncio
import aiohttp

async def get_postcode_async(address):
    async with aiohttp.ClientSession() as session:
        async with session.get(PDOK_BASE_URL, params=params) as resp:
            # Process response
            ...

# Process 10 at a time
results = await asyncio.gather(*[get_postcode_async(addr) for addr in batch])
```

**Benefit:** 3-5x faster
**Risk:** Higher load on PDOK API

---

## 🎛️ Environment Variable Config (Advanced)

Make it configurable without code changes:

```python
# api/index.py
import os

MAX_ADDRESSES = int(os.environ.get('MAX_ADDRESSES', '50'))

if len(addresses) > MAX_ADDRESSES:
    return jsonify({'error': f'Maximum {MAX_ADDRESSES} adressen'}), 400
```

**Vercel Dashboard:**
1. Project Settings
2. Environment Variables
3. Add: `MAX_ADDRESSES = 200`
4. Redeploy

Now you can change the limit without code changes!

---

## 📊 Comparison Table

| Method | Max Addresses | Time | Cost | Setup |
|--------|---------------|------|------|-------|
| **Web Free** | 50 | ~25s | $0 | ✅ Easy |
| **Web Pro** | 200 | ~100s | $20/mo | ✅ Easy |
| **Web Optimized** | 80 | ~10s | $0 | ⚠️ Risky |
| **Web Async** | 200 | ~30s | $20/mo | 🔧 Complex |
| **CLI Local** | ∞ Unlimited | Varies | $0 | 🔧 Setup |

---

## 🤔 Which Should You Choose?

### Stay on Free (50 addresses)
**If:**
- Budget conscious
- Occasional use
- 50 addresses is enough

**Recommendation:** ✅ Current setup is perfect

---

### Upgrade to Pro (200 addresses)
**If:**
- Regular use
- Need more capacity
- Want better performance

**Recommendation:** ✅ Worth $20/month if daily use

---

### Use CLI (Unlimited)
**If:**
- Batch processing (500+ addresses)
- One-time large imports
- Technical user

**Recommendation:** ✅ Best for bulk operations

---

## 💰 Cost Calculation

### Free Tier:
- 100 GB-Hours/month included
- 50 addresses × 25s = 0.35 GB-Hours
- **~285 batches/month FREE** (14,250 addresses)

### Pro Tier ($20/month):
- 1,000 GB-Hours/month included
- 200 addresses × 100s = 5.5 GB-Hours
- **~180 batches/month** (36,000 addresses)
- Then $0.12 per extra GB-Hour

**TL;DR:** Unless you process 15,000+ addresses/month, stay on free!

---

## 🔄 Quick Switch Guide

### From 50 → 200 addresses:

```bash
# 1. Upgrade Vercel to Pro
# Visit: https://vercel.com/dashboard

# 2. Update code
sed -i 's/MAX_ADDRESSES_FREE/MAX_ADDRESSES_PRO/g' api/index.py
sed -i 's/50 adressen/200 adressen/g' templates/index_vercel.html

# 3. Deploy
git add .
git commit -m "Upgrade to 200 address limit (Vercel Pro)"
git push
```

Done in 2 minutes! 🚀

---

## 🐛 Troubleshooting

### "FUNCTION_INVOCATION_TIMEOUT"

**Cause:** Processing took >10s (Free) or >60s (Pro)

**Fix:**
1. Reduce number of addresses
2. Or upgrade to Pro
3. Or check if PDOK API is slow

---

### "Rate limit" errors from PDOK

**Cause:** API_DELAY_SECONDS too low

**Fix:**
```python
API_DELAY_SECONDS = 0.2  # Increase from 0.15
```

---

### Processing is slow

**Check:**
- PDOK API response time
- Your internet connection
- Vercel region (closer = faster)

**Fix:** Can't do much about PDOK API speed

---

## ✅ Recommended Setup

**For 99% of users:**
```
Vercel: Free
Limit: 50 addresses
Cost: $0
```

**For power users:**
```
Vercel: Pro
Limit: 200 addresses
Cost: $20/month
```

**For bulk processing:**
```
CLI: Local
Limit: Unlimited
Cost: $0
```

---

## 📝 Summary

**Current:** 50 addresses (Free tier) ✅
**Option 1:** 200 addresses (Pro tier - $20/mo)
**Option 2:** CLI for unlimited (Free)

**My recommendation:** Keep 50 for now. Upgrade to Pro only if you regularly hit the limit.

---

**Questions?** Check VERCEL_DEPLOY.md for more details!
