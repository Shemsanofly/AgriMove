# AgriMove AI

AgriMove AI is a smart rural logistics platform that connects farmers with transport drivers to move agricultural products from villages to markets. This full-stack prototype includes farmer dashboards, driver management, an admin panel with real-time analytics, and advanced logistics features.

## 🎯 Features

### Farmer Portal
- Submit transport requests with pickup/destination details
- Real-time request status tracking
- Notifications for driver assignments and delivery updates
- Request history and delivery confirmations

### Driver Dashboard
- View available transport requests
- Accept jobs with one click
- Update delivery status (Accepted → In Transit → Delivered)
- Automatic ETA calculations
- Driver availability management

### Admin Dashboard
- Real-time overview of all requests and drivers
- Advanced search and filtering
- Request status distribution by driver
- Driver roster with availability status
- Activity log with timestamp notifications

### Analytics & Insights
- Interactive charts (delivery distribution, 7-day trends)
- Completion rate tracking with visual progress bars
- Average ETA metrics
- Real-time data refresh (30-second intervals)
- Export-ready analytics data

### Advanced Features
- **AI Market Intelligence Dashboard** — Smart predictive models showing best locations to sell, demand hotspots, projected price shifts, and logistics routing.
- **USSD Simulator Sandbox** — Virtual Nokia-style smartphone mockup dialing `*123#`, running simulated Africa's Talking USSD API logic, and testing numeric menu navigations.
- **Simulated SMS Inbox** — Real-time SMS logger displaying alerts for transport confirmation, delivery arrival, and buyer offers.
- **Dark/Light Mode Toggle** — Global, persistent theme layout preference syncing across dashboards.
- **Search & Filter** — Live requests search filtering by ID, crop name, status, or driver name.
- **Dynamic GPS Journey Simulation** — Polled coordinates updating real-time truck markers and journey timelines.
- **Responsive Layout** — Clean CSS styling optimized for rural phone browsers and widescreen admin monitors.
- **REST APIs** — JSON and form-encoded endpoints for external integrations.

## Tech Stack

- **Frontend**: HTML, CSS (custom, no Bootstrap), Vanilla JavaScript, Chart.js
- **Backend**: Python Flask
- **Database**: SQLite
- **Charts**: Chart.js (via CDN)

## Project Structure

```
agrimove-ai/
  app.py                           # Flask app with all routes & API
  database.db                      # SQLite database (auto-created)
  requirements.txt                 # Python dependencies
  README.md                        # Documentation
  static/
    css/
      styles.css                  # All styles (light/dark mode)
    js/
      main.js                     # Frontend interactions
  templates/
    index.html                    # Landing page
    dashboard_base.html           # Shared dashboard layout
    farmer_dashboard.html         # Farmer portal
    driver_dashboard.html         # Driver portal
    admin_dashboard.html          # Admin main dashboard
    admin_analytics.html          # Analytics & reports
```

## Installation & Setup

### 1. Clone or Download
```bash
cd agrimove-ai
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# or
source .venv/bin/activate       # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Africa's Talking Sandbox
Set your Africa's Talking sandbox credentials as environment variables. Do not paste API keys into code.

Windows PowerShell:
```powershell
$env:AT_USERNAME="sandbox"
$env:AT_API_KEY="your_new_sandbox_api_key"
```

Expose Flask with a public HTTPS tunnel, then use the tunnel URL as your USSD callback:
```text
https://your-public-url/api/ussd
```

You can verify the integration mode at:
```text
http://127.0.0.1:5000/api/africas-talking/status
```

### 5. Run the Application
```bash
python app.py
```

The app will start at: `http://127.0.0.1:5000`

## 🚀 Access Points

| Role | URL | Purpose |
|------|-----|---------|
| **Public** | http://127.0.0.1:5000/ | Landing page with feature overview |
| **Farmer** | http://127.0.0.1:5000/farmer | Submit requests & track deliveries |
| **AI Insights** | http://127.0.0.1:5000/market/insights | Market demand predictive analytics |
| **USSD Simulator** | http://127.0.0.1:5000/ussd-simulator | Dial *123# and test phone sandbox |
| **Driver** | http://127.0.0.1:5000/driver | Accept jobs & manage deliveries |
| **Admin** | http://127.0.0.1:5000/admin | Price roster, buyer verification, orders |
| **Analytics** | http://127.0.0.1:5000/admin/analytics | Advanced interactive performance charts |

## 📊 API Endpoints (JSON)

### GET `/api/requests`
Returns all requests with farmer/driver details.

```bash
curl http://127.0.0.1:5000/api/requests
```

### GET `/api/drivers`
Returns all drivers and availability status.

```bash
curl http://127.0.0.1:5000/api/drivers
```

### GET `/api/statistics`
Returns dashboard statistics (totals, pending, delivered, etc.).

```bash
curl http://127.0.0.1:5000/api/statistics
```

### GET `/api/analytics`
Returns analytics data for charts (status distribution, daily trends).

```bash
curl http://127.0.0.1:5000/api/analytics
```

## 🎨 UI/UX Highlights

### Design System
- **Color Palette**: Green (#2f7d32), Gold (#f2c14e), Dark accents
- **Typography**: Inter font, 3-level hierarchy
- **Spacing**: Consistent 16px/18px grid
- **Animations**: Smooth transitions, pulse effects, fade-in reveals

### Dark Mode
- Toggle via button on admin dashboard
- Automatically saved to browser localStorage
- Smooth color transitions
- Optimized contrast for accessibility

### Responsive
- Mobile-first approach
- Works seamlessly on phones, tablets, desktops
- Sidebar collapses to hamburger menu on small screens
- Touch-friendly buttons and inputs

### Performance
- Lightweight (~50KB CSS, 10KB JS)
- No heavy dependencies (except Chart.js via CDN)
- Database queries optimized with proper indexing
- Lazy loading for analytics charts

## 🧪 Demo Data

The database automatically seeds with:
- **4 Sample Drivers**: Ready for job assignment
- **Status Workflow**: Pending → Accepted → In Transit → Delivered
- **Auto-assignment**: First driver match based on distance simulation
- **ETA Calculation**: Realistic estimated delivery times

## 🔌 Future Integrations

### SMS Notifications (Africa's Talking)
The `dispatch_notification()` function in `app.py` is a hook ready for:
```python
def dispatch_notification(conn, message, request_id=None):
    # TODO: Integrate Africa's Talking SMS API
    # Example: client.send_sms(phone, message)
    create_notification(conn, message, request_id)
```

### Real GPS Tracking
Replace simulation markers with actual GPS coordinates from driver devices.

### Payment Integration
Add Stripe/PayPal for farmer-to-driver payment workflow.

## 📋 Hackathon Checklist

✅ Landing page with modern hero & features
✅ Farmer dashboard with request submission
✅ Driver dashboard with job management
✅ Admin dashboard with system overview
✅ Analytics with live charts
✅ Dark/light mode toggle
✅ Search & filter functionality
✅ Responsive on all devices
✅ REST API for integrations
✅ Professional, startup-quality UI
✅ Clean, commented code
✅ Database with proper schema
✅ Easy deployment (single `python app.py`)

## 💡 Tips for Presentation

1. **Start at landing page** (`/`) to show the vision
2. **Submit a request** on Farmer dashboard to create live data
3. **Switch to Driver** dashboard, accept a job, start delivery
4. **Show Admin dashboard** with the updated request status
5. **Open Analytics** tab to show charts updating in real-time
6. **Toggle dark mode** to showcase theme flexibility
7. **Open DevTools** to show network calls to `/api/*` endpoints
8. **Mention SMS integration hooks** for future scalability

## 📝 Notes

- Database resets on app restart (auto-init on startup)
- Driver sample data reseeds if table is empty
- All timestamps stored in UTC ISO format
- Notifications are simulated; ready for real SMS integration
- AI route optimization uses random distance simulation

---

**Built for AgriMove AI Hackathon** 🚀
**Smart logistics for rural Africa**
