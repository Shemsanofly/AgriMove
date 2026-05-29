# 🚀 AgriMove AI - Complete Access Guide

## ✅ System Requirements

- **Python 3.7+** (recommended 3.10 or higher)
- **pip** (Python package manager)
- **Browser** (Chrome, Firefox, Safari, Edge)
- **Windows/Mac/Linux**

## 📥 Step 1: Setup (First Time Only)

### Option A: Windows CMD

```bash
# Navigate to project folder
cd c:\Users\amins\Downloads\Hackathon\agrimove-ai

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; print('✓ Flask installed')"
```

### Option B: PowerShell

```powershell
Set-Location "c:\Users\amins\Downloads\Hackathon\agrimove-ai"

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Option C: macOS/Linux

```bash
cd ~/Downloads/Hackathon/agrimove-ai

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

---

## 🏃 Step 2: Run the Application

### Start the Server

```bash
# Make sure virtual environment is active
python app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

✅ **Server is running!** The database will auto-initialize with sample data.

---

## 🌐 Step 3: Access All Features

### 📌 **Main Access Points**

| Feature | URL | Purpose | Demo Action |
|---------|-----|---------|-------------|
| 🏠 **Home** | http://127.0.0.1:5000/ | Landing page & overview | Scroll, explore features |
| 👨‍🌾 **Farmer Dashboard** | http://127.0.0.1:5000/farmer | Submit transport requests | Fill form & submit |
| 🚗 **Driver Dashboard** | http://127.0.0.1:5000/driver | Accept & manage deliveries | Accept job → Start → Deliver |
| 👨‍💼 **Admin Dashboard** | http://127.0.0.1:5000/admin | System overview & management | View requests, search, toggle dark mode |
| 📊 **Analytics** | http://127.0.0.1:5000/admin/analytics | Charts & performance metrics | View live charts |

---

## 💡 Step 4: Demo Workflow

### **Quick Demo (2 minutes)**

**Step 1: Farmer Submits Request**
```
1. Go to http://127.0.0.1:5000/farmer
2. Fill the form:
   - Farmer Name: "John Doe"
   - Phone: "+233555123456"
   - Pickup Location: "Kumasi Village"
   - Destination: "Central Market"
   - Goods Type: "Tomatoes"
   - Quantity: "50 crates"
3. Click "Request Transport"
4. ✅ Success message appears
5. Request appears in table with "Pending" status
```

**Step 2: Admin Views Request**
```
1. Go to http://127.0.0.1:5000/admin
2. Scroll down to "All Requests" table
3. See the new request with status "Pending"
4. View stats: "Total Requests: 1"
5. Toggle Dark Mode (🌙 button)
```

**Step 3: Driver Accepts Job**
```
1. Go to http://127.0.0.1:5000/driver
2. See request in "Available Requests" table
3. Click "Accept Job" button
4. Status changes to "Accepted"
5. Driver is assigned automatically
```

**Step 4: Driver Starts Delivery**
```
1. Still on http://127.0.0.1:5000/driver
2. Request now shows "Start Delivery" button
3. Click "Start Delivery"
4. Status changes to "In Transit" ✅
```

**Step 5: Driver Completes Delivery**
```
1. On driver dashboard
2. Request shows "Mark Delivered" button
3. Click "Mark Delivered"
4. Status changes to "Delivered" ✅
5. Driver becomes "available" again
```

**Step 6: Check Analytics**
```
1. Go to http://127.0.0.1:5000/admin/analytics
2. View charts showing:
   - Delivery status distribution (pie chart)
   - 7-day request trend (line chart)
   - Completion rate (progress bar)
   - Average delivery time (ETA)
```

---

## 🔌 Step 5: Access API Endpoints (Optional)

### **Programmatic Access via cURL or Browser**

#### Get All Requests
```bash
curl http://127.0.0.1:5000/api/requests
```

#### Get All Drivers
```bash
curl http://127.0.0.1:5000/api/drivers
```

#### Get Statistics
```bash
curl http://127.0.0.1:5000/api/statistics
```

#### Get Analytics Data
```bash
curl http://127.0.0.1:5000/api/analytics
```

Or simply open these URLs in your browser:
- http://127.0.0.1:5000/api/requests
- http://127.0.0.1:5000/api/drivers
- http://127.0.0.1:5000/api/statistics
- http://127.0.0.1:5000/api/analytics

---

## 🎨 Step 6: Explore Advanced Features

### **Dark Mode**
```
1. Go to http://127.0.0.1:5000/admin
2. Click "🌙 Dark Mode" button
3. Entire app switches to dark theme
4. Theme persists across page reloads (saved in browser)
```

### **Search & Filter**
```
1. Go to http://127.0.0.1:5000/admin
2. Type in "Quick Search" box (e.g., farmer name)
3. Use checkboxes to filter by status
4. Table updates in real-time
```

### **Live Data**
```
1. Create multiple requests on farmer dashboard
2. View them on admin/driver dashboards
3. Analytics charts update automatically
4. New notifications appear in activity log
```

---

## 🛑 Step 7: Stop the Server

### **To Stop the App**

**Press in Terminal:**
```
Ctrl + C
```

Or kill the process:
```bash
# Windows (PowerShell)
Get-Process python | Stop-Process

# macOS/Linux
pkill -f "python app.py"
```

---

## 📊 Database Info

### **Auto-Generated on First Run**

The `database.db` file includes:
- ✅ 4 Sample Drivers (seeded automatically)
- ✅ Farmers table (created on first request)
- ✅ Requests table (populated as you submit)
- ✅ Notifications table (activity log)

### **Reset Database** (Start Fresh)

```bash
# Delete database
rm database.db

# Or simply delete via file explorer:
# c:\Users\amins\Downloads\Hackathon\agrimove-ai\database.db

# Restart app (database auto-recreates)
python app.py
```

---

## 🐛 Troubleshooting

### **Problem: "Port 5000 already in use"**
```bash
# Kill existing Flask process
Get-Process python | Stop-Process  # Windows

# Or use a different port
FLASK_ENV=development FLASK_DEBUG=1 python -c "from app import app; app.run(port=5001)"
```

### **Problem: "ModuleNotFoundError: No module named 'flask'"**
```bash
# Virtual environment not activated
.venv\Scripts\activate  # Windows

source .venv/bin/activate  # Mac/Linux

# Then reinstall
pip install -r requirements.txt
```

### **Problem: "Database is locked"**
```bash
# Close any other terminal windows running the app
# Delete database.db and restart
rm database.db
python app.py
```

### **Problem: "Cannot find Python"**
```bash
# Check Python installation
python --version

# If not found, install Python 3.10+
# Then add to PATH and restart terminal
```

---

## 📱 Responsive Design Testing

### **Test on Different Screen Sizes**

```
1. Open Chrome DevTools (F12)
2. Click device toggle (Ctrl+Shift+M)
3. Select device:
   - iPhone SE
   - iPad
   - Desktop
4. Sidebar collapses to hamburger menu
5. All features work on mobile
```

---

## 🎯 Complete Feature Checklist

- ✅ Landing page with hero section
- ✅ Farmer dashboard (submit requests)
- ✅ Driver dashboard (accept jobs, update status)
- ✅ Admin dashboard (system overview)
- ✅ Analytics with live charts
- ✅ Search & filter functionality
- ✅ Dark/light mode toggle
- ✅ REST API endpoints (JSON)
- ✅ Responsive design (mobile-friendly)
- ✅ Auto-database initialization
- ✅ Sample driver data seeding
- ✅ Real-time notifications
- ✅ AI route optimization simulation
- ✅ ETA calculation simulation
- ✅ Status workflow management
- ✅ Driver availability tracking
- ✅ Request history
- ✅ Activity log

---

## 📞 Support

If you encounter any issues:

1. **Check terminal output** for error messages
2. **Verify Python version**: `python --version`
3. **Verify Flask installed**: `python -c "import flask"`
4. **Check if database exists**: Look in project folder
5. **Restart the app**: Stop (Ctrl+C) and start again

---

## 🎓 Learning Resources

### **Modify the App**

**Add a new route** in `app.py`:
```python
@app.route("/new-page")
def new_page():
    return render_template("new_page.html")
```

**Add new styles** in `static/css/styles.css`:
```css
.my-class {
  color: var(--green);
  padding: 20px;
}
```

**Add new functionality** in `static/js/main.js`:
```javascript
document.addEventListener("DOMContentLoaded", () => {
  console.log("Page loaded!");
});
```

---

## 🚀 Ready to Demo!

Your AgriMove AI project is **fully functional** and ready to showcase. 

**Quick Start Command:**
```bash
cd c:\Users\amins\Downloads\Hackathon\agrimove-ai
python app.py
```

Then visit: **http://127.0.0.1:5000**

**Enjoy your startup MVP! 🎉**
