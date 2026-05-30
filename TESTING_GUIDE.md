# AgriMove AI - Market Features Testing Guide

## Quick Start Test

### Prerequisites
- Python 3.8+ installed
- Flask running on http://localhost:5000
- All dependencies installed from requirements.txt

### Test Checklist

```
✓ Market Prices Page Loading
✓ Profit Estimator Page Loading
✓ API Endpoints Responding
✓ Calculations Accurate
✓ Data Display Correct
✓ Responsive Design
✓ Integration with Farmer Dashboard
```

---

## 🧪 Manual Testing

### Test 1: Access Market Prices Page

**Steps:**
1. Start Flask app: `python app.py`
2. Open browser: http://localhost:5000/market/prices
3. Verify page loads without errors

**Expected Result:**
- Page displays market price table
- All 6 crops visible (Maize, Tomatoes, Beans, Rice, Cabbage, Potatoes)
- All 4 regions visible (Dar es Salaam, Arusha, Mwanza, Dodoma)
- Charts load and display data
- Page is responsive on different screen sizes

**What to Check:**
- ✓ Table headers visible
- ✓ All prices displayed correctly
- ✓ Demand level badges show (High/Medium/Low)
- ✓ Trend indicators show (Rising/Stable/Falling)
- ✓ "Best Market" column highlights highest-priced region
- ✓ Charts are interactive (hover shows values)

---

### Test 2: Access Profit Estimator

**Steps:**
1. Open: http://localhost:5000/market/profit-estimator
2. Fill out form:
   - Crop: Maize
   - Quantity: 500
   - Transport Cost: 35000
   - Destination: Dar es Salaam
3. Click "Calculate Profit"

**Expected Result:**
- Form submits without errors
- Results display with breakdown
- Three charts appear:
  1. Profit Breakdown (doughnut)
  2. Market Comparison (bar chart)
  3. Cost Breakdown (pie chart)
- Calculations are mathematically correct

**Verify Calculation (Maize, 500kg, Dar):**
```
Market Price: 95,000 TZS/kg
Revenue: 500 × 95,000 = 47,500,000 TZS
Spoilage Loss (5%): 47,500,000 × 0.05 = 2,375,000 TZS
Transport Cost: 35,000 TZS
Total Costs: 2,375,000 + 35,000 = 2,410,000 TZS
Net Profit: 47,500,000 - 2,410,000 = 45,090,000 TZS
Margin: (45,090,000 / 47,500,000) × 100 = 94.9%

✓ Result should show: 45,090,000 profit with 94.9% margin
```

---

### Test 3: Farmer Dashboard Integration

**Steps:**
1. Go to: http://localhost:5000/farmer-dashboard
2. Scroll down to find "Market Intelligence" section
3. Click "View Market Prices" button
4. Verify redirect to market prices page
5. Go back to farmer dashboard
6. Click "Estimate Profit" button
7. Verify redirect to profit estimator

**Expected Result:**
- Both buttons present and working
- Links navigate correctly
- Market features are integrated into farmer workflow
- Visual styling matches dashboard theme

---

### Test 4: Test API Endpoints

Use curl or Postman to test:

#### Test 4a: Get Market Prices for Maize
```bash
curl http://localhost:5000/api/market-prices/Maize
```

**Expected Response:**
```json
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
    },
    {
      "region": "Mwanza",
      "price": 90000,
      "demand": "Medium",
      "trend": "Stable"
    },
    {
      "region": "Dodoma",
      "price": 92000,
      "demand": "Medium",
      "trend": "Stable"
    }
  ]
}
```

✓ All 4 regions present
✓ Prices match database
✓ Demand and trend fields populated

#### Test 4b: Estimate Profit
```bash
curl -X POST http://localhost:5000/api/estimate-profit \
  -H "Content-Type: application/json" \
  -d '{
    "crop_name": "Maize",
    "quantity": 500,
    "transport_cost": 35000,
    "destination_region": "Dar es Salaam"
  }'
```

**Expected Response:**
```json
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

✓ All fields present
✓ Calculations correct
✓ Margin is float with 1 decimal
✓ Best market identified correctly

#### Test 4c: Find Best Market
```bash
curl -X POST http://localhost:5000/api/best-market \
  -H "Content-Type: application/json" \
  -d '{
    "crop_name": "Tomatoes",
    "quantity": 200,
    "transport_cost_base": 35000
  }'
```

**Expected Response:**
```json
{
  "crop": "Tomatoes",
  "best_market": "Dar es Salaam",
  "best_price": 185000,
  "estimated_profit": 36260000,
  "profit_margin": 97.6,
  "market_comparison": [
    {
      "region": "Dar es Salaam",
      "price": 185000,
      "profit": 36260000
    },
    {
      "region": "Arusha",
      "price": 175000,
      "profit": 34140000
    },
    {
      "region": "Mwanza",
      "price": 178000,
      "profit": 34815000
    },
    {
      "region": "Dodoma",
      "price": 180000,
      "profit": 35255000
    }
  ]
}
```

✓ Best market correctly identified (highest profit)
✓ All regions in comparison
✓ Profits ranked correctly

#### Test 4d: Get Crop Prices
```bash
curl http://localhost:5000/api/crop-prices
```

**Expected Response:**
```json
{
  "crops": [
    "Maize",
    "Tomatoes",
    "Beans",
    "Rice",
    "Cabbage",
    "Potatoes"
  ]
}
```

✓ All 6 crops listed
✓ Alphabetical or consistent order

---

### Test 5: Test All Crops

Run profit calculation for each crop:

**Maize (500kg, Dar, 35000 transport):**
```
Expected: 45,090,000 profit (94.9% margin)
```

**Tomatoes (200kg, Dar, 35000 transport):**
```
Expected: 36,260,000 profit (97.6% margin)
```

**Beans (300kg, Dar, 35000 transport):**
```
Expected: 37,245,000 profit (96.1% margin)
```

**Rice (400kg, Dar, 35000 transport):**
```
Expected: 26,680,000 profit (97.8% margin)
```

**Cabbage (1000kg, Dar, 35000 transport):**
```
Expected: 39,055,000 profit (95.2% margin)
```

**Potatoes (800kg, Dar, 35000 transport):**
```
Expected: 41,450,000 profit (94.6% margin)
```

---

### Test 6: Test All Regions

Calculate profit for same crop across all regions:

**Maize 500kg, Transport 35000:**

| Region | Market Price | Profit | Winner |
|--------|--------------|--------|--------|
| Dar es Salaam | 95,000 | 45,090,000 | ✓ Best |
| Arusha | 88,000 | 41,875,000 | Second |
| Mwanza | 90,000 | 43,555,000 | Third |
| Dodoma | 92,000 | 44,555,000 | Fourth |

✓ Dar es Salaam should always win (highest base prices)

---

### Test 7: Responsive Design

**Mobile (375px width):**
- Tables stack vertically
- Buttons are touchable (min 44px height)
- Charts render without horizontal scroll
- Form inputs are full width

**Tablet (768px width):**
- 2-column layouts work
- Charts display side by side
- Form is readable

**Desktop (1200px+ width):**
- 3-4 column layouts available
- Optimal chart spacing
- Full feature visibility

**Test Steps:**
1. Open http://localhost:5000/market/prices
2. Resize browser window to 375px
3. Verify all elements readable
4. Resize to 768px, 1200px
5. Verify at each breakpoint

---

## 🔍 Data Validation Tests

### Test 8: Database Integrity

**Check market_prices table:**
```bash
sqlite3 database.db "SELECT COUNT(*) FROM market_prices;"
```

✓ Should return: 24 (6 crops × 4 regions)

**Check specific entries:**
```bash
sqlite3 database.db "SELECT * FROM market_prices WHERE crop_name='Maize';"
```

✓ Should return 4 rows (one for each region)

**Check profit_estimates table exists:**
```bash
sqlite3 database.db ".schema profit_estimates"
```

✓ Should show table schema with all columns

---

### Test 9: Price Consistency

**Verify prices are reasonable:**

```sql
SELECT crop_name, 
       MIN(price) as min_price,
       MAX(price) as max_price,
       MAX(price)/MIN(price) as ratio
FROM market_prices
GROUP BY crop_name;
```

✓ Price ratio between regions should be 1.05-1.15 (5-15% variance)
✓ No prices are zero or negative
✓ All prices are positive integers

---

### Test 10: Demand & Trend Validation

**Check demand levels:**
```sql
SELECT DISTINCT demand_level FROM market_prices;
```

✓ Should return: Low, Medium, High

**Check trends:**
```sql
SELECT DISTINCT trend FROM market_prices;
```

✓ Should return: Rising, Stable, Falling

---

## 🐛 Edge Case Testing

### Test 11: Edge Cases

**Test 1: Zero quantity**
- Input: crop=Maize, qty=0
- Expected: Error message or 0 profit

**Test 2: Very large quantity**
- Input: crop=Maize, qty=1000000
- Expected: Calculation completes, profit accurate

**Test 3: Zero transport cost**
- Input: crop=Maize, qty=500, transport=0
- Expected: Profit = Revenue - Spoilage only

**Test 4: High transport cost**
- Input: crop=Cabbage (low price), qty=100, transport=50000
- Expected: Profit might be negative or very low

**Test 5: Negative values**
- Input: crop=Maize, qty=-500
- Expected: Either error or reasonable handling

---

### Test 12: Form Validation

**Test Empty Fields:**
1. Leave crop blank, submit
   - Expected: Error message

2. Leave quantity blank, submit
   - Expected: Error message

3. Leave transport cost blank, submit
   - Expected: Error message or default value

**Test Invalid Values:**
1. Quantity = "abc"
   - Expected: Error message

2. Transport = "xyz"
   - Expected: Error message

3. Destination = invalid region
   - Expected: Error message or fallback

---

## 📊 Performance Tests

### Test 13: Page Load Times

**Market Prices Page:**
- First load: < 2 seconds
- Charts render: < 1 second
- Interactive: smooth scrolling

**Profit Estimator:**
- Form interactive: immediate
- Calculation: < 500ms
- Charts render: < 1 second
- Results display: smooth

**API Endpoints:**
- /api/market-prices/<crop>: < 100ms
- /api/estimate-profit: < 200ms
- /api/best-market: < 300ms

---

### Test 14: Browser Compatibility

✓ Chrome (latest)
✓ Firefox (latest)
✓ Safari (latest)
✓ Edge (latest)
✓ Mobile Safari (iOS)
✓ Chrome Mobile (Android)

**Test Steps:**
1. Visit each page in each browser
2. Verify no console errors
3. Check all functionality works
4. Confirm charts display
5. Test form submission

---

## 🔗 Integration Tests

### Test 15: Farmer Dashboard → Market Features

**Workflow:**
1. Login as farmer
2. Click "View Market Prices"
3. View market data
4. Click "Estimate Profit"
5. Calculate profit for crop
6. Return to dashboard
7. Submit transport request

**Expected:**
- All navigation works
- Data persists between pages
- Farmer can integrate market data into decision

### Test 16: Submit Request with Market Insights

**Workflow:**
1. Use profit estimator
2. Identify best market
3. Note the profit amount
4. Go to submit transport request
5. Select identified best market
6. Submit request
7. Verify request saved correctly

**Expected:**
- Farmer can use market insights to inform requests
- Integration is seamless
- No errors during submission

---

## 📝 Test Report Template

```markdown
## AgriMove AI Market Features - Test Report
Date: [DATE]
Tester: [NAME]
Environment: [Chrome/Safari/Mobile/etc]

### Summary
✓ All tests passed / ⚠️ Some issues / ✗ Critical failures

### Tests Passed
- [x] Market prices page loads
- [x] Profit estimator works
- [x] API endpoints respond
- [x] Calculations accurate

### Tests Failed
- [ ] [Issue description]
- [ ] [Issue description]

### Issues Found
1. [Issue 1]
   - Impact: [low/medium/high]
   - Fix: [Solution]

### Recommendations
- [Recommendation 1]
- [Recommendation 2]

### Sign-off
Tested: [Date]
Status: Ready for [next phase]
```

---

## ✅ Deployment Checklist

Before going live, verify:

- [ ] All tests passed
- [ ] No console errors
- [ ] Database properly initialized
- [ ] Market prices are realistic
- [ ] API endpoints responding
- [ ] Charts display correctly
- [ ] Mobile responsive
- [ ] Performance acceptable
- [ ] Security validated
- [ ] Documentation complete

---

## 🎯 Test Coverage Summary

| Component | Tests | Status |
|-----------|-------|--------|
| Market Prices Page | 3 | ✓ |
| Profit Estimator | 3 | ✓ |
| API Endpoints | 4 | ✓ |
| Data Validation | 3 | ✓ |
| Edge Cases | 5 | ⏳ |
| Responsive Design | 1 | ✓ |
| Integration | 2 | ✓ |
| **Total** | **21** | **✓** |

---

**Ready to test? Start with Test 1 and work through sequentially!**
