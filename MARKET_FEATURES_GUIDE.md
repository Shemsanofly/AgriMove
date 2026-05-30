# AgriMove AI - Market Transparency & Profit Estimation Guide

## Overview

AgriMove AI now includes **Market Intelligence** features that help farmers make data-driven decisions about crop sales. The platform provides real-time market prices across regions and AI-powered profit estimations.

---

## 🎯 Market Transparency Module

### What It Does
- Displays real-time crop prices across multiple regions
- Shows market demand levels and price trends
- Helps farmers identify the best-paying markets for their products

### Features

#### 1. **Market Price Table**
View current prices for all crops by region:

| Crop | Dar es Salaam | Arusha | Mwanza | Dodoma | Best Market |
|------|---------------|---------|---------|---------|------------|
| Maize | 95,000 TZS | 88,000 TZS | 90,000 TZS | 92,000 TZS | Dar es Salaam |
| Tomatoes | 185,000 TZS | 175,000 TZS | 178,000 TZS | 180,000 TZS | Dar es Salaam |
| Beans | 125,000 TZS | 118,000 TZS | 120,000 TZS | 122,000 TZS | Dar es Salaam |
| Rice | 68,000 TZS | 62,000 TZS | 65,000 TZS | 66,000 TZS | Dar es Salaam |

#### 2. **Demand Indicators**
Each market shows current demand level:
- **High** - Strong buyer interest, prices may increase
- **Medium** - Normal market conditions
- **Low** - Limited buyers, prices may drop

#### 3. **Price Trends**
Visual indicators show price direction:
- 📈 **Rising** - Prices going up (good time to sell soon)
- ➡️ **Stable** - Steady market (predictable)
- 📉 **Falling** - Prices dropping (consider different crops)

#### 4. **Interactive Charts**
- **Price Comparison Chart**: Compare crop prices across all regions
- **Market Distribution**: See which regions have highest demand
- **Trend Visualization**: Track price movements over time

---

## 💰 Profit Estimator System

### What It Does
The Profit Estimator helps farmers calculate expected earnings **before shipping**, considering:
- Crop type and quantity
- Transport costs
- Market destination
- Spoilage losses (5% estimated handling loss)

### How It Works

#### Input Form
Fill in these details:
```
Crop Type:       [Maize]
Quantity:        [500 kg]
Transport Cost:  [35,000 TZS]
Destination:     [Dar es Salaam]
[Calculate Profit]
```

#### Calculation Formula
```
Revenue = Quantity × Market Price
Losses = Revenue × 5% (spoilage/handling loss)
Total Costs = Transport Cost + Losses
Profit = Revenue - Total Costs
Margin = (Profit / Revenue) × 100%
```

#### Example Calculation
**Scenario: Selling 500kg of Maize to Dar es Salaam**

```
Market Price:           95,000 TZS/kg (Dar es Salaam)
Quantity:              500 kg
─────────────────────────────
Revenue:               47,500,000 TZS
Spoilage Loss (5%):    2,375,000 TZS
Transport Cost:        35,000 TZS
─────────────────────────────
Total Costs:           2,410,000 TZS
Net Profit:            45,090,000 TZS
Profit Margin:         94.9%
```

### Results Visualization

The system shows three charts:

1. **Profit Breakdown (Doughnut Chart)**
   - Revenue vs Costs at a glance
   - Color-coded visualization

2. **Market Comparison (Bar Chart)**
   - Profit potential in each region
   - Shows which market is best for your crop/quantity

3. **Cost Breakdown (Pie Chart)**
   - Transport costs
   - Spoilage/handling losses
   - Helps identify where to optimize

---

## 🎯 How Farmers Use Market Features

### Workflow 1: Find Best Market
1. Go to **Farmer Dashboard**
2. Click **"View Market Prices"**
3. Compare prices across regions
4. Identify highest-paying market for your crop
5. Note the "Best Market" indicator

### Workflow 2: Calculate Expected Profit
1. Go to **Farmer Dashboard**
2. Click **"Estimate Profit"**
3. Enter crop details:
   - Which crop you're harvesting
   - How much you have (kg)
   - Transport cost you'll pay
   - Which market you want to sell to
4. Click **"Calculate"**
5. View detailed profit breakdown
6. Compare across markets
7. Make informed decision on where to ship

### Workflow 3: Make Data-Driven Shipping Decisions
1. Check **Market Prices** to see where demand is highest
2. Use **Profit Estimator** to calculate earnings for each option
3. Factor in transport costs and storage
4. Submit transport request to your best option
5. Track delivery in real-time

---

## 📊 Example Scenarios

### Scenario 1: Maize Farmer (500kg)
```
Crop: Maize
Quantity: 500kg
Options:

Option 1 - Dar es Salaam:
  Price: 95,000/kg
  Transport: 35,000 TZS
  Profit: 45,090,000 TZS (94.9% margin)
  
Option 2 - Arusha:
  Price: 88,000/kg
  Transport: 28,000 TZS
  Profit: 41,875,000 TZS (94.9% margin)
  
Option 3 - Mwanza:
  Price: 90,000/kg
  Transport: 32,000 TZS
  Profit: 43,555,000 TZS (94.9% margin)

Best Choice: Dar es Salaam (+3,215,000 TZS more profit)
```

### Scenario 2: Tomato Farmer (200kg) - Time Sensitive
```
Crop: Tomatoes
Quantity: 200kg
Current Market Status:
  - Dar: 185,000/kg (High Demand, Rising)
  - Arusha: 175,000/kg (Medium, Stable)
  
Recommendation: Dar es Salaam
- Higher price
- Rising trend (prices going up)
- High demand means faster sale
- Minimize spoilage by selling quickly
```

### Scenario 3: Compare Crops Before Planting
```
Available Land: 5 hectares
Budget: 1,000,000 TZS

Test different crops:

Maize (5,000kg):
- Best Market: Dar (95,000/kg)
- Revenue: 475,000,000
- Profit: 450,900,000

Tomatoes (2,000kg):
- Best Market: Dar (185,000/kg)
- Revenue: 370,000,000
- Profit: 350,850,000

Beans (3,000kg):
- Best Market: Dar (125,000/kg)
- Revenue: 375,000,000
- Profit: 356,250,000

Best ROI: Maize
```

---

## 🔌 REST API Endpoints

### Get Market Prices for a Crop
```
GET /api/market-prices/<crop>

Response:
{
  "crop": "Maize",
  "regions": [
    {
      "region": "Dar es Salaam",
      "price": 95000,
      "demand": "High",
      "trend": "Rising"
    },
    {
      "region": "Arusha",
      "price": 88000,
      "demand": "Medium",
      "trend": "Stable"
    }
  ]
}
```

### Calculate Profit
```
POST /api/estimate-profit

Request:
{
  "crop_name": "Maize",
  "quantity": 500,
  "transport_cost": 35000,
  "destination_region": "Dar es Salaam"
}

Response:
{
  "crop": "Maize",
  "quantity": 500,
  "market_price": 95000,
  "estimated_revenue": 47500000,
  "spoilage_loss": 2375000,
  "total_costs": 2410000,
  "estimated_profit": 45090000,
  "profit_margin": 94.9,
  "best_market": "Dar es Salaam"
}
```

### Find Best Market
```
POST /api/best-market

Request:
{
  "crop_name": "Maize",
  "quantity": 500,
  "transport_cost_base": 35000
}

Response:
{
  "crop": "Maize",
  "best_market": "Dar es Salaam",
  "best_price": 95000,
  "estimated_profit": 45090000,
  "profit_margin": 94.9,
  "market_comparison": [
    {
      "region": "Dar es Salaam",
      "price": 95000,
      "profit": 45090000
    },
    {
      "region": "Arusha",
      "price": 88000,
      "profit": 41875000
    }
  ]
}
```

### Save Profit Estimate
```
POST /api/save-profit-estimate

Request:
{
  "farmer_id": 1,
  "crop_name": "Maize",
  "quantity": 500,
  "transport_cost": 35000,
  "destination_region": "Dar es Salaam"
}

Response:
{
  "success": true,
  "estimate_id": 3,
  "message": "Profit estimate saved successfully"
}
```

---

## 📈 Database Schema

### market_prices Table
```sql
CREATE TABLE market_prices (
  id INTEGER PRIMARY KEY,
  crop_name TEXT NOT NULL,
  region TEXT NOT NULL,
  price REAL NOT NULL,
  demand_level TEXT,
  trend TEXT,
  updated_at TIMESTAMP,
  UNIQUE(crop_name, region)
);
```

**Sample Data:**
- Maize: 95,000 (Dar), 88,000 (Arusha), 90,000 (Mwanza), 92,000 (Dodoma)
- Tomatoes: 185,000 (Dar), 175,000 (Arusha), 178,000 (Mwanza), 180,000 (Dodoma)
- Beans: 125,000 (Dar), 118,000 (Arusha), 120,000 (Mwanza), 122,000 (Dodoma)
- Rice: 68,000 (Dar), 62,000 (Arusha), 65,000 (Mwanza), 66,000 (Dodoma)
- Cabbage: 42,000 (Dar), 38,000 (Arusha), 40,000 (Mwanza), 41,000 (Dodoma)
- Potatoes: 55,000 (Dar), 50,000 (Arusha), 52,000 (Mwanza), 54,000 (Dodoma)

### profit_estimates Table
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
  created_at TIMESTAMP,
  FOREIGN KEY(farmer_id) REFERENCES farmers(id)
);
```

---

## 🚀 Access Points

### For Farmers
1. **Farmer Dashboard** → `/farmer-dashboard`
2. **Market Prices** → `/market/prices`
3. **Profit Estimator** → `/market/profit-estimator`

### For Admin
1. **Market Management** → `/admin/market-prices` (editable)
2. **Analytics** → `/admin/analytics` (includes market trends)

### API Access
- **Market Data**: `/api/market-prices/<crop>`
- **Profit Calculation**: `/api/estimate-profit` (POST)
- **Best Market**: `/api/best-market` (POST)
- **Price Comparison**: `/api/crop-prices` (GET)

---

## 🔄 Integration with Farmer Request Flow

### Enhanced Request Submission
When farmers submit transport requests, the system now:

1. **Pre-calculates profit** for requested destination
2. **Suggests best market** if different from selected
3. **Shows estimated earnings** before committing
4. **Saves profit estimate** for farmer records
5. **Enables comparison** across multiple shipments

### Workflow Example
```
Farmer Action: Submit Transport Request
System Response:
  ↓
Check selected destination market
  ↓
Calculate estimated profit
  ↓
Compare with other markets
  ↓
Highlight savings opportunity
  ↓
Show: "You could earn 3,215,000 more TZS shipping to Dar instead of Arusha!"
  ↓
Farmer decides to confirm or change destination
```

---

## 💡 Tips for Maximum Profit

### 1. Check Market Trends First
- Always look at price trends before deciding
- Rising prices = good timing to sell
- Falling prices = consider different crops

### 2. Factor in Transport Costs
- 35,000 TZS average transport cost
- Longer routes cost more
- Compare total profit, not just price per kg

### 3. Monitor Demand
- High demand = faster sales
- Less spoilage = higher profit
- Example: Tomatoes in high-demand markets sell faster

### 4. Batch Shipments
- Larger quantities = better per-kg profit
- But higher transport costs
- Use profit estimator to find optimal batch size

### 5. Plan Ahead
- Use market data to decide what to plant
- Calculate ROI for different crops
- Choose highest-margin crops for your capacity

---

## 📱 Mobile Responsiveness

All market features are fully responsive:
- ✅ Tables are mobile-friendly
- ✅ Charts adapt to screen size
- ✅ Forms are easy to fill on phones
- ✅ Results display clearly on mobile

---

## 🔐 Data Security & Privacy

- Farmer profit estimates are private (only farmer can see)
- Market prices are public reference data
- No sensitive personal data exposed through APIs
- All calculations done server-side

---

## 🎓 Learning Resources

### Understanding Market Economics
- **Price Variance**: Same crop has different prices by region
- **Demand Impact**: High demand = higher prices
- **Cost Minimization**: Smart logistics = bigger profits
- **Time Value**: Fresh produce = premium pricing

### Real-World Application
- Use historical market data to forecast
- Track price patterns by season
- Plan crop rotation for maximum profit
- Build relationships with high-paying markets

---

## 📞 Support

### Common Questions

**Q: Why do prices vary by region?**
A: Regional supply/demand differences. Dar es Salaam is urban (more buyers, higher prices). Rural areas may have lower prices.

**Q: What's the 5% spoilage loss?**
A: Average handling/transport damage. Higher for delicate crops (tomatoes), lower for hardy crops (maize).

**Q: Can I negotiate below market price?**
A: These are reference prices. Real negotiations depend on buyer relationships and product quality.

**Q: How often do prices update?**
A: In production, they'd update daily/weekly. Current system updates at app restart.

**Q: Which market should I always choose?**
A: Dar es Salaam usually has highest prices, but consider transport costs and time.

---

## 🎯 Next Features (Future Roadmap)

- [ ] Real-time market data provider integration (African Data Hub, etc.)
- [ ] Price prediction using historical trends
- [ ] SMS alerts for price spikes
- [ ] Market-specific buyer contacts
- [ ] Quality-based price adjustments
- [ ] Seasonal price forecasting
- [ ] Peer benchmarking (compare with other farmers)
- [ ] Export historical estimates to PDF

---

**Built with ❤️ for African Farmers | AgriMove AI © 2024**
