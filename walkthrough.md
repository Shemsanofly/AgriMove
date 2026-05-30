# AgriMove-AI — Walkthrough Guide
## Tanzania Smallholder Farmer Features

---

## 🚀 Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python app.py

# 3. Seed demo data (open in browser or curl)
GET http://localhost:5000/setup-demo
```

The app runs at **http://localhost:5000**

---

## 🌍 Feature Walkthrough

---

### Feature 1 — Bei za Soko (Market Price Board)
**Route:** `/market-prices` | **API:** `/api/prices`

Shows live crop prices per kg in TZS across 5 Tanzanian markets.

| Crop (Swahili) | Best Market | Price/kg TZS |
|---------------|-------------|-------------|
| Mahindi (Maize) | Kariakoo, Dar | 950 TZS |
| Mpunga (Rice) | Kariakoo, Dar | 2,000 TZS |
| Muhogo (Cassava) | Kariakoo, Dar | 550 TZS |
| Nyanya (Tomatoes) | Kariakoo, Dar | 1,500 TZS |
| Vitunguu (Onions) | Kariakoo, Dar | 1,800 TZS |
| Kahawa (Coffee) | Arusha Auction | 8,500 TZS |
| Korosho (Cashews) | Kariakoo, Dar | 6,000 TZS |

**How to use:**
1. Go to `/market-prices`
2. Use filter buttons to select a crop
3. Green ↑ = price rising, Red ↓ = falling, Grey → = stable
4. Click **API Data (JSON)** to see raw JSON feed

**API:**
```
GET /api/prices              → All prices
GET /api/prices/maize        → Maize prices only
GET /api/prices/kahawa       → Coffee prices (Swahili name works too)
```

---

### Feature 2 — Shamba Connect (Load Pooling)
**Route:** `/transport` | **API:** `/api/transport/*`

Farmers share truck space to reduce per-bag transport costs.

**How to use:**
1. Go to `/transport`
2. Fill in: your village, ward, district, crop, number of bags, pickup date
3. Click **Tafuta Usafiri** (Find Transport)
4. See matching open truck pools — shows cost per bag in TZS
5. Click **Jiunge** (Join) to reserve slots

**API:**
```
POST /api/transport/request          → Submit a new load request
GET  /api/transport/pool/<ward>      → Find pools near a ward
POST /api/transport/join/<pool_id>   → Join a pool (decrements available slots)
```

---

### Feature 3 — Malango Salama (Safe M-Pesa Payment)
**Route:** `/payments` | **API:** `/api/payment/*`

Escrow-based payment system: buyer pays into escrow, funds released only when farmer confirms delivery.

**How to use:**
1. Go to `/payments`
2. Enter: buyer name/phone, farmer name/phone, crop, quantity (kg), price (TZS)
3. Click **Anza Malipo** (Start Payment)
4. System generates M-Pesa reference (e.g., `MP-2024-001`)
5. Status tracker shows: Pending → Confirmed → Released
6. Click **Thibithisha Malipo** (Confirm Payment) to release funds

**Statuses:**
- `pending` — Escrow created, awaiting M-Pesa confirmation
- `confirmed` — M-Pesa STK push confirmed by buyer
- `released` — Funds released to farmer after delivery

**API:**
```
POST /api/payment/initiate          → Create escrow transaction
POST /api/payment/confirm/<id>      → Release funds to farmer
GET  /api/payment/status/<id>       → Check transaction status
```

---

### Feature 4 — Hifadhi Yangu (Storage Finder)
**Route:** `/storage` | **API:** `/api/storage/*`

Find certified warehouses, silos, and cold stores near you.

**How to use:**
1. Go to `/storage`
2. Filter by region or sort by GPS distance
3. See capacity bars (available / total tons)
4. **WRS badge** = facility accepts Warehouse Receipt System
5. Click phone number to call directly

**Sample facilities:**
| Name | Region | Type | TZS/bag/month |
|------|--------|------|--------------|
| Kariakoo Cold Store | Dar es Salaam | Cold Storage | 3,500 |
| Arusha Grain Depot | Arusha | Warehouse | 2,800 |
| Mbeya Highland Silo | Mbeya | Silo | 1,800 |

**API:**
```
GET /api/storage                     → All facilities
GET /api/storage/<region>            → Filter by region (e.g., /api/storage/Arusha)
GET /api/storage/nearest?lat=&lng=   → Sort by GPS distance
```

---

### Feature 5 — USSD *384# Simulator
**Route:** `/ussd-simulator`

Interactive simulation of what farmers experience on a feature phone via USSD.

**How to use:**
1. Go to `/ussd-simulator`
2. Dial `*384#` on the phone mockup
3. Navigate menus using number keys (1–5)
4. Explore: Prices, Transport pools, Payments, Storage, Help
5. All data is live from the Tanzanian database tables

**Menu tree:**
```
*384#
├── 1. Bei za Soko (Market Prices)
│     └── Select crop → show top 3 regional prices
├── 2. Shamba Connect (Transport)
│     └── Show open pools with departure dates
├── 3. Malango Salama (Payments)
│     └── Check transaction status by reference
├── 4. Hifadhi Yangu (Storage)
│     └── Nearest facility by region
└── 5. Msaada (Help)
      └── Contact numbers and instructions
```

---

### Feature 6 — Swahili Language Toggle
**Route:** `/` (home page)

Switch between English and Swahili for the entire dashboard.

**How to use:**
1. Go to the home page `/`
2. Click 🇹🇿 **SW** button (top right) to switch to Swahili
3. Click 🇬🇧 **EN** to switch back
4. Language preference is saved in `localStorage` — persists across browser sessions

**Statistics strip on homepage:**
- Live count of registered farmers
- Current maize price in TZS/kg (from market_prices)
- Total loads pooled (from transport_requests)

---

### Feature 7 — Demo Reset
**Route:** `GET /setup-demo`

**Use this before every demo presentation** to reset to a clean, realistic data state.

```bash
curl http://localhost:5000/setup-demo
```

Returns JSON confirming what was seeded and navigation links to all features.

---

## 🗺️ Navigation Map

| URL | Feature | Description |
|-----|---------|-------------|
| `/` | Home | Dashboard with stats strip + language toggle |
| `/market-prices` | Bei za Soko | Live crop prices board |
| `/transport` | Shamba Connect | Load pooling for farmers |
| `/payments` | Malango Salama | M-Pesa escrow payments |
| `/storage` | Hifadhi Yangu | Storage facility finder |
| `/ussd-simulator` | USSD *384# | Feature phone simulation |
| `/farmer` | Farmer Dashboard | Request transport |
| `/driver` | Driver Dashboard | Accept and manage deliveries |
| `/admin` | Admin | Manage prices, buyers, analytics |
| `/setup-demo` | Demo Reset | Reseed all tables |

---

## 📡 API Quick Reference

```
# Market Prices
GET  /api/prices
GET  /api/prices/<crop>

# Transport / Load Pooling
POST /api/transport/request
GET  /api/transport/pool/<ward>
POST /api/transport/join/<pool_id>

# M-Pesa Escrow
POST /api/payment/initiate
POST /api/payment/confirm/<id>
GET  /api/payment/status/<id>

# Storage
GET  /api/storage
GET  /api/storage/<region>
GET  /api/storage/nearest?lat=<lat>&lng=<lng>

# SMS / Africa's Talking
GET  /api/africas-talking/status

# Demo
GET  /setup-demo
```

---

## 📋 Tech Notes

- **Database:** SQLite (`database.db`) — single file, no setup needed
- **Language:** Flask 2.x + Python 3.10+
- **SMS:** Africa's Talking SDK (optional, falls back to simulation if `AT_API_KEY` not set)
- **Mobile-first:** All new pages use min 16px font, high-contrast colours, tap targets ≥44px
- **Offline-friendly:** Market prices page works with cached last response
- **2G-safe:** All USSD flows are text-only, <160 chars per screen

---

*AgriMove-AI — Connecting Tanzania's smallholder farmers directly to markets.*
