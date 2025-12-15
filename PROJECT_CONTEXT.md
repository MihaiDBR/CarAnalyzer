\# 🚗 Car Price Analyzer - Context Proiect



\## 📋 Overview

Full-stack aplicație pentru analiza prețurilor mașinilor second-hand din România.

\- \*\*Backend:\*\* FastAPI + PostgreSQL + Selenium (scraping real)

\- \*\*Frontend:\*\* React + Tailwind CSS + Axios

\- \*\*Database:\*\* PostgreSQL 18

\- \*\*Python:\*\* 3.11.9

\- \*\*Node:\*\* v18+



---



\## 🏗️ Arhitectură



\### Backend (D:\\Caranalyzer\\car-price-analyzer-backend)

```
app/

├── main.py                    # FastAPI app + CORS + lifespan

├── database.py                # PostgreSQL config + tables (SQLAlchemy 1.4.51)

├── schemas.py                 # Pydantic models pentru validare

├── routers/

│   ├── analysis.py            # POST /api/analyze - calcul preț

│   ├── scraping.py            # POST /api/scrape - scraping Autovit/OLX

│   └── listings.py            # GET /api/listings - anunțuri din DB

├── scrapers/

│   ├── autovit.py             # Selenium scraper pentru Autovit.ro

│   └── olx.py                 # aiohttp scraper pentru OLX.ro

└── analysis/

&nbsp;   └── price\_analyzer.py      # Motor calcul preț (FĂRĂ sklearn)

```



\### Frontend (D:\\Caranalyzer\\car-price-analyzer-frontend)

```

src/

├── App.js                     # Componentă principală

├── services/

│   └── api.js                 # Axios wrapper pentru backend

└── components/                # (viitoare componente)

```



---



\## 🗄️ Database Schema (PostgreSQL)



\*\*Tabele:\*\*

1\. `car\_models` - Mărci/modele cu depreciere (20 entries)

2\. `dotari` - Echipamente cu valori (20 entries)

3\. `listings` - Anunțuri scraped (populate manual cu INSERT)

4\. `price\_history` - Istoric modificări preț

5\. `saved\_analyses` - Analize salvate



\*\*Connection String:\*\*

```

postgresql://postgres:neneidodo@localhost:5432/car\_analyzer

```



---



\## ✅ Ce FUNCȚIONEAZĂ acum:



\### Backend:

\- ✅ FastAPI server pe http://localhost:8000

\- ✅ Swagger UI: http://localhost:8000/docs

\- ✅ Database conectat + populate cu date test

\- ✅ Endpoint `/api/analyze` - calculează 4 strategii pricing:

&nbsp; - Preț rapid (91% din optim, 1-2 săpt)

&nbsp; - Preț optim (100%, 3-5 săpt)

&nbsp; - Preț negociere (105%, 5-8 săpt)

&nbsp; - Preț premium (112%, 2-4 luni)

\- ✅ Calcul depreciere bazat pe: an, km, dotări

\- ✅ Endpoint `/api/equipment` - returnează dotări disponibile

\- ✅ Endpoint `/api/brands` - returnează mărci din listings



\### Frontend:

\- ✅ React app pe http://localhost:3000

\- ✅ Formular funcțional: marcă, model, an, km, combustibil, dotări

\- ✅ 4 carduri cu strategii pricing (culori diferite)

\- ✅ Export rezultate în JSON

\- ✅ Comunicare cu backend prin Axios

\- ✅ Design responsive cu Tailwind CSS



---



\## ⚠️ Limitări Actuale:



\### Backend:

\- ❌ Scraping real nu e testat (scrapers existenți dar nefolosiți)

\- ❌ Nu am sklearn (folosim numpy pentru statistici simple)

\- ❌ Listings table populat MANUAL (nu automat prin scraping)

\- ❌ Nu avem autentificare/JWT

\- ❌ Nu avem rate limiting

\- ❌ ChromeDriver configurat pe "auto" (webdriver-manager)



\### Frontend:

\- ❌ Nu avem tab "Comparativ Piață" (doar Analiză)

\- ❌ Nu avem tab "Anunțuri Similare"

\- ❌ Nu avem grafice (recharts instalat dar nefolosit)

\- ❌ Nu avem sistem de alerte

\- ❌ Nu avem istoric prețuri



\### Database:

\- ❌ Listings table aproape goală (5-6 test entries)

\- ❌ Nu avem date reale din piață

\- ❌ price\_history nefolosit

\- ❌ saved\_analyses nefolosit



---



\## 🎯 Următorii Pași Prioritari:



\### Priority 1 - Scraping Real:

1\. Testează `AutovitScraper` + `OLXScraper`

2\. Populează `listings` automat din frontend

3\. Adaugă progress indicator pentru scraping

4\. Handle erori de scraping (rate limits, timeouts)



\### Priority 2 - Frontend Features:

1\. Tab "Comparativ Piață" cu grafice

2\. Tab "Anunțuri Similare" cu listă

3\. Filtre avansate (preț min/max, locație)

4\. Sistem de alerte pentru prețuri bune



\### Priority 3 - Data \& ML:

1\. Populează car\_models cu toate mașinile populare

2\. Adaugă mai multe dotări în dotari table

3\. (Opțional) Integrează sklearn pentru ML real

4\. Tracking istoric prețuri în time



\### Priority 4 - Production Ready:

1\. Docker Compose pentru deploy

2\. JWT authentication

3\. Rate limiting

4\. Logging + monitoring

5\. Error handling mai robust



---



\## 🔧 Dependențe Cheie:



\### Backend (requirements.txt):

```

fastapi==0.104.1

uvicorn\[standard]==0.24.0

sqlalchemy==1.4.51          # Versiune specifică pentru databases

databases\[postgresql]==0.8.0

psycopg2-binary==2.9.9

selenium==4.15.2

beautifulsoup4==4.12.2

numpy==1.24.4

pandas==2.0.3

```



\### Frontend (package.json):

```

axios, lucide-react, recharts, tailwindcss

```



---



\## 🐛 Known Issues:



1\. \*\*Scraping poate da timeout\*\* - site-urile au rate limits

2\. \*\*sklearn nu e instalat\*\* - Python 3.13 compatibility issues, downgrade la 3.11

3\. \*\*Listings table goală\*\* - trebuie populate manual sau prin scraping

4\. \*\*CORS trebuie configurat\*\* în .env backend cu frontend URL



---



\## 💡 Tips pentru Dezvoltare:



\### Start servers:

```powershell

\# Backend

cd car-price-analyzer-backend

.venv\\Scripts\\Activate.ps1

uvicorn app.main:app --reload



\# Frontend

cd car-price-analyzer-frontend

npm start

```



\### Database access:

```powershell

psql -U postgres -d car\_analyzer

```



\### Test API:

\- Swagger UI: http://localhost:8000/docs

\- Health check: http://localhost:8000/health



\### Frontend debugging:

\- F12 → Network tab pentru API calls

\- F12 → Console pentru erori JavaScript



---



\## 📊 Database Queries Utile:

```sql

-- Verifică număr anunțuri

SELECT COUNT(\*) FROM listings WHERE este\_activ = true;



-- Anunțuri pe marcă

SELECT marca, COUNT(\*) FROM listings GROUP BY marca;



-- Șterge date test

DELETE FROM listings WHERE source = 'test';



-- Adaugă anunț test

INSERT INTO listings (source, url, marca, model, an, km, pret, combustibil, locatie, dotari, imagini, descriere, data\_publicare, data\_scraping, este\_activ)

VALUES ('test', 'http://test.ro', 'Volkswagen', 'Golf 7', 2018, 85000, 12500, 'diesel', 'bucuresti', '\["piele"]', '\[]', 'Test', NOW(), NOW(), true);

```



---



\## 🎨 Design Patterns Folosite:



\- \*\*Repository Pattern\*\* - database.py separat de logica business

\- \*\*Router Pattern\*\* - FastAPI routers pentru organizare

\- \*\*Service Layer\*\* - api.js în frontend pentru centralizare API calls

\- \*\*Component-Based\*\* - React components (viitor)



---



\## 🚀 Cum să continui cu AI Assistant:



Când lucrezi cu Claude/AI în VS Code, dă-i acest prompt:

```

"Citește PROJECT\_CONTEXT.md pentru context complet. 

Vreau să lucrăm la \[FEATURE/BUG]. 

Ține cont de limitările actuale și arhitectură existentă."

```



---



\*\*Ultima actualizare:\*\* 15 Decembrie 2024

\*\*Status:\*\* ✅ MVP funcțional, backend + frontend comunică, ready pentru features noi

```



Salvează.



---



\## 🎯 \*\*Acum când lucrezi în VS Code:\*\*



1\. Deschide VS Code în `D:\\Caranalyzer`

2\. Apasă \*\*Ctrl+Shift+P\*\* → `Tasks: Run Task` → \*\*🚀 Start ALL\*\*

3\. Când vrei ajutor de la AI, dă-i prompt-ul:

```

Citește D:\\Caranalyzer\\PROJECT\_CONTEXT.md pentru context complet despre proiectul nostru.



Vreau să \[DESCRIE CE VREI SĂ FACI].



Ține cont de:

\- Arhitectura existentă

\- Limitările actuale

\- Dependențele instalate

