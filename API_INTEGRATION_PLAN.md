# 🚗 Plan Integrare API-uri Legale Piață Auto

## 📋 Opțiuni API Legale Disponibile

### 1. **Mobile.de API** (Germania - Cel mai mare marketplace auto din Europa)
- **Link:** https://services.mobile.de/manual/
- **Acoperire:** Germania, Austria, Italia, Belgia, Olanda, Spania
- **Tip Access:** API comercial, necesită aplicație pentru access token
- **Cost:** Gratuită pentru dezvoltatori individuali (limited), comercială pentru volume mari
- **Date disponibile:**
  - Listings complete cu prețuri în EUR
  - Specificații detaliate (dotări, culoare, transmisie, etc.)
  - Istoric prețuri
  - Imagini
- **Avantaje:** Foarte completă, date actualizate zilnic
- **Dezavantaje:** Necesită aprobare, poate dura câteva zile

### 2. **AutoScout24 API** (Europa - Multi-țări)
- **Link:** https://www.autoscout24.com/
- **Acoperire:** Germania, Austria, Italia, Olanda, Belgia, Spania, Franța
- **Tip Access:** Partner API (necesită cont comercial)
- **Cost:** Pe bază de contract
- **Date disponibile:**
  - Listings complete
  - Specificații tehnice detaliate
  - Prețuri în EUR
- **Avantaje:** Bază largă de date
- **Dezavantaje:** Access mai restrictiv, de obicei pentru dealeri

### 3. **NHTSA Vehicle API** (US - Date Tehnice)
- **Link:** https://vpic.nhtsa.dot.gov/api/
- **Acoperire:** Specificații tehnice globale
- **Tip Access:** Complet PUBLIC și GRATUIT
- **Cost:** FREE, fără limită
- **Date disponibile:**
  - VIN decoding
  - Specificații complete vehicle (make, model, year, engine, etc.)
  - Equipment standard
  - Safety ratings
- **Avantaje:** 100% gratuit, fără autorizare necesară
- **Dezavantaje:** Nu conține prețuri de piață, doar date tehnice

### 4. **Edmunds API** (US - Pricing & Specs)
- **Link:** https://developer.edmunds.com/
- **Acoperire:** Primarily US, dar multe vehicule europene
- **Tip Access:** API key gratuit pentru dezvoltatori
- **Cost:** Tier gratuit disponibil
- **Date disponibile:**
  - TMV (True Market Value) pricing
  - Detailed specifications
  - Equipment lists
  - Historical pricing data
- **Avantaje:** Date de pricing bune, API bine documentat
- **Dezavantaje:** Focus pe piața US

### 5. **Carvago API** (Europa Centrală și de Est)
- **Link:** https://www.carvago.com/
- **Acoperire:** România, Cehia, Slovacia, Polonia, Ungaria, Austria, Germania
- **Tip Access:** Marketplace cu API potențial (necesită contact)
- **Cost:** Unknown - necesită negociere
- **Date disponibile:**
  - Listings din Europa de Est
  - Prețuri în EUR și monede locale
  - Inspecții certificate
- **Avantaje:** Acoperire bună pentru România și țările vecine
- **Dezavantaje:** API nu este public documentat

### 6. **DAT (Deutsche Automobil Treuhand)** (Germania - Date Oficiale)
- **Link:** https://www.dat.de/
- **Acoperire:** Germania, date oficiale valori reziduale
- **Tip Access:** API comercial
- **Cost:** Subscription based
- **Date disponibile:**
  - Valori reziduale oficiale
  - Specificații complete
  - Echipament standard și opțional
  - Depreciation rates
- **Avantaje:** Date oficiale, foarte precise
- **Dezavantaje:** Cost ridicat, acces comercial

### 7. **CarQuery API** (Global - Specificații)
- **Link:** http://www.carqueryapi.com/
- **Acoperire:** Global database
- **Tip Access:** PUBLIC și GRATUIT
- **Cost:** FREE
- **Date disponibile:**
  - Make, model, trim
  - Year ranges
  - Engine specifications
  - Basic equipment
- **Avantaje:** Gratuit, simplu de folosit
- **Dezavantaje:** Nu are prețuri, doar specs

## 🎯 Recomandare: Arhitectură Multi-API Hibridă

### Soluția Optimă:
Combinăm mai multe API-uri pentru date complete și legale:

```
┌─────────────────────────────────────────────────┐
│         CarAnalyzer Backend                      │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │   API Aggregator Service (NOU)           │  │
│  └──────────────────────────────────────────┘  │
│            │            │            │          │
│            ▼            ▼            ▼          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Mobile.de│  │  NHTSA   │  │CarQuery  │    │
│  │   API    │  │   API    │  │   API    │    │
│  │(Pricing) │  │  (Specs) │  │  (Specs) │    │
│  └──────────┘  └──────────┘  └──────────┘    │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │   Price Adjustment Engine                 │  │
│  │   - EUR → RON conversion                  │  │
│  │   - Regional coefficient (0.75-0.85)      │  │
│  │   - Import tax adjustment                 │  │
│  │   - Local market trends                   │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │   PostgreSQL Database                     │  │
│  │   - Cached API responses                  │  │
│  │   - Historical pricing data               │  │
│  │   - Equipment mappings                    │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 📊 Strategy: Combinație APIs

### Step 1: Date Tehnice (100% Gratuit)
**API:** NHTSA + CarQuery
- Obținem specificații complete pentru orice vehicul
- Make, model, year, engine, transmission, standard equipment
- Fără cost, fără limită de requests

### Step 2: Pricing Europa (Necesită aplicație)
**API:** Mobile.de
- Aplicăm pentru API access (gratuit pentru dezvoltatori individuali)
- Obținem prețuri reale din Germania/Europa
- Cache rezultatele pentru a reduce API calls

### Step 3: Price Adjustment pentru România
**Formula:**
```python
pret_romania = pret_europa_eur * eur_ron_rate * regional_coefficient

unde:
- eur_ron_rate = 4.97 (actualizat zilnic via API BCE)
- regional_coefficient = 0.75-0.85 (bazat pe:
    * Vechime vehicul
    * Km parcurși
    * Dotări
    * Piața locală)
```

### Step 4: Fallback la Date Locale
Dacă API-urile europene nu returnează date:
- Folosim scrapers existenți (Autovit.ro, OLX.ro) ca fallback
- Cu rate limiting agresiv (1 request/10s)
- Doar pentru vehicule specifice cerute de user

## 🔧 Implementare Tehnică

### 1. Structură Nouă Backend
```
app/
├── integrations/          # NOU
│   ├── __init__.py
│   ├── mobile_de.py      # Mobile.de API client
│   ├── nhtsa.py          # NHTSA API client
│   ├── carquery.py       # CarQuery API client
│   ├── ecb_rates.py      # European Central Bank exchange rates
│   └── aggregator.py     # Combină toate API-urile
├── services/             # NOU
│   ├── price_adjuster.py # Ajustare EUR → RON
│   └── cache_manager.py  # Redis/PostgreSQL cache
└── routers/
    └── market_data.py    # NOU endpoint /api/market-data
```

### 2. Endpoints Noi
```python
POST /api/market-data/search
{
  "make": "Volkswagen",
  "model": "Golf",
  "year": 2018,
  "mileage": 85000,
  "fuel_type": "diesel"
}

Response:
{
  "european_listings": [
    {
      "source": "mobile_de",
      "price_eur": 14500,
      "price_ron": 72065,  # Ajustat pentru România
      "location": "Germany",
      "equipment": ["leather", "navigation", "parking_sensors"],
      "mileage": 87000,
      "year": 2018
    }
  ],
  "technical_specs": {
    "source": "nhtsa",
    "engine": "2.0 TDI",
    "horsepower": 150,
    "transmission": "manual",
    "standard_equipment": [...]
  },
  "market_analysis": {
    "avg_price_eur": 14200,
    "avg_price_ron": 70574,
    "price_range_ron": {
      "min": 65000,
      "max": 78000
    },
    "sample_size": 45
  }
}
```

### 3. Cache Strategy
```python
# Redis sau PostgreSQL pentru cache
cache_key = f"{make}:{model}:{year}:{mileage}"
cache_ttl = 24 * 3600  # 24 ore

# Reduce API calls, salvează costs
```

## 💰 Cost Estimate

| API            | Cost/Month    | Usage Limit      | Status           |
|----------------|---------------|------------------|------------------|
| NHTSA          | FREE          | Unlimited        | ✅ Ready to use  |
| CarQuery       | FREE          | Unlimited        | ✅ Ready to use  |
| Mobile.de      | FREE (basic)  | ~1000 req/day    | 📝 Needs signup  |
| ECB Rates      | FREE          | Unlimited        | ✅ Ready to use  |
| **TOTAL**      | **0 EUR**     | -                | -                |

## 🚀 Implementation Steps

### Phase 1: Setup API Clients (1-2 zile)
1. Signup pentru Mobile.de API (dacă disponibil) sau găsim alternativă
2. Implementează NHTSA client (immediate, public API)
3. Implementează CarQuery client (immediate, public API)
4. Implementează ECB rates fetcher pentru EUR/RON

### Phase 2: Price Adjustment Engine (1 zi)
1. Formula de conversie EUR → RON
2. Regional coefficients bazați pe statistici
3. Testing cu date reale

### Phase 3: Integration în Backend (2-3 zile)
1. Creează API aggregator service
2. Adaugă cache layer (PostgreSQL sau Redis)
3. Create noul endpoint `/api/market-data`
4. Unit tests

### Phase 4: Frontend Integration (2 zile)
1. Adaugă tab "Piață Reală"
2. Display listings din Europa
3. Show prețuri ajustate pentru România
4. Comparație cu analiza locală

### Phase 5: Testing & Optimization (1-2 zile)
1. Load testing
2. Cache optimization
3. Error handling pentru API failures
4. Fallback mechanisms

## ⚖️ Legal Compliance

### Terms of Service Check:
- ✅ NHTSA: Public domain, no restrictions
- ✅ CarQuery: Free for any use
- ✅ ECB: Free for any use
- ⚠️ Mobile.de: Trebuie să respectăm TOS-ul lor (rate limits, attribution)

### Attribution Required:
```javascript
// Footer in frontend
"Prețuri piață europeană furnizate de Mobile.de"
"Date tehnice de la NHTSA Vehicle Database"
```

## 🔄 Alternative Fallback

Dacă Mobile.de nu ne aprobă API access:
1. **Plan B:** Folosim scraping etic cu rate limiting foarte conservativ
   - 1 request per 30 secunde
   - User-Agent corect
   - robots.txt compliance
   - Cache agresiv (7 zile)

2. **Plan C:** Parteneriat cu Carvago sau altă platformă din România/Europa de Est
   - Contact direct pentru API access
   - Potential cost mic

3. **Plan D:** Crowdsourcing
   - Users pot contribui cu prețuri văzute pe piață
   - Moderare și validare
   - Build propriul nostru database over time

## 📝 Next Actions

1. **IMEDIAT:** Implementăm NHTSA + CarQuery (100% gratuit, public)
2. **Săptămâna 1:** Aplicăm pentru Mobile.de API access
3. **Săptămâna 1:** Implementăm price adjustment engine
4. **Săptămâna 2:** Full integration în frontend

Vrei să încep cu implementarea? Pot începe cu API-urile gratuite (NHTSA + CarQuery) chiar acum!
