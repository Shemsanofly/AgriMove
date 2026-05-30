# Anti-Middlemen Protection & Buyer Marketplace

## Overview

AgriMove AI now features a powerful **Anti-Middlemen Protection System** and **Direct Buyer Marketplace** that empowers farmers by:

- 🛡️ **Protecting** farmers from exploitative middlemen
- 💰 **Providing** transparent price comparisons against market averages
- 🤝 **Connecting** farmers directly with verified buyers
- 📊 **Showing** fair price alerts and recommendations
- ✅ **Verifying** trusted buyers through a verification system

---

## System Architecture

### Database Tables

#### 1. **buyer_offers** Table
Stores all crop demands posted by buyers.

```sql
CREATE TABLE buyer_offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER NOT NULL,
    buyer_name TEXT NOT NULL,
    crop_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    offered_price REAL NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'Active',
    farmer_id INTEGER,
    accepted_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (buyer_id) REFERENCES buyers (id),
    FOREIGN KEY (farmer_id) REFERENCES farmers (id)
);
```

#### 2. **trusted_buyers** Table
Stores verified buyer information.

```sql
CREATE TABLE trusted_buyers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER NOT NULL,
    buyer_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    verification_status TEXT DEFAULT 'Pending',
    verified_by TEXT,
    verified_at TEXT,
    rating REAL DEFAULT 5.0,
    total_purchases INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE(buyer_id, buyer_name)
);
```

#### 3. **price_alerts** Table
Tracks price comparison alerts for farmers.

```sql
CREATE TABLE price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    offer_id INTEGER NOT NULL,
    crop_name TEXT NOT NULL,
    market_price REAL NOT NULL,
    offered_price REAL NOT NULL,
    price_difference REAL NOT NULL,
    percentage_below REAL NOT NULL,
    alert_type TEXT DEFAULT 'warning',
    created_at TEXT NOT NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmers (id),
    FOREIGN KEY (offer_id) REFERENCES buyer_offers (id)
);
```

---

## Features

### 1. Buyer Marketplace Dashboard

**Route:** `/buyer/marketplace`

**Features:**
- Post crop demand with quantity and price offer
- View active crop demands from other buyers
- Track buyer verification status
- Filter crops by type
- Manage posted demands

**Form Fields:**
- Buyer Name
- Phone Number
- Crop Needed (Maize, Tomatoes, Beans, Rice, Cabbage, Potatoes)
- Quantity (in units)
- Offered Price Per Unit
- Pickup Location
- Description (optional)

**UI Components:**
- Modern post offer card on the left
- Active offers grid on the right
- Verified buyers section at the bottom
- Real-time offer display

---

### 2. Fair Price Checker (Anti-Middlemen Protection)

**API Endpoint:** `POST /api/fair-price-check`

**Purpose:** Compares buyer offers with market average prices to detect exploitation.

**Request Payload:**
```json
{
    "crop_name": "Maize",
    "offered_price": 88000,
    "quantity": 100,
    "destination": "Dar es Salaam"
}
```

**Response:**
```json
{
    "is_fair": false,
    "alert_type": "warning",
    "message": "⚠️ WARNING: Offer is 7.3% below market average",
    "market_average_price": 95000,
    "offered_price": 88000,
    "difference": -7000,
    "percentage_below": 7.3,
    "recommended_price": 90250,
    "total_market_value": 9500000,
    "total_offered_value": 8800000
}
```

**Alert Types:**
- ✅ **success** - Offer is above market average (0% to -20%)
- ℹ️ **info** - Offer matches market average or within acceptable range (0% to 10%)
- ⚠️ **warning** - Offer is 10% to 30% below market average
- ❌ **danger** - Offer is more than 30% below market average (likely exploitation)

---

### 3. Farmer Offers Dashboard

**Route:** `/farmer/offers/<farmer_id>`

**Features:**
- View all active buyer offers
- Filter offers by crop type
- See fair price alerts for each offer
- Compare prices with market averages
- Accept offers that are fair

**Key Information Displayed:**
- Buyer name and location
- Crop type and quantity needed
- Offered price per unit
- Buyer verification status
- Fair price warning/alert
- Total value calculation

**Price Comparison Analysis:**
Shows detailed comparison including:
- Market average price
- Offered price
- Price difference
- Percentage below/above market
- Recommended price
- Total market value vs total offered value

---

### 4. Trusted Buyer Verification System

**API Endpoint:** `GET /api/trusted-buyers`

**Purpose:** Displays verified and trusted buyers to farmers.

**Response:**
```json
[
    {
        "id": 1,
        "buyer_id": 1,
        "buyer_name": "Premium Foods Ltd",
        "phone": "+255 123 456 789",
        "verification_status": "Verified",
        "rating": 4.9,
        "total_purchases": 45
    }
]
```

**Verification Levels:**
- 🔴 **Pending** - Awaiting verification
- 🟡 **Verified** - Passed verification, safe to trade with
- 🟢 **Trusted** - Long history of fair dealings

---

### 5. API Endpoints

#### Create Buyer Offer
```
POST /api/buyer-offer/create

Payload:
{
    "buyer_name": "John Buyer",
    "phone": "+255 123 456 789",
    "crop_name": "Maize",
    "quantity": 100,
    "offered_price": 88000,
    "location": "Dar es Salaam",
    "description": "Need for mill"
}

Response:
{
    "success": true,
    "offer_id": 1,
    "message": "Offer posted successfully. Total: 100 units at 88000/unit"
}
```

#### Get Buyer Offers
```
GET /api/buyer-offers
GET /api/buyer-offers?crop=Maize

Response:
[
    {
        "id": 1,
        "buyer_name": "John Buyer",
        "crop_name": "Maize",
        "quantity": 100,
        "offered_price": 88000,
        "location": "Dar es Salaam",
        "status": "Active",
        "created_at": "2024-01-15T10:30:00"
    }
]
```

#### Accept Buyer Offer
```
POST /api/offer/accept

Payload:
{
    "offer_id": 1,
    "farmer_id": 5
}

Response:
{
    "success": true,
    "message": "Offer accepted successfully"
}
```

#### Check Fair Price
```
POST /api/fair-price-check

Payload:
{
    "crop_name": "Maize",
    "offered_price": 88000,
    "quantity": 100,
    "destination": "Dar es Salaam"
}

Response: (see Fair Price Checker section above)
```

---

## How It Works: Complete User Journey

### For Buyers

1. **Access Buyer Marketplace**
   - Navigate to `/buyer/marketplace`
   - See current active crop demands from other buyers

2. **Post Crop Demand**
   - Fill in the form with crop details, quantity, and offered price
   - Submit the form
   - Offer appears in the "Active Crop Demands" section

3. **Track Offers**
   - View all posted demands
   - See buyer verification status
   - Track total offer values

### For Farmers

1. **Access Farmer Offers**
   - Go to Farmer Dashboard
   - Click "View Buyer Offers" in Market Intelligence section
   - Or navigate to `/farmer/offers/<farmer_id>`

2. **View Available Offers**
   - See all active buyer crop demands
   - Filter by crop type using the search box
   - View buyer information and location

3. **Price Comparison**
   - Click "Compare Price" on any offer
   - See detailed price analysis:
     - Market average vs offered price
     - Fair price alert (color-coded)
     - Total value comparison
     - Recommended fair price

4. **Accept Fair Offers**
   - Click "Accept Offer" for good prices
   - Offer is marked as accepted
   - Buyer is notified

---

## Price Protection Algorithm

### Alert Color Coding

```
Percentage Below Market Average:
├─ < 0% (Above Market)      → 💰 SUCCESS  (Green)    "Great! Offer is X% above market"
├─ 0% (Matches Market)       → 💯 INFO     (Blue)     "Offer matches market average"
├─ 0-10% Below Market        → ℹ️ INFO     (Blue)     "Offer is X% below (acceptable)"
├─ 10-30% Below Market       → ⚠️ WARNING  (Yellow)   "WARNING: Offer is X% below market"
└─ >30% Below Market         → ❌ DANGER   (Red)      "DANGER: Likely exploitation!"
```

### Fair Price Calculation

```
Fair Price Threshold:
├─ Minimum Acceptable = Market Average × 90% (10% below is acceptable)
├─ Recommended Price  = Market Average × 95% (5% buffer for processing)
└─ Exploitation Level = Market Average × 70% (30% below is dangerous)

Total Value = Offered Price × Quantity
```

---

## Integration with Existing Features

### Market Prices Module
- Uses existing `market_prices` table for comparison
- 6 crops tracked across 4 regions
- Real-time price data for fairness calculation

### Farmer Dashboard
- Quick link to "View Buyer Offers"
- Accessible from market intelligence section
- Integrates with transport request system

### Driver Dashboard
- Drivers can see buyer marketplace
- Understanding supply-demand helps with route planning

### Admin Dashboard
- Admin can verify buyers
- Monitor offer acceptance rates
- Track fair price compliance

---

## Security & Trust Features

### Buyer Verification
- Phone number validation
- Multi-level verification system (Pending → Verified)
- Rating system based on transaction history

### Fair Price Protection
- Automatic market price comparison
- Visual warnings for suspicious offers
- Protection against exploitation

### Transaction Tracking
- All offers logged with timestamps
- Acceptance history maintained
- Audit trail for disputes

---

## Example Scenarios

### Scenario 1: Fair Offer
```
Market Average: 95,000 per unit
Buyer Offers:   92,000 per unit
Percentage:     3.2% below market (ACCEPTABLE)
Alert Type:     INFO (Blue)
Message:        "Offer is 3.2% below market average (acceptable range)"
```

### Scenario 2: Exploitative Offer
```
Market Average: 95,000 per unit
Buyer Offers:   65,000 per unit
Percentage:     31.5% below market (DANGER!)
Alert Type:     DANGER (Red)
Message:        "DANGER: Offer is 31.5% below market value. Likely exploitation!"
```

### Scenario 3: Excellent Offer
```
Market Average: 95,000 per unit
Buyer Offers:   105,000 per unit
Percentage:     10.5% above market (GREAT!)
Alert Type:     SUCCESS (Green)
Message:        "Great! Offer is 10.5% above market average!"
```

---

## Managing the Marketplace

### As Admin
1. Access Admin Dashboard
2. Monitor buyer verification requests
3. Verify trusted buyers
4. Track marketplace health metrics
5. Generate reports on fair trading

### As Farmer
1. Regularly check for new offers
2. Use price comparison tool
3. Accept fair offers only
4. Build reputation through trades
5. Report suspicious offers

### As Buyer
1. Post clear, competitive offers
2. Complete trades fairly
3. Build verified buyer status
4. Maintain good ratings
5. Expand sourcing network

---

## Troubleshooting

### Offer Not Showing
- Check if offer status is "Active"
- Verify crop name matches database
- Clear browser cache and reload

### Price Comparison Not Loading
- Ensure market prices exist for the crop
- Check internet connection
- Verify crop name spelling

### Buyer Verification Issues
- Wait for admin verification
- Contact support with buyer details
- Provide transaction history

---

## Future Enhancements

1. **Direct Messaging** - Buyers and farmers chat in-app
2. **Rating System** - Both parties rate transactions
3. **Payment Integration** - Mobile money integration (M-Pesa)
4. **Contract System** - Smart contracts for long-term agreements
5. **Quality Grading** - AI-based crop quality assessment
6. **Price Prediction** - ML-based price forecasting
7. **Logistics Bundling** - Group shipments for cost savings
8. **Insurance** - Crop insurance integration
9. **Weather Alerts** - Weather-based price predictions
10. **Supply Chain Analytics** - Full transparency dashboard

---

## Support & Documentation

For more help:
- 📖 Visit the Help Center: `/help`
- 💬 Contact Support: `support@agrimove.ai`
- 📊 View Analytics: Admin Dashboard
- 📱 Mobile App Coming Soon

---

**Version:** 1.0  
**Last Updated:** January 2024  
**Status:** Production Ready
