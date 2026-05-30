# Admin Market Management Guide

## Overview

This guide explains how administrators manage market prices, monitor market trends, and optimize the platform for farmers.

---

## 📊 Current Market Data

### Crops Supported (6 types)
1. **Maize** - Staple crop, high volume
2. **Tomatoes** - High margin, perishable
3. **Beans** - Long shelf life, stable
4. **Rice** - Premium pricing in some regions
5. **Cabbage** - Low cost, good supply
6. **Potatoes** - Root crop, storage friendly

### Market Regions (4 regions)
1. **Dar es Salaam** - Urban, highest demand, highest prices
2. **Arusha** - Growing market, medium prices
3. **Mwanza** - Regional hub, competitive prices
4. **Dodoma** - Capital city, stable market

### Current Pricing Matrix (TZS per kg)

```
Crop        | Dar es Salaam | Arusha | Mwanza | Dodoma
------------|---------------|--------|--------|--------
Maize       | 95,000        | 88,000 | 90,000 | 92,000
Tomatoes    | 185,000       | 175,000| 178,000| 180,000
Beans       | 125,000       | 118,000| 120,000| 122,000
Rice        | 68,000        | 62,000 | 65,000 | 66,000
Cabbage     | 42,000        | 38,000 | 40,000 | 41,000
Potatoes    | 55,000        | 50,000 | 52,000 | 54,000
```

---

## 🎛️ Admin Management Tasks

### 1. Update Market Prices

**When to Update:**
- Daily (for real-time accuracy)
- After major market events
- Seasonally (crop availability changes)
- When receiving new market data

**How (Future Feature):**
```
POST /admin/api/update-price

{
  "crop_name": "Maize",
  "region": "Dar es Salaam",
  "new_price": 98000,
  "demand_level": "High",
  "trend": "Rising"
}
```

**Current Implementation:**
- Market data hardcoded in seed_market_prices()
- To update: Edit seed_market_prices() function and restart app
- Location: app.py, lines 152-214

### 2. Monitor Market Trends

**Key Metrics to Track:**
- Price volatility (high = unstable)
- Regional price gaps (large gaps = opportunity)
- Demand correlation with season
- Crop availability cycles

**Trend Types:**
- **Rising** 📈 - Prices increasing, good selling time
- **Stable** ➡️ - Steady prices, predictable
- **Falling** 📉 - Prices decreasing, market saturated

### 3. Analyze Farmer Profit Estimates

**Data to Review:**
- Most popular destinations
- Average profit margins
- Crops with highest ROI
- Regional demand patterns

**SQL Query:**
```sql
SELECT 
  crop_name,
  destination_region,
  COUNT(*) as estimate_count,
  AVG(profit_margin) as avg_margin,
  AVG(estimated_profit) as avg_profit
FROM profit_estimates
GROUP BY crop_name, destination_region
ORDER BY avg_profit DESC;
```

### 4. Set Demand Levels

**Demand Levels Explained:**

| Level | Meaning | Action |
|-------|---------|--------|
| **High** | Strong buyer interest, competitive markets | Consider increasing supply |
| **Medium** | Normal market, balanced supply/demand | Maintain current supply |
| **Low** | Weak buyer interest, excess supply | Plan production reduction |

**Examples:**
- Tomatoes in Dar: **High** (urban consumption)
- Beans in Arusha: **Medium** (balanced market)
- Potatoes in Mwanza: **Low** (low seasonal demand)

### 5. Manage Price Trends

**How Trends Affect Farmers:**

1. **Rising Trend** - Farmer sees as opportunity
   - "Sell now before prices drop"
   - Higher profit margins available
   - Encourage quick shipments

2. **Stable Trend** - Farmer sees as predictable
   - "Safe investment, reliable margins"
   - Plan long-term shipments
   - Budget for consistent costs

3. **Falling Trend** - Farmer sees as risk
   - "Don't harvest yet, prices will drop"
   - Plan alternative crops
   - Focus on costs reduction

---

## 📈 Market Analytics Dashboard

### Metrics to Monitor

#### Price Statistics
```sql
SELECT 
  crop_name,
  MIN(price) as min_price,
  MAX(price) as max_price,
  AVG(price) as avg_price,
  MAX(price) - MIN(price) as price_range
FROM market_prices
GROUP BY crop_name;
```

**Interpretation:**
- Small range = stable market
- Large range = opportunities for farmers who know markets

#### Regional Analysis
```sql
SELECT 
  region,
  COUNT(*) as crops_in_market,
  AVG(price) as avg_price_level,
  SUM(CASE WHEN demand_level = 'High' THEN 1 ELSE 0 END) as high_demand_crops
FROM market_prices
GROUP BY region;
```

#### Farmer Profit Analysis
```sql
SELECT 
  destination_region,
  COUNT(*) as shipments_planned,
  AVG(estimated_profit) as avg_farmer_profit,
  AVG(profit_margin) as avg_margin_percent
FROM profit_estimates
GROUP BY destination_region
ORDER BY avg_farmer_profit DESC;
```

---

## 🔧 Technical Implementation

### Database Tables

#### market_prices Table
```sql
CREATE TABLE market_prices (
  id INTEGER PRIMARY KEY,
  crop_name TEXT NOT NULL,
  region TEXT NOT NULL,
  price REAL NOT NULL,
  demand_level TEXT,
  trend TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(crop_name, region)
);
```

**Fields:**
- `crop_name`: "Maize", "Tomatoes", etc.
- `region`: "Dar es Salaam", "Arusha", etc.
- `price`: Price in TZS per kg
- `demand_level`: "Low", "Medium", "High"
- `trend`: "Rising", "Stable", "Falling"

#### profit_estimates Table
```sql
CREATE TABLE profit_estimates (
  id INTEGER PRIMARY KEY,
  farmer_id INTEGER NOT NULL,
  crop_name TEXT NOT NULL,
  quantity REAL NOT NULL,
  transport_cost REAL NOT NULL,
  destination_region TEXT NOT NULL,
  estimated_revenue REAL,
  estimated_profit REAL,
  profit_margin REAL,
  recommended_market TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(farmer_id) REFERENCES farmers(id)
);
```

### API Endpoints for Admin

#### Get All Market Prices
```
GET /api/all-market-prices

Response:
[
  {
    "id": 1,
    "crop_name": "Maize",
    "region": "Dar es Salaam",
    "price": 95000,
    "demand_level": "High",
    "trend": "Rising"
  },
  ...
]
```

#### Update Single Price
```
POST /admin/api/update-price
(Future implementation)

{
  "crop_name": "Maize",
  "region": "Dar es Salaam",
  "price": 98000,
  "demand_level": "High",
  "trend": "Rising"
}
```

#### Bulk Import Prices
```
POST /admin/api/import-prices
(Future implementation)

{
  "source": "african-data-hub",
  "crops": ["Maize", "Tomatoes"],
  "regions": ["Dar es Salaam", "Arusha"]
}
```

---

## 📱 Admin Dashboard Views

### Market Overview Card
Shows quick statistics:
- Total crops in system
- Total regions covered
- Average price level
- High demand markets

### Price Monitoring Table
Editable table with:
- Crop name
- Region
- Current price
- Demand level
- Trend
- Last updated
- Edit/Delete buttons

### Regional Performance
Compare regions by:
- Average price level
- Demand intensity
- Farmer activity
- Transaction volume

### Crop Performance
Track crops by:
- Average price
- Price range (volatility)
- Demand consistency
- Farmer interest

---

## 💡 Best Practices

### 1. Keep Prices Realistic
- Research actual market conditions
- Don't set artificial price floors
- Allow natural supply/demand dynamics
- Update seasonally

### 2. Balance Regional Pricing
- Prices should vary (Dar > Arusha > Rural)
- But not too much (ruins incentive to find best market)
- Realistic: 5-15% difference between regions
- Current system: 5-10% differences ✓

### 3. Set Accurate Demand Levels
- Research buyer activity
- High demand = selling competes on speed
- Medium demand = balanced
- Low demand = oversupply risk

### 4. Use Realistic Trends
- Match actual market conditions
- Don't mislead farmers
- Update frequently for accuracy
- Remember: trends affect farmer psychology

### 5. Monitor Farmer Behavior
- Where do farmers want to ship?
- Which crops are most profitable?
- Are recommendations being followed?
- Adjust data to match reality

---

## 🎯 Optimization Strategies

### For Maximum Farmer Profit
1. Ensure market prices reflect reality
2. Highlight best markets prominently
3. Provide accurate transport cost data
4. Monitor spoilage assumptions (currently 5%)

### For Balanced Market Health
1. Avoid price spikes (damages farmer confidence)
2. Maintain regional variety (competitive markets)
3. Reflect seasonal changes (realistic modeling)
4. Update data consistently (trust-building)

### For System Engagement
1. Show farmers how to maximize earnings
2. Make market data accessible
3. Provide profit projections
4. Celebrate farmer successes

---

## 🔄 Workflow Example: Seasonal Price Update

### Scenario: Maize harvest season ends, prices rise

**Step 1: Monitor Market**
- Farmers report rising maize prices
- Market feedback: "Fewer sellers, buyers still need maize"

**Step 2: Update Prices**
```
Maize (before): 95,000 → 102,000 (Dar es Salaam)
Maize (before): 88,000 → 94,000 (Arusha)
Maize (before): 90,000 → 97,000 (Mwanza)
Maize (before): 92,000 → 99,000 (Dodoma)
```

**Step 3: Update Trends**
```
Maize: "Falling" → "Rising"
Demand: "Medium" → "High"
```

**Step 4: Communicate**
- System shows: "Maize prices rising! Good time to sell"
- Farmers use profit estimator: See higher profits
- More farmers submit maize shipments
- Supply enters market → prices stabilize

---

## 📊 Key Formulas Used

### Profit Calculation
```
estimated_revenue = quantity × market_price
spoilage_loss = estimated_revenue × 0.05 (hardcoded 5%)
total_costs = transport_cost + spoilage_loss
estimated_profit = estimated_revenue - total_costs
profit_margin = (estimated_profit / estimated_revenue) × 100
```

### Best Market Algorithm
```
For each region:
  calculate profit using estimate_profit()
Return region with max profit
```

### Price Variance Analysis
```
price_range = max_price - min_price
price_volatility = price_range / avg_price × 100
High volatility = unstable market
Low volatility = stable market
```

---

## 🚀 Future Admin Features (Roadmap)

### Phase 1: Enhanced Management
- [ ] Web UI for price editing (no code restart)
- [ ] Bulk import from CSV/Excel
- [ ] Price audit trail (who changed what/when)
- [ ] Automated alerts for price anomalies

### Phase 2: Data Integration
- [ ] Real-time data from African Data Hub
- [ ] Weather impact on prices
- [ ] Seasonal forecasting
- [ ] Competitor price tracking

### Phase 3: Advanced Analytics
- [ ] Predictive pricing models
- [ ] Farmer behavior heatmaps
- [ ] Profit optimization recommendations
- [ ] Market health scores

### Phase 4: Automation
- [ ] Auto-update prices from data providers
- [ ] Automatic demand level adjustment
- [ ] Price anomaly detection
- [ ] Farmer alert generation

---

## 🔐 Data Governance

### Access Control
- Only admins can modify market prices
- All changes should be logged
- Farmers can only read market data
- API access is public for market data

### Data Accuracy
- Prices must be verified
- No speculative pricing
- Regular calibration with real markets
- Transparent methodology

### Farmer Trust
- Accurate data builds farmer confidence
- Consistent updates show commitment
- Realistic trends build credibility
- Fair regional pricing maintains fairness

---

## 📞 Support

### Common Admin Tasks

**Q: How do I update prices without restarting the app?**
A: Future feature. Currently: edit seed_market_prices() and restart.

**Q: What if farmer says price is wrong?**
A: Verify with market research, update if incorrect, note the feedback.

**Q: Should prices vary more between regions?**
A: No - 5-10% variance is realistic. More creates distrust.

**Q: How often should I update?**
A: Daily ideal, weekly minimum, seasonal at least.

**Q: Can I edit profit loss percentage?**
A: Currently hardcoded at 5%. Custom per-crop in future.

---

**Last Updated:** 2024 | AgriMove AI Admin Suite
