# AgriMove-AI — Hackathon Changes Log

> Tanzania-specific agricultural logistics features added on top of the existing anti-middlemen marketplace.
> Target: Tanzanian smallholder farmers | Stack: Flask + SQLite + Vanilla JS | Language: EN/Swahili

---

## Modified Files

### `app.py`
- **Extended `init_db()`** — 4 new tables:
  - `transport_requests` — farmer load-pooling requests
  - `transport_pools` — available trucks with slots
  - `transactions` — M-Pesa escrow records
  - `storage_facilities` — certified warehouses, silos, cold stores
  - Extended `market_prices` with columns: `crop_name_swahili`, `market_name`, `price_per_kg_tzs`, `price_trend`, `last_updated`
- **Extended `/` (home route)** — passes `farmers_count`, `maize_price`, `loads_count` to template for the stats strip
- **Added `seed_market_prices()` Tanzanian extension** — seeds crops in Swahili across Kariakoo, Arusha, Mwanza, Mbeya, Dodoma markets
- **New routes added:**

| Route | Method | Feature | Description |
|-------|--------|---------|-------------|
| `/api/prices` | GET | Bei za Soko | All market prices as JSON |
| `/api/prices/<crop>` | GET | Bei za Soko | Prices filtered by crop name |
| `/market-prices` | GET | Bei za Soko | HTML dashboard |
| `/api/transport/request` | POST | Shamba Connect | Submit load-pooling request |
| `/api/transport/pool/<ward>` | GET | Shamba Connect | Find pools near a ward |
| `/api/transport/join/<pool_id>` | POST | Shamba Connect | Join a transport pool |
| `/transport` | GET | Shamba Connect | HTML page |
| `/api/payment/initiate` | POST | Malango Salama | Create M-Pesa escrow |
| `/api/payment/confirm/<id>` | POST | Malango Salama | Release escrow funds |
| `/api/payment/status/<id>` | GET | Malango Salama | Check transaction status |
| `/payments` | GET | Malango Salama | HTML page |
| `/api/storage` | GET | Hifadhi Yangu | All storage facilities |
| `/api/storage/<region>` | GET | Hifadhi Yangu | Facilities by region |
| `/api/storage/nearest` | GET | Hifadhi Yangu | Sort by GPS distance |
| `/storage` | GET | Hifadhi Yangu | HTML page |
| `/ussd-simulator` | GET | USSD *384# | Interactive USSD phone mockup |
| `/setup-demo` | GET | Demo Reset | Clears & reseeds all tables |

### `templates/index.html`
- Added **EN/SW language toggle** (flag buttons, top-right)
- Language persisted in `localStorage` under key `agrimove_lang`
- Added **Statistics strip** showing: active farmers count, live maize price (TZS/kg), total loads pooled
- All dashboard strings have `data-en` / `data-sw` attributes for live switching

### `templates/dashboard_base.html`
- Added Tanzanian module links to the sidebar navigation:
  - 📊 Bei za Soko → `/market-prices`
  - 🚛 Shamba Connect → `/transport`
  - 🔐 Malango Salama → `/payments`
  - 🏪 Hifadhi Yangu → `/storage`
  - 📱 USSD *384# → `/ussd-simulator`

---

## New Files

### `templates/bei_za_soko.html`
- High-contrast, large-text (≥16px) market price board
- Displays crop prices per kg in TZS with trend arrows (↑ ↓ →)
- Grouped by crop with Swahili name shown
- Filters: All Crops / Mahindi / Mpunga / Nyanya / Korosho etc.
- Offline-cache friendly (static data display)

### `templates/shamba_connect.html`
- Load-pooling UI for rural Tanzania farmers
- Form: village, ward, district, crop type, bags count, pickup date
- Shows matching open transport pools with Join button
- Cost calculator (bags × TZS/bag)
- Swahili labels throughout

### `templates/malango_salama.html`
- Simulated M-Pesa escrow payment flow
- 3-step: Deal Setup → Payment Pending → Funds Released
- Transaction status tracker (pending / confirmed / released)
- Generates copyable M-Pesa reference number
- SMS confirmation text simulation

### `templates/hifadhi_yangu.html`
- Storage finder with GPS distance sorting
- Region filter dropdown (Dar, Arusha, Mwanza, Mbeya, Dodoma…)
- Capacity bar (available / total tons)
- WRS (Warehouse Receipt System) badge
- Direct call button (`tel:` links) per facility

### `templates/ussd_simulator.html`
- Interactive phone mockup of the `*384#` USSD flow
- Menu navigation: Prices / Transport / Payments / Storage / Help
- Live data pulled from new Tanzanian DB tables
- Simulates 2G-safe short-session interaction pattern

---

## Demo Reset

Visit **`/setup-demo`** to clear and reseed all tables with:
- 5 Tanzanian farmers (Swahili names, +255 numbers)
- 4 drivers
- 5 delivery requests (across all statuses)
- 23 market prices (7 crops × 5 regions)
- 4 transport pools (open, with available slots)
- 4 transport requests
- 4 M-Pesa transactions (across pending/confirmed/released)
- 7 storage facilities (6 regions, including WRS-enabled)
- 4 trusted buyers

Returns JSON confirming counts and navigation links.

---

## JSON Response Contract

All API endpoints follow the standard envelope:
```json
{
  "success": true,
  "data": {},
  "message": "Human-readable status"
}
```

---

## Requirements

No new pip packages required beyond the original `requirements.txt`.
All features use standard Flask + SQLite + vanilla JS.
