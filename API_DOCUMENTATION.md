# AgriMove AI - Complete REST API Documentation

## API Overview

AgriMove AI provides a comprehensive REST API for accessing platform functionality. All endpoints return JSON responses.

**Base URL:** `http://localhost:5000`

---

## 📋 API Categories

1. **Request Management** - Farmer requests & tracking
2. **Driver Operations** - Job acceptance & status updates
3. **Admin Operations** - System monitoring
4. **Market Intelligence** - Prices & profit calculations
5. **Notifications** - Alerts & messages
6. **User Management** - Profiles & preferences

---

## 🚀 Request Management APIs

### 1. Submit Transport Request
**Endpoint:** `POST /api/submit-request`

**Request Body:**
```json
{
  "farmer_id": 1,
  "pickup_location": "Morogoro",
  "destination": "Dar es Salaam",
  "goods_type": "Maize",
  "quantity": 500,
  "pickup_time": "2024-05-28 08:00"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Request submitted successfully",
  "request_id": 15,
  "status": "Pending",
  "estimated_driver_time": 2,
  "created_at": "2024-05-28T14:20:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "success": false,
  "error": "Missing required field: goods_type"
}
```

---

### 2. Get All Farmer Requests
**Endpoint:** `GET /api/my-requests`

**Query Parameters:**
```
?farmer_id=1
?status=Pending    (optional filter)
?limit=10          (optional, default 20)
```

**Response (200 OK):**
```json
{
  "success": true,
  "requests": [
    {
      "id": 15,
      "farmer_id": 1,
      "pickup_location": "Morogoro",
      "destination": "Dar es Salaam",
      "goods_type": "Maize",
      "quantity": 500,
      "status": "In Transit",
      "driver_id": 3,
      "driver_name": "John",
      "created_at": "2024-05-28T14:20:00Z",
      "estimated_time": 120,
      "actual_time": null
    }
  ],
  "total": 1
}
```

---

### 3. Get Request Details
**Endpoint:** `GET /api/request/<request_id>`

**Response (200 OK):**
```json
{
  "success": true,
  "request": {
    "id": 15,
    "farmer_id": 1,
    "farmer_name": "Alice",
    "driver_id": 3,
    "driver_name": "John",
    "driver_phone": "0712345678",
    "pickup_location": "Morogoro",
    "destination": "Dar es Salaam",
    "goods_type": "Maize",
    "quantity": 500,
    "status": "In Transit",
    "distance_km": 195,
    "price": 2500000,
    "created_at": "2024-05-28T14:20:00Z",
    "estimated_time": 120,
    "actual_time": null,
    "rating": null,
    "review": null
  }
}
```

---

### 4. Cancel Request
**Endpoint:** `POST /api/cancel-request`

**Request Body:**
```json
{
  "request_id": 15,
  "reason": "Found another driver"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Request cancelled successfully"
}
```

---

## 👨‍💼 Driver Operations APIs

### 5. Get Available Requests
**Endpoint:** `GET /api/available-requests`

**Query Parameters:**
```
?driver_id=3
?limit=10
```

**Response (200 OK):**
```json
{
  "success": true,
  "requests": [
    {
      "id": 15,
      "farmer_id": 1,
      "farmer_name": "Alice",
      "farmer_phone": "0765432100",
      "pickup_location": "Morogoro",
      "destination": "Dar es Salaam",
      "goods_type": "Maize",
      "quantity": 500,
      "distance_km": 195,
      "estimated_time": 120,
      "price": 2500000,
      "created_at": "2024-05-28T14:20:00Z"
    }
  ],
  "total": 5
}
```

---

### 6. Accept Job
**Endpoint:** `POST /api/accept-request`

**Request Body:**
```json
{
  "request_id": 15,
  "driver_id": 3
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Job accepted successfully",
  "request_id": 15,
  "estimated_arrival": "2024-05-28T16:20:00Z",
  "earnings": 2500000
}
```

---

### 7. Update Delivery Status
**Endpoint:** `POST /api/update-status`

**Request Body:**
```json
{
  "request_id": 15,
  "status": "In Transit"
}
```

**Allowed Statuses:**
- `Accepted` - Driver accepted job
- `In Transit` - Started delivery
- `Delivered` - Delivery complete

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Status updated to In Transit",
  "request_id": 15,
  "current_status": "In Transit"
}
```

---

### 8. Get Driver Jobs
**Endpoint:** `GET /api/my-jobs`

**Query Parameters:**
```
?driver_id=3
?status=Completed    (optional filter)
```

**Response (200 OK):**
```json
{
  "success": true,
  "jobs": [
    {
      "id": 15,
      "farmer_name": "Alice",
      "goods_type": "Maize",
      "destination": "Dar es Salaam",
      "status": "Delivered",
      "price": 2500000,
      "rating": 5,
      "review": "Great driver!"
    }
  ],
  "total_earnings": 15000000,
  "active_jobs": 2
}
```

---

### 9. Toggle Availability
**Endpoint:** `POST /api/toggle-availability`

**Request Body:**
```json
{
  "driver_id": 3,
  "available": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Availability set to Online",
  "status": "Online"
}
```

---

## 📊 Admin Operations APIs

### 10. Get All Requests
**Endpoint:** `GET /api/all-requests`

**Query Parameters:**
```
?status=Pending
?page=1
?limit=20
```

**Response (200 OK):**
```json
{
  "success": true,
  "requests": [
    {
      "id": 15,
      "farmer_name": "Alice",
      "driver_name": "John",
      "goods_type": "Maize",
      "pickup_location": "Morogoro",
      "destination": "Dar es Salaam",
      "status": "In Transit",
      "created_at": "2024-05-28T14:20:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "pages": 3
}
```

---

### 11. Get All Drivers
**Endpoint:** `GET /api/all-drivers`

**Response (200 OK):**
```json
{
  "success": true,
  "drivers": [
    {
      "id": 3,
      "name": "John",
      "phone": "0712345678",
      "availability": "Online",
      "total_jobs": 15,
      "completed_jobs": 14,
      "avg_rating": 4.8,
      "total_earnings": 25000000,
      "verified": true
    }
  ],
  "total": 8,
  "online_now": 5
}
```

---

### 12. Get Statistics
**Endpoint:** `GET /api/statistics`

**Response (200 OK):**
```json
{
  "success": true,
  "statistics": {
    "total_requests": 42,
    "pending_requests": 5,
    "delivered_requests": 31,
    "active_drivers": 5,
    "total_drivers": 8,
    "total_revenue": 125000000,
    "today_requests": 3,
    "average_delivery_time": 145
  }
}
```

---

### 13. Get Analytics Data
**Endpoint:** `GET /api/analytics`

**Response (200 OK):**
```json
{
  "success": true,
  "analytics": {
    "delivery_distribution": {
      "Pending": 5,
      "Accepted": 3,
      "In Transit": 2,
      "Delivered": 32
    },
    "daily_requests_7days": [
      {"date": "2024-05-22", "count": 2},
      {"date": "2024-05-23", "count": 5},
      {"date": "2024-05-24", "count": 3},
      {"date": "2024-05-25", "count": 6},
      {"date": "2024-05-26", "count": 4},
      {"date": "2024-05-27", "count": 8},
      {"date": "2024-05-28", "count": 14}
    ],
    "top_routes": [
      {
        "route": "Morogoro → Dar",
        "count": 12,
        "avg_time": 140
      }
    ]
  }
}
```

---

## 💰 Market Intelligence APIs (NEW)

### 14. Get Market Prices for Crop
**Endpoint:** `GET /api/market-prices/<crop>`

**Example:** `GET /api/market-prices/Maize`

**Response (200 OK):**
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

---

### 15. Estimate Profit
**Endpoint:** `POST /api/estimate-profit`

**Request Body:**
```json
{
  "crop_name": "Maize",
  "quantity": 500,
  "transport_cost": 35000,
  "destination_region": "Dar es Salaam"
}
```

**Response (200 OK):**
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

---

### 16. Find Best Market
**Endpoint:** `POST /api/best-market`

**Request Body:**
```json
{
  "crop_name": "Maize",
  "quantity": 500,
  "transport_cost_base": 35000
}
```

**Response (200 OK):**
```json
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
      "region": "Dodoma",
      "price": 92000,
      "profit": 44235000
    },
    {
      "region": "Mwanza",
      "price": 90000,
      "profit": 43555000
    },
    {
      "region": "Arusha",
      "price": 88000,
      "profit": 41875000
    }
  ]
}
```

---

### 17. Get Crop Prices Overview
**Endpoint:** `GET /api/crop-prices`

**Response (200 OK):**
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

---

### 18. Save Profit Estimate
**Endpoint:** `POST /api/save-profit-estimate`

**Request Body:**
```json
{
  "farmer_id": 1,
  "crop_name": "Maize",
  "quantity": 500,
  "transport_cost": 35000,
  "destination_region": "Dar es Salaam"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "estimate_id": 12,
  "message": "Profit estimate saved successfully",
  "profit_estimate": {
    "crop": "Maize",
    "quantity": 500,
    "estimated_profit": 45090000,
    "profit_margin": 94.9
  }
}
```

---

## 🔔 Notification APIs

### 19. Send Notification
**Endpoint:** `POST /api/send-notification`

**Request Body:**
```json
{
  "user_type": "farmer",
  "user_id": 1,
  "message": "Driver accepted your request!",
  "type": "job_accepted"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "notification_id": 34,
  "message": "Notification sent"
}
```

---

### 20. Get Notifications
**Endpoint:** `GET /api/notifications`

**Query Parameters:**
```
?user_type=farmer
?user_id=1
?unread=true    (optional)
```

**Response (200 OK):**
```json
{
  "success": true,
  "notifications": [
    {
      "id": 34,
      "message": "Driver John accepted your request",
      "type": "job_accepted",
      "read": false,
      "created_at": "2024-05-28T14:25:00Z"
    }
  ],
  "unread_count": 2
}
```

---

## 🎯 Tracking APIs

### 21. Update Tracking
**Endpoint:** `POST /api/update-tracking`

**Request Body:**
```json
{
  "request_id": 15,
  "latitude": -6.7924,
  "longitude": 39.2083,
  "status": "In Transit",
  "eta_minutes": 45
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Location updated"
}
```

---

### 22. Get Tracking Data
**Endpoint:** `GET /api/tracking/<request_id>`

**Response (200 OK):**
```json
{
  "success": true,
  "tracking": {
    "request_id": 15,
    "current_location": {
      "latitude": -6.7924,
      "longitude": 39.2083
    },
    "status": "In Transit",
    "eta_minutes": 45,
    "pickup_location": "Morogoro",
    "destination": "Dar es Salaam",
    "driver_name": "John",
    "driver_phone": "0712345678",
    "history": [
      {
        "timestamp": "2024-05-28T14:25:00Z",
        "latitude": -6.8100,
        "longitude": 39.1900,
        "status": "Accepted"
      }
    ]
  }
}
```

---

## 📋 Response Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Request successful |
| 201 | Created | New resource created |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal server error |

---

## 🔒 Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "error_code": "INVALID_INPUT"
}
```

---

## 📊 Common Errors

### Missing Required Field
```json
{
  "success": false,
  "error": "Missing required field: goods_type"
}
```

### Resource Not Found
```json
{
  "success": false,
  "error": "Request ID 999 not found"
}
```

### Invalid Status
```json
{
  "success": false,
  "error": "Invalid status. Must be: Accepted, In Transit, or Delivered"
}
```

---

## 🧪 Testing with cURL

### Example 1: Get Market Prices
```bash
curl http://localhost:5000/api/market-prices/Maize
```

### Example 2: Estimate Profit
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

### Example 3: Find Best Market
```bash
curl -X POST http://localhost:5000/api/best-market \
  -H "Content-Type: application/json" \
  -d '{
    "crop_name": "Tomatoes",
    "quantity": 200,
    "transport_cost_base": 35000
  }'
```

### Example 4: Submit Request
```bash
curl -X POST http://localhost:5000/api/submit-request \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": 1,
    "pickup_location": "Morogoro",
    "destination": "Dar es Salaam",
    "goods_type": "Maize",
    "quantity": 500,
    "pickup_time": "2024-05-28 08:00"
  }'
```

---

## 📚 Complete Endpoint Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/submit-request | Create new request |
| GET | /api/my-requests | Get farmer requests |
| GET | /api/request/<id> | Get request details |
| POST | /api/cancel-request | Cancel request |
| GET | /api/available-requests | Get jobs for driver |
| POST | /api/accept-request | Accept job |
| POST | /api/update-status | Update delivery status |
| GET | /api/my-jobs | Get driver jobs |
| POST | /api/toggle-availability | Set driver online/offline |
| GET | /api/all-requests | Admin view all |
| GET | /api/all-drivers | Admin view drivers |
| GET | /api/statistics | Admin statistics |
| GET | /api/analytics | Admin analytics |
| GET | /api/market-prices/<crop> | Market prices |
| POST | /api/estimate-profit | Calculate profit |
| POST | /api/best-market | Find best market |
| GET | /api/crop-prices | List crops |
| POST | /api/save-profit-estimate | Save estimate |
| POST | /api/send-notification | Create alert |
| GET | /api/notifications | Get alerts |
| POST | /api/update-tracking | Update location |
| GET | /api/tracking/<id> | Get tracking |

---

**API is fully functional and ready for integration!**
