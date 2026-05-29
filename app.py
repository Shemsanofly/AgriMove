import os
import random
import sqlite3
from datetime import datetime, timedelta
import json

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "agrimove-ai-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

STATUS_FLOW = ["Pending", "Accepted", "In Transit", "Delivered"]

CROPS = ["Maize", "Tomatoes", "Beans", "Rice", "Cabbage", "Potatoes"]

PICKUP_LOCATIONS = [
    "Morogoro Farm Gate",
    "Mvomero Cooperative",
    "Ifakara Collection Point",
    "Moshi Highland Farms",
    "Nakuru Farmers Hub",
    "Eldoret Grain Depot",
    "Kumasi Produce Yard",
    "Ibadan Agro Hub",
]

MARKET_REGIONS = [
    "Dar es Salaam",
    "Dodoma",
    "Arusha",
    "Mwanza",
    "Nairobi",
    "Mombasa",
    "Kampala",
    "Kigali",
    "Accra",
    "Kumasi",
    "Lagos",
    "Ibadan",
]

LOCATION_COORDS = {
    "Morogoro Farm Gate": (-6.8200, 37.6600),
    "Mvomero Cooperative": (-6.3000, 37.4500),
    "Ifakara Collection Point": (-8.1333, 36.6833),
    "Moshi Highland Farms": (-3.3349, 37.3404),
    "Nakuru Farmers Hub": (-0.3031, 36.0800),
    "Eldoret Grain Depot": (0.5143, 35.2698),
    "Kumasi Produce Yard": (6.6666, -1.6163),
    "Ibadan Agro Hub": (7.3775, 3.9470),
    "Dar es Salaam": (-6.7924, 39.2729),
    "Dodoma": (-6.1630, 35.7516),
    "Arusha": (-3.3671, 36.6822),
    "Mwanza": (-2.5164, 32.9018),
    "Nairobi": (-1.2921, 36.8219),
    "Mombasa": (-4.0435, 39.6682),
    "Kampala": (0.3476, 32.5825),
    "Kigali": (-1.9441, 30.0619),
    "Accra": (5.6037, -0.1870),
    "Kumasi": (6.6885, -1.6244),
    "Lagos": (6.5244, 3.3792),
    "Ibadan": (7.3775, 3.9470),
}


# ============== AFRICA'S TALKING SDK INITIALIZATION ==============
AT_USERNAME = os.environ.get("AT_USERNAME", "sandbox")
AT_API_KEY = os.environ.get("AT_API_KEY")

sms_client = None
sms_status = {
    "enabled": False,
    "username": AT_USERNAME,
    "mode": "simulated",
    "message": "AT_API_KEY is not set. Using local simulated notifications.",
}
if AT_API_KEY:
    try:
        import africastalking
        africastalking.initialize(AT_USERNAME, AT_API_KEY)
        sms_client = africastalking.SMS
        sms_status.update({
            "enabled": True,
            "mode": "africas_talking",
            "message": "Africa's Talking SMS SDK initialized successfully.",
        })
        print("Africa's Talking SMS SDK initialized successfully.")
    except ImportError:
        sms_status["message"] = "africastalking module not found. Run 'pip install -r requirements.txt'. Falling back to simulated notifications."
        print("africastalking module not found. Run 'pip install africastalking'. Falling back to simulated notifications.")
    except Exception as e:
        sms_status["message"] = f"Africa's Talking SDK could not initialize: {e}"
        print(f"Africa's Talking SDK could not initialize: {e}")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            rating REAL DEFAULT 5.0,
            total_requests INTEGER DEFAULT 0,
            total_delivered INTEGER DEFAULT 0,
            member_since TEXT NOT NULL,
            points INTEGER DEFAULT 0
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            availability TEXT NOT NULL,
            rating REAL DEFAULT 5.0,
            total_deliveries INTEGER DEFAULT 0,
            completed_today INTEGER DEFAULT 0,
            earnings REAL DEFAULT 0.0,
            vehicle_type TEXT DEFAULT 'truck',
            points INTEGER DEFAULT 0
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            pickup_location TEXT NOT NULL,
            destination TEXT NOT NULL,
            goods_type TEXT NOT NULL,
            quantity TEXT NOT NULL,
            status TEXT NOT NULL,
            driver_id INTEGER,
            eta_minutes INTEGER,
            actual_time INTEGER,
            distance_km REAL,
            price REAL,
            rating INTEGER,
            review TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (farmer_id) REFERENCES farmers (id),
            FOREIGN KEY (driver_id) REFERENCES drivers (id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            created_at TEXT NOT NULL,
            FOREIGN KEY (request_id) REFERENCES requests (id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            latitude REAL,
            longitude REAL,
            status TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (request_id) REFERENCES requests (id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            region TEXT NOT NULL,
            price REAL NOT NULL,
            demand_level TEXT DEFAULT 'Medium',
            trend TEXT DEFAULT 'Stable',
            updated_at TEXT NOT NULL,
            UNIQUE(crop_name, region)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS profit_estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            crop_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            transport_cost REAL NOT NULL,
            source_region TEXT,
            destination_region TEXT,
            estimated_revenue REAL,
            estimated_profit REAL,
            profit_margin REAL,
            recommended_market TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (farmer_id) REFERENCES farmers (id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS buyer_offers (
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
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trusted_buyers (
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
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS price_alerts (
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
        )
        """
    )
    conn.commit()
    conn.close()


def seed_drivers():
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM drivers").fetchone()[0]
    if count == 0:
        drivers = [
            ("Kwame Boateng", "+233 555 210 120", "available", 4.8, 156, 12, 2400.50, "truck"),
            ("Amina Njeri", "+254 712 490 330", "available", 4.9, 203, 8, 3200.75, "van"),
            ("Tunde Okafor", "+234 802 301 556", "available", 4.7, 134, 5, 1950.25, "truck"),
            ("Zola Mbeki", "+27 712 555 010", "available", 4.6, 98, 3, 1450.00, "pickup"),
        ]
        conn.executemany(
            """INSERT INTO drivers 
            (name, phone, availability, rating, total_deliveries, completed_today, earnings, vehicle_type) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
            drivers
        )
        conn.commit()
    conn.close()


def seed_market_prices():
    """Seed market prices for different crops and regions"""
    conn = get_db_connection()
    crop_base_prices = {
        "Maize": 95000,
        "Tomatoes": 150000,
        "Beans": 180000,
        "Rice": 200000,
        "Cabbage": 45000,
        "Potatoes": 65000,
    }
    region_profiles = [
        ("Dar es Salaam", 1.00, "High", "Stable"),
        ("Dodoma", 0.97, "High", "Rising"),
        ("Arusha", 0.93, "Medium", "Rising"),
        ("Mwanza", 0.95, "Medium", "Stable"),
        ("Nairobi", 1.18, "High", "Rising"),
        ("Mombasa", 1.10, "High", "Stable"),
        ("Kampala", 1.04, "Medium", "Rising"),
        ("Kigali", 1.12, "High", "Stable"),
        ("Accra", 1.20, "High", "Rising"),
        ("Kumasi", 1.08, "Medium", "Stable"),
        ("Lagos", 1.26, "High", "Rising"),
        ("Ibadan", 1.14, "Medium", "Falling"),
    ]

    for crop, base_price in crop_base_prices.items():
        for region, multiplier, demand, trend in region_profiles:
            price = round(base_price * multiplier, -2)
            conn.execute(
                """INSERT OR IGNORE INTO market_prices
                   (crop_name, region, price, demand_level, trend, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (crop, region, price, demand, trend, datetime.now().isoformat())
            )
    conn.commit()
    conn.close()


def seed_buyers():
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM trusted_buyers").fetchone()[0]
    if count == 0:
        buyers = [
            (1, "Salim Corp", "+255 712 999 111", "Pending", 4.5, 34),
            (2, "Mwangi Traders", "+254 722 888 222", "Verified", 4.8, 120),
            (3, "Dodoma Harvests", "+255 688 111 222", "Pending", 4.2, 12),
            (4, "Kigali Wholesalers", "+250 788 333 444", "Verified", 4.9, 210),
        ]
        for b_id, name, phone, status, rating, purchases in buyers:
            conn.execute(
                """INSERT OR IGNORE INTO trusted_buyers 
                (buyer_id, buyer_name, phone, verification_status, rating, total_purchases, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (b_id, name, phone, status, rating, purchases, datetime.now().isoformat())
            )
        conn.commit()
    conn.close()


def calculate_price(distance_km):
    """Dynamic pricing based on distance"""
    base_price = 5.0
    per_km = 2.5
    return round(base_price + (distance_km * per_km), 2)


def estimate_profit(crop_name, quantity, transport_cost, source_region, destination_region, conn=None):
    """Calculate profit estimate for a crop shipment"""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    
    # Get destination market price
    dest_price = conn.execute(
        "SELECT price FROM market_prices WHERE crop_name = ? AND region = ?",
        (crop_name, destination_region)
    ).fetchone()
    
    if not dest_price:
        if should_close:
            conn.close()
        return None
    
    market_price_per_unit = dest_price[0]
    estimated_revenue = quantity * market_price_per_unit
    
    # Calculate costs (including transport + 5% loss due to spoilage/handling)
    total_costs = transport_cost + (estimated_revenue * 0.05)
    estimated_profit = estimated_revenue - total_costs
    profit_margin = (estimated_profit / estimated_revenue * 100) if estimated_revenue > 0 else 0
    
    if should_close:
        conn.close()
    
    return {
        'estimated_revenue': round(estimated_revenue, 2),
        'estimated_profit': round(estimated_profit, 2),
        'profit_margin': round(profit_margin, 1),
        'total_costs': round(total_costs, 2),
        'market_price_per_unit': market_price_per_unit
    }


def get_best_market(crop_name, quantity, transport_costs_by_region, conn=None):
    """Recommend best market destination for maximum profit"""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    
    # Get all regions with this crop
    regions = conn.execute(
        "SELECT DISTINCT region FROM market_prices WHERE crop_name = ?",
        (crop_name,)
    ).fetchall()
    
    best_market = None
    max_profit = -float('inf')
    
    for region_row in regions:
        region = region_row[0]
        transport_cost = transport_costs_by_region.get(region, 50000)  # Default transport cost
        
        estimate = estimate_profit(crop_name, quantity, transport_cost, "Local", region, conn)
        if estimate and estimate['estimated_profit'] > max_profit:
            max_profit = estimate['estimated_profit']
            best_market = {
                'region': region,
                'profit': estimate['estimated_profit'],
                'revenue': estimate['estimated_revenue'],
                'margin': estimate['profit_margin']
            }
    
    if should_close:
        conn.close()
    
    return best_market


def dispatch_notification(conn, message, request_id=None):
    # Log inside local notifications database (for simulator view)
    create_notification(conn, message, request_id)
    
    # If Africa's Talking API client is set, send a real SMS
    if sms_client and request_id:
        try:
            req = conn.execute(
                """SELECT f.phone FROM requests r 
                   JOIN farmers f ON r.farmer_id = f.id 
                   WHERE r.id = ?""",
                (request_id,)
            ).fetchone()
            if req and req["phone"]:
                # Send SMS via AT client
                response = sms_client.send(message, [req["phone"]])
                print(f"AT SMS Sent successfully to {req['phone']}: {response}")
        except Exception as e:
            print(f"Error sending SMS via Africa's Talking SDK: {e}")


@app.get("/api/africas-talking/status")
def africas_talking_status():
    """Return current Africa's Talking integration mode without exposing secrets."""
    return jsonify({
        "sms_enabled": sms_status["enabled"],
        "username": sms_status["username"],
        "mode": sms_status["mode"],
        "message": sms_status["message"],
        "ussd_callback": url_for("api_ussd", _external=True),
    })


def assign_driver(conn):
    drivers = conn.execute(
        "SELECT * FROM drivers WHERE availability = 'available'"
    ).fetchall()
    if not drivers:
        return None, None
    distances = {driver["id"]: random.randint(6, 45) for driver in drivers}
    selected = min(drivers, key=lambda driver: distances[driver["id"]])
    eta = distances[selected["id"]] * random.randint(2, 4) + random.randint(12, 28)
    return selected, eta


def summarize_statuses(requests_rows):
    counts = {status: 0 for status in STATUS_FLOW}
    for row in requests_rows:
        if row["status"] in counts:
            counts[row["status"]] += 1
    return counts


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/farmer", methods=["GET", "POST"])
def farmer_dashboard():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        pickup = request.form.get("pickup_location", "").strip()
        destination = request.form.get("destination", "").strip()
        goods_type = request.form.get("goods_type", "").strip()
        quantity = request.form.get("quantity", "").strip()

        conn = get_db_connection()
        farmer = conn.execute(
            "SELECT id FROM farmers WHERE phone = ?", (phone,)
        ).fetchone()
        if farmer:
            farmer_id = farmer["id"]
        else:
            farmer_id = conn.execute(
                "INSERT INTO farmers (name, phone, member_since) VALUES (?, ?, ?)",
                (name, phone, datetime.utcnow().isoformat(timespec="seconds")),
            ).lastrowid

        driver, eta = assign_driver(conn)
        driver_id = driver["id"] if driver else None
        status = "Pending"

        if driver_id:
            conn.execute(
                "UPDATE drivers SET availability = 'busy' WHERE id = ?", (driver_id,)
            )

        request_id = conn.execute(
            """
            INSERT INTO requests (
                farmer_id, pickup_location, destination, goods_type, quantity,
                status, driver_id, eta_minutes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                farmer_id,
                pickup,
                destination,
                goods_type,
                quantity,
                status,
                driver_id,
                eta,
                datetime.utcnow().isoformat(timespec="seconds"),
            ),
        ).lastrowid

        if driver_id:
            dispatch_notification(
                conn,
                f"Driver assigned successfully. Estimated delivery time: {eta} mins.",
                request_id,
            )
        else:
            dispatch_notification(
                conn,
                "Request received. Searching for available drivers.",
                request_id,
            )

        dispatch_notification(conn, "AI Route Optimization Active.", request_id)

        conn.commit()
        conn.close()

        flash("Transport request submitted successfully.", "success")
        return redirect(url_for("farmer_dashboard"))

    conn = get_db_connection()
    requests_rows = conn.execute(
        """
        SELECT r.*, f.name AS farmer_name, f.phone AS farmer_phone,
               d.name AS driver_name, d.phone AS driver_phone
        FROM requests r
        JOIN farmers f ON r.farmer_id = f.id
        LEFT JOIN drivers d ON r.driver_id = d.id
        ORDER BY r.id DESC
        """
    ).fetchall()
    notifications = conn.execute(
        "SELECT * FROM notifications ORDER BY id DESC LIMIT 6"
    ).fetchall()
    counts = summarize_statuses(requests_rows)
    latest = requests_rows[0] if requests_rows else None
    conn.close()

    return render_template(
        "farmer_dashboard.html",
        active="farmer",
        heading="Farmer Dashboard",
        subheading="Request transport and track the movement of your harvest.",
        requests=requests_rows,
        notifications=notifications,
        counts=counts,
        latest=latest,
        pickup_locations=PICKUP_LOCATIONS,
        destination_regions=MARKET_REGIONS,
        crops=CROPS,
    )


@app.route("/driver")
def driver_dashboard():
    conn = get_db_connection()
    requests_rows = conn.execute(
        """
        SELECT r.*, f.name AS farmer_name, f.phone AS farmer_phone,
               d.name AS driver_name, d.phone AS driver_phone
        FROM requests r
        JOIN farmers f ON r.farmer_id = f.id
        LEFT JOIN drivers d ON r.driver_id = d.id
        ORDER BY r.id DESC
        """
    ).fetchall()
    notifications = conn.execute(
        "SELECT * FROM notifications ORDER BY id DESC LIMIT 6"
    ).fetchall()
    drivers = conn.execute("SELECT * FROM drivers ORDER BY name").fetchall()
    counts = summarize_statuses(requests_rows)
    available_drivers = len(
        [driver for driver in drivers if driver["availability"] == "available"]
    )
    busy_drivers = len(drivers) - available_drivers
    conn.close()

    return render_template(
        "driver_dashboard.html",
        active="driver",
        heading="Driver Dashboard",
        subheading="Accept jobs, manage delivery progress, and update statuses.",
        requests=requests_rows,
        notifications=notifications,
        counts=counts,
        drivers=drivers,
        available_drivers=available_drivers,
        busy_drivers=busy_drivers,
    )


@app.post("/driver/accept/<int:request_id>")
def accept_job(request_id):
    conn = get_db_connection()
    req = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not req:
        conn.close()
        abort(404)

    driver_id = req["driver_id"]
    if driver_id is None:
        driver, eta = assign_driver(conn)
        if driver:
            driver_id = driver["id"]
            conn.execute(
                "UPDATE requests SET driver_id = ?, eta_minutes = ? WHERE id = ?",
                (driver_id, eta, request_id),
            )
            conn.execute(
                "UPDATE drivers SET availability = 'busy' WHERE id = ?", (driver_id,)
            )
            dispatch_notification(
                conn,
                f"Driver assigned successfully. Estimated delivery time: {eta} mins.",
                request_id,
            )

    conn.execute(
        "UPDATE requests SET status = 'Accepted' WHERE id = ?", (request_id,)
    )
    dispatch_notification(conn, "Driver assigned successfully.", request_id)
    conn.commit()
    conn.close()
    flash("Job accepted successfully.", "success")
    return redirect(url_for("driver_dashboard"))


@app.post("/driver/start/<int:request_id>")
def start_delivery(request_id):
    conn = get_db_connection()
    req = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not req:
        conn.close()
        abort(404)

    conn.execute(
        "UPDATE requests SET status = 'In Transit' WHERE id = ?", (request_id,)
    )
    dispatch_notification(conn, "Your goods are on the way.", request_id)
    conn.commit()
    conn.close()
    flash("Delivery started.", "success")
    return redirect(url_for("driver_dashboard"))


@app.post("/driver/deliver/<int:request_id>")
def mark_delivered(request_id):
    conn = get_db_connection()
    req = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not req:
        conn.close()
        abort(404)

    conn.execute(
        "UPDATE requests SET status = 'Delivered' WHERE id = ?", (request_id,)
    )
    if req["driver_id"]:
        conn.execute(
            "UPDATE drivers SET availability = 'available' WHERE id = ?",
            (req["driver_id"],),
        )
    dispatch_notification(conn, "Delivery completed.", request_id)
    conn.commit()
    conn.close()
    flash("Delivery marked as completed.", "success")
    return redirect(url_for("driver_dashboard"))


init_db()
seed_drivers()
seed_market_prices()
seed_buyers()


# ============== REST API ENDPOINTS ==============


@app.get("/api/requests")
def api_requests():
    """Return all requests as JSON for API/dashboard use."""
    conn = get_db_connection()
    requests_rows = conn.execute(
        """
        SELECT r.*, f.name AS farmer_name, f.phone AS farmer_phone,
               d.name AS driver_name, d.phone AS driver_phone
        FROM requests r
        JOIN farmers f ON r.farmer_id = f.id
        LEFT JOIN drivers d ON r.driver_id = d.id
        ORDER BY r.id DESC
        """
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in requests_rows])


@app.get("/api/drivers")
def api_drivers():
    """Return all drivers as JSON."""
    conn = get_db_connection()
    drivers = conn.execute("SELECT * FROM drivers ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(row) for row in drivers])


@app.get("/api/statistics")
def api_statistics():
    """Return dashboard statistics as JSON."""
    conn = get_db_connection()
    requests_rows = conn.execute(
        "SELECT * FROM requests ORDER BY created_at DESC"
    ).fetchall()
    drivers = conn.execute("SELECT * FROM drivers").fetchall()
    conn.close()

    counts = summarize_statuses(requests_rows)
    active_drivers = len(
        [d for d in drivers if d["availability"] == "available"]
    )

    return jsonify(
        {
            "total_requests": len(requests_rows),
            "pending": counts["Pending"],
            "accepted": counts["Accepted"],
            "in_transit": counts["In Transit"],
            "delivered": counts["Delivered"],
            "active_drivers": active_drivers,
            "total_drivers": len(drivers),
        }
    )


@app.get("/api/analytics")
def api_analytics():
    """Return comprehensive analytics data for advanced charts."""
    conn = get_db_connection()
    requests_rows = conn.execute(
        "SELECT status, created_at FROM requests ORDER BY created_at"
    ).fetchall()
    
    # Group by status
    by_status = summarize_statuses(requests_rows)

    # Calculate daily trend (last 7 days)
    daily_data = {}
    for row in requests_rows:
        date = row["created_at"][:10]
        daily_data[date] = daily_data.get(date, 0) + 1

    sorted_daily = sorted(daily_data.items())[-7:]
    
    # 1. Crop Demand data for Demand Trends chart
    demand_data = conn.execute(
        """SELECT crop_name, 
                  SUM(CASE WHEN demand_level = 'High' THEN 3 WHEN demand_level = 'Medium' THEN 2 ELSE 1 END) as demand_score 
           FROM market_prices GROUP BY crop_name"""
    ).fetchall()
    
    # 2. Market Activity prices range comparison
    price_spread = conn.execute(
        "SELECT crop_name, AVG(price) as avg_price FROM market_prices GROUP BY crop_name"
    ).fetchall()
    
    # 3. Delivery Performance (driver completed vs ratings)
    driver_perf = conn.execute(
        "SELECT name, rating, total_deliveries FROM drivers ORDER BY total_deliveries DESC LIMIT 6"
    ).fetchall()
    
    conn.close()

    return jsonify(
        {
            "by_status": by_status,
            "daily_trend": [{"date": d[0], "count": d[1]} for d in sorted_daily],
            "crop_demand": [{"crop": d["crop_name"], "score": d["demand_score"]} for d in demand_data],
            "price_spread": [{"crop": p["crop_name"], "avg_price": p["avg_price"]} for p in price_spread],
            "driver_performance": [{"name": dp["name"], "rating": dp["rating"], "deliveries": dp["total_deliveries"]} for dp in driver_perf]
        }
    )


# ============== ADVANCED FEATURES ==============


@app.get("/profile/driver/<int:driver_id>")
def driver_profile(driver_id):
    """Driver profile with stats and ratings"""
    conn = get_db_connection()
    driver = conn.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,)).fetchone()
    if not driver:
        abort(404)
    
    requests = conn.execute(
        "SELECT * FROM requests WHERE driver_id = ? ORDER BY id DESC LIMIT 10",
        (driver_id,)
    ).fetchall()
    conn.close()
    
    return render_template(
        "driver_profile.html",
        driver=driver,
        requests=requests,
        badges=get_driver_badges(driver)
    )


@app.get("/profile/farmer/<int:farmer_id>")
def farmer_profile(farmer_id):
    """Farmer profile with stats and ratings"""
    conn = get_db_connection()
    farmer = conn.execute("SELECT * FROM farmers WHERE id = ?", (farmer_id,)).fetchone()
    if not farmer:
        abort(404)
    
    requests = conn.execute(
        "SELECT r.*, d.name AS driver_name FROM requests r LEFT JOIN drivers d ON r.driver_id = d.id WHERE r.farmer_id = ? ORDER BY r.id DESC LIMIT 10",
        (farmer_id,)
    ).fetchall()
    
    # Calculate average order value
    avg_order = conn.execute(
        "SELECT AVG(price) as avg_price FROM requests WHERE farmer_id = ? AND price IS NOT NULL",
        (farmer_id,)
    ).fetchone()
    
    conn.close()
    
    farmer_data = dict(farmer) if farmer else {}
    farmer_data['avg_order_value'] = avg_order['avg_price'] if avg_order and avg_order['avg_price'] else 0
    
    return render_template(
        "farmer_profile.html",
        farmer=farmer_data,
        requests=requests
    )


def get_driver_badges(driver):
    """Generate achievement badges for driver"""
    badges = []
    if driver["total_deliveries"] >= 100:
        badges.append({"name": "Century Club", "icon": "🏆", "desc": "100+ deliveries"})
    if driver["rating"] >= 4.9:
        badges.append({"name": "5-Star Elite", "icon": "⭐", "desc": "Rating 4.9+"})
    if driver["total_deliveries"] >= 200:
        badges.append({"name": "Logistics Legend", "icon": "👑", "desc": "200+ deliveries"})
    if driver["earnings"] >= 2000:
        badges.append({"name": "Top Earner", "icon": "💰", "desc": "₵2000+ earnings"})
    return badges


@app.post("/request/<int:request_id>/rate")
def rate_delivery(request_id):
    """Submit rating and review for delivery"""
    conn = get_db_connection()
    req = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not req:
        abort(404)
    
    rating = int(request.form.get("rating", 5))
    review = request.form.get("review", "").strip()
    
    conn.execute(
        "UPDATE requests SET rating = ?, review = ? WHERE id = ?",
        (rating, review, request_id)
    )
    
    # Update driver rating
    if req["driver_id"]:
        all_ratings = conn.execute(
            "SELECT AVG(rating) as avg_rating FROM requests WHERE driver_id = ? AND rating IS NOT NULL",
            (req["driver_id"],)
        ).fetchone()
        avg_rating = all_ratings["avg_rating"] or 5.0
        conn.execute(
            "UPDATE drivers SET rating = ? WHERE id = ?",
            (round(avg_rating, 1), req["driver_id"])
        )
    
    # Update farmer rating
    all_farmer_ratings = conn.execute(
        "SELECT AVG(rating) as avg_rating FROM requests WHERE farmer_id = ? AND rating IS NOT NULL",
        (req["farmer_id"],)
    ).fetchone()
    avg_farmer_rating = all_farmer_ratings["avg_rating"] or 5.0
    conn.execute(
        "UPDATE farmers SET rating = ? WHERE id = ?",
        (round(avg_farmer_rating, 1), req["farmer_id"])
    )
    
    conn.commit()
    conn.close()
    flash("Thank you for your rating!", "success")
    return redirect(url_for("farmer_dashboard"))


@app.get("/tracking/<int:request_id>")
def live_tracking(request_id):
    """Live GPS tracking simulation"""
    conn = get_db_connection()
    req = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not req:
        abort(404)
    
    tracking = conn.execute(
        "SELECT * FROM tracking WHERE request_id = ? ORDER BY timestamp DESC LIMIT 20",
        (request_id,)
    ).fetchall()
    conn.close()
    
    return render_template(
        "tracking.html",
        request=req,
        tracking=tracking
    )


@app.get("/invoice/<int:request_id>")
def invoice(request_id):
    """Generate delivery invoice/receipt"""
    conn = get_db_connection()
    req = conn.execute(
        """SELECT r.*, f.name as farmer_name, f.phone as farmer_phone,
           d.name as driver_name, d.phone as driver_phone FROM requests r
           JOIN farmers f ON r.farmer_id = f.id
           LEFT JOIN drivers d ON r.driver_id = d.id
           WHERE r.id = ?""",
        (request_id,)
    ).fetchone()
    
    driver = None
    farmer = None
    if req and req['driver_id']:
        driver = conn.execute("SELECT * FROM drivers WHERE id = ?", (req['driver_id'],)).fetchone()
    if req:
        farmer = conn.execute("SELECT * FROM farmers WHERE id = ?", (req['farmer_id'],)).fetchone()
    
    conn.close()
    
    if not req:
        abort(404)
    
    invoice_data = {
        'id': f'INV-{request_id:05d}',
        'date': datetime.now().strftime('%d %b %Y')
    }
    
    return render_template("invoice.html", invoice=invoice_data, request=req, driver=driver, farmer=farmer)


# ============== MARKET TRANSPARENCY & PROFIT ESTIMATION ==============


@app.get("/market/prices")
def market_prices():
    """View all market prices for crops"""
    conn = get_db_connection()
    prices = conn.execute(
        "SELECT DISTINCT crop_name FROM market_prices ORDER BY crop_name"
    ).fetchall()
    
    crops = [p[0] for p in prices]
    market_data = {}
    
    for crop in crops:
        regions = conn.execute(
            "SELECT region, price, demand_level, trend FROM market_prices WHERE crop_name = ? ORDER BY price DESC",
            (crop,)
        ).fetchall()
        market_data[crop] = [dict(row) for row in regions]
    
    conn.close()
    return render_template("market_prices.html", crops=crops, market_data=market_data)


@app.get("/market/profit-estimator")
def profit_estimator_page():
    """Profit estimator tool for farmers"""
    conn = get_db_connection()
    crops = conn.execute(
        "SELECT DISTINCT crop_name FROM market_prices ORDER BY crop_name"
    ).fetchall()
    regions = conn.execute(
        "SELECT DISTINCT region FROM market_prices ORDER BY region"
    ).fetchall()
    conn.close()
    
    crops = [c[0] for c in crops]
    regions = [r[0] for r in regions]
    
    return render_template("profit_estimator.html", crops=crops, regions=regions)


@app.post("/api/estimate-profit")
def api_estimate_profit():
    """API endpoint for profit estimation"""
    data = request.get_json()
    crop = data.get("crop")
    quantity = float(data.get("quantity", 0))
    transport_cost = float(data.get("transport_cost", 0))
    destination = data.get("destination")
    
    if not all([crop, quantity, destination]):
        return jsonify({"error": "Missing required fields"}), 400
    
    estimate = estimate_profit(crop, quantity, transport_cost, "Local", destination)
    if not estimate:
        return jsonify({"error": "Crop or region not found"}), 404
    
    return jsonify(estimate)


@app.post("/api/best-market")
def api_best_market():
    """API endpoint for best market recommendation"""
    data = request.get_json()
    crop = data.get("crop")
    quantity = float(data.get("quantity", 0))
    transport_costs = data.get("transport_costs", {})
    
    if not crop or quantity <= 0:
        return jsonify({"error": "Invalid crop or quantity"}), 400
    
    best = get_best_market(crop, quantity, transport_costs)
    if not best:
        return jsonify({"error": "No markets available"}), 404
    
    return jsonify(best)


@app.get("/api/market-prices/<crop>")
def api_crop_prices(crop):
    """Get all prices for a specific crop"""
    conn = get_db_connection()
    prices = conn.execute(
        "SELECT region, price, demand_level, trend FROM market_prices WHERE crop_name = ? ORDER BY price DESC",
        (crop,)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in prices])


@app.post("/api/save-profit-estimate")
def api_save_profit_estimate():
    """Save profit estimate to farmer's history"""
    data = request.get_json()
    farmer_id = data.get("farmer_id")
    crop = data.get("crop")
    quantity = float(data.get("quantity", 0))
    transport_cost = float(data.get("transport_cost", 0))
    destination = data.get("destination")
    
    if not all([farmer_id, crop, quantity, destination]):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    estimate = estimate_profit(crop, quantity, transport_cost, "Local", destination, conn)
    
    if estimate:
        conn.execute(
            """INSERT INTO profit_estimates 
            (farmer_id, crop_name, quantity, transport_cost, destination_region, 
             estimated_revenue, estimated_profit, profit_margin, recommended_market, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (farmer_id, crop, quantity, transport_cost, destination,
             estimate['estimated_revenue'], estimate['estimated_profit'], 
             estimate['profit_margin'], destination, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "estimate": estimate})
    
    conn.close()
    return jsonify({"error": "Could not calculate profit"}), 400


# ============== ANTI-MIDDLEMEN & BUYER MARKETPLACE ==============


@app.get("/buyer/marketplace")
def buyer_marketplace():
    """Buyer marketplace dashboard"""
    conn = get_db_connection()
    offers = conn.execute(
        "SELECT * FROM buyer_offers WHERE status = 'Active' ORDER BY created_at DESC"
    ).fetchall()
    trusted_buyers = conn.execute(
        "SELECT * FROM trusted_buyers WHERE verification_status = 'Verified' ORDER BY rating DESC"
    ).fetchall()
    conn.close()
    
    return render_template("buyer_marketplace.html", offers=offers, trusted_buyers=trusted_buyers)


@app.post("/api/buyer-offer/create")
def create_buyer_offer():
    """Create a new buyer offer"""
    data = request.get_json()
    
    buyer_name = data.get("buyer_name")
    phone = data.get("phone")
    crop = data.get("crop_name")
    quantity = float(data.get("quantity", 0))
    offered_price = float(data.get("offered_price", 0))
    location = data.get("location")
    description = data.get("description", "")
    
    if not all([buyer_name, phone, crop, quantity, offered_price, location]):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    
    # Register or get buyer in trusted_buyers
    buyer = conn.execute(
        "SELECT id FROM trusted_buyers WHERE buyer_name = ? AND phone = ?",
        (buyer_name, phone)
    ).fetchone()
    
    if not buyer:
        conn.execute(
            """INSERT INTO trusted_buyers 
            (buyer_id, buyer_name, phone, verification_status, created_at)
            VALUES (?, ?, ?, ?, ?)""",
            (1, buyer_name, phone, "Pending", datetime.now().isoformat())
        )
        conn.commit()
        buyer_id = conn.execute(
            "SELECT id FROM trusted_buyers WHERE buyer_name = ? AND phone = ?",
            (buyer_name, phone)
        ).fetchone()
        buyer_id = buyer_id[0] if buyer_id else 1
    else:
        buyer_id = buyer[0]
    
    # Create the offer
    conn.execute(
        """INSERT INTO buyer_offers 
        (buyer_id, buyer_name, crop_name, quantity, offered_price, location, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (buyer_id, buyer_name, crop, quantity, offered_price, location, description, datetime.now().isoformat())
    )
    conn.commit()
    
    offer_id = conn.lastrowid
    conn.close()
    
    return jsonify({
        "success": True, 
        "offer_id": offer_id,
        "message": f"Offer posted successfully. Total: {quantity} units at {offered_price}/unit"
    })


@app.get("/api/buyer-offers")
def api_buyer_offers():
    """Get all active buyer offers"""
    crop_filter = request.args.get("crop")
    
    conn = get_db_connection()
    
    if crop_filter:
        offers = conn.execute(
            "SELECT * FROM buyer_offers WHERE status = 'Active' AND crop_name = ? ORDER BY created_at DESC",
            (crop_filter,)
        ).fetchall()
    else:
        offers = conn.execute(
            "SELECT * FROM buyer_offers WHERE status = 'Active' ORDER BY created_at DESC"
        ).fetchall()
    
    conn.close()
    return jsonify([dict(row) for row in offers])


@app.post("/api/offer/accept")
def accept_buyer_offer():
    """Farmer accepts a buyer offer"""
    data = request.get_json()
    
    offer_id = data.get("offer_id")
    farmer_id = data.get("farmer_id")
    
    if not offer_id or not farmer_id:
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    
    # Get offer details
    offer = conn.execute(
        "SELECT * FROM buyer_offers WHERE id = ?", (offer_id,)
    ).fetchone()
    
    if not offer:
        conn.close()
        return jsonify({"error": "Offer not found"}), 404
    
    # Update offer
    conn.execute(
        "UPDATE buyer_offers SET farmer_id = ?, status = ? WHERE id = ?",
        (farmer_id, "Accepted", offer_id)
    )
    
    # Create notification
    create_notification(
        conn,
        f"Offer accepted! {offer['buyer_name']} wants {offer['quantity']} units of {offer['crop_name']}",
        notification_type="success"
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True,
        "message": "Offer accepted successfully"
    })


@app.post("/api/fair-price-check")
def check_fair_price():
    """Check if an offer price is fair compared to market price"""
    data = request.get_json()
    
    crop = data.get("crop_name")
    offered_price = float(data.get("offered_price", 0))
    quantity = float(data.get("quantity", 0))
    destination = data.get("destination", "Dar es Salaam")
    
    if not all([crop, offered_price]):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    
    # Get market price for the crop
    market_price = conn.execute(
        "SELECT AVG(price) as avg_price FROM market_prices WHERE crop_name = ?",
        (crop,)
    ).fetchone()
    
    conn.close()
    
    if not market_price or market_price['avg_price'] is None:
        return jsonify({"error": "Market data not available"}), 404
    
    avg_market_price = market_price['avg_price']
    difference = avg_market_price - offered_price
    percentage_below = (difference / avg_market_price) * 100 if avg_market_price > 0 else 0
    
    # Determine if price is fair
    is_fair = percentage_below < 10  # Within 10% is considered fair
    alert_type = "success" if is_fair else "warning"
    
    if percentage_below < 0:
        message = f"💰 Great! Offer is {abs(percentage_below):.1f}% above market average!"
        alert_type = "success"
    elif percentage_below == 0:
        message = "💯 Offer matches market average price"
        alert_type = "info"
    elif percentage_below < 10:
        message = f"⚠️ Offer is {percentage_below:.1f}% below market average (acceptable range)"
        alert_type = "info"
    elif percentage_below < 30:
        message = f"⚠️ WARNING: Offer is {percentage_below:.1f}% below market average"
        alert_type = "warning"
    else:
        message = f"❌ DANGER: Offer is {percentage_below:.1f}% below market value. Likely exploitation!"
        alert_type = "danger"
    
    return jsonify({
        "is_fair": is_fair,
        "alert_type": alert_type,
        "message": message,
        "market_average_price": round(avg_market_price, 2),
        "offered_price": offered_price,
        "difference": round(difference, 2),
        "percentage_below": round(percentage_below, 2),
        "recommended_price": round(avg_market_price * 0.95, 2),
        "total_market_value": round(avg_market_price * quantity, 2),
        "total_offered_value": round(offered_price * quantity, 2)
    })


@app.get("/api/trusted-buyers")
def api_trusted_buyers():
    """Get all verified trusted buyers"""
    conn = get_db_connection()
    buyers = conn.execute(
        "SELECT * FROM trusted_buyers WHERE verification_status = 'Verified' ORDER BY rating DESC"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in buyers])


@app.get("/farmer/offers/<int:farmer_id>")
def farmer_offers(farmer_id):
    """View all offers for a specific farmer"""
    conn = get_db_connection()
    
    farmer = conn.execute(
        "SELECT * FROM farmers WHERE id = ?", (farmer_id,)
    ).fetchone()
    
    if not farmer:
        conn.close()
        abort(404)
    
    offers = conn.execute(
        "SELECT * FROM buyer_offers WHERE status = 'Active' ORDER BY created_at DESC"
    ).fetchall()
    
    # Get market prices for comparison
    crops = conn.execute(
        "SELECT DISTINCT crop_name FROM market_prices"
    ).fetchall()
    crops = [c[0] for c in crops]
    
    conn.close()
    
    return render_template(
        "farmer_offers.html",
        farmer=farmer,
        offers=offers,
        crops=crops
    )


# ============== USSD SIMULATOR & API --------------

@app.route("/ussd-simulator")
def ussd_simulator():
    """Render USSD & SMS Simulator page"""
    conn = get_db_connection()
    requests_rows = conn.execute(
        """SELECT r.id, f.name as farmer_name, r.pickup_location, r.destination,
                  r.goods_type, r.status
           FROM requests r JOIN farmers f ON r.farmer_id = f.id 
           ORDER BY r.id DESC LIMIT 10"""
    ).fetchall()
    conn.close()
    return render_template(
        "ussd_simulator.html",
        active="ussd",
        heading="USSD & SMS Simulation Hub",
        subheading="Test Africa's Talking-style USSD, SMS alerts, and GPS journeys.",
        requests=requests_rows,
        callback_url=url_for("api_ussd", _external=True),
        sms_status=sms_status,
    )


@app.post("/api/ussd")
def api_ussd():
    """Africa's Talking USSD Sandbox Endpoint"""
    session_id = request.form.get("sessionId", "session_1234")
    service_code = request.form.get("serviceCode", "*123#")
    phone_number = request.form.get("phoneNumber", "+254700000000")
    text = request.form.get("text", "")
    
    parts = [p.strip() for p in text.split("*")] if text else []
    
    crops = CROPS
    regions = MARKET_REGIONS
    pickup_locations = PICKUP_LOCATIONS
    
    if len(parts) == 0 or not text:
        return "CON Welcome to AgriMove AI.\nChoose option:\n1. Check Market Prices\n2. Request Transport\n3. Find Buyers\n4. Track Delivery\n5. Profit Estimator"
        
    elif parts[0] == "1":
        if len(parts) == 1:
            crop_list = "\n".join([f"{i+1}. {crop}" for i, crop in enumerate(crops)])
            return f"CON Select Crop:\n{crop_list}"
        elif len(parts) == 2:
            try:
                crop_idx = int(parts[1]) - 1
                if 0 <= crop_idx < len(crops):
                    region_list = "\n".join([f"{i+1}. {region}" for i, region in enumerate(regions)])
                    return f"CON Select Region for {crops[crop_idx]}:\n{region_list}"
                else:
                    return "END Invalid crop selection."
            except ValueError:
                return "END Invalid input."
        elif len(parts) == 3:
            try:
                crop_idx = int(parts[1]) - 1
                region_idx = int(parts[2]) - 1
                if 0 <= crop_idx < len(crops) and 0 <= region_idx < len(regions):
                    crop_name = crops[crop_idx]
                    region_name = regions[region_idx]
                    conn = get_db_connection()
                    price_row = conn.execute(
                        "SELECT price, demand_level, trend FROM market_prices WHERE crop_name = ? AND region = ?",
                        (crop_name, region_name)
                    ).fetchone()
                    conn.close()
                    if price_row:
                        return f"END {crop_name} ({region_name}):\nPrice: {price_row['price']:,} TZS\nDemand: {price_row['demand_level']}\nTrend: {price_row['trend']}"
                    else:
                        return f"END Price data not found for {crop_name} in {region_name}."
                else:
                    return "END Invalid selection."
            except ValueError:
                return "END Invalid input."
                
    elif parts[0] == "2":
        if len(parts) == 1:
            crop_list = "\n".join([f"{i+1}. {crop}" for i, crop in enumerate(crops)])
            return f"CON Select Crop to Transport:\n{crop_list}"
        elif len(parts) == 2:
            return "CON Enter quantity (e.g. 50 bags):"
        elif len(parts) == 3:
            pickup_list = "\n".join([f"{i+1}. {place}" for i, place in enumerate(pickup_locations)])
            return f"CON Select Pickup Location:\n{pickup_list}"
        elif len(parts) == 4:
            region_list = "\n".join([f"{i+1}. {region}" for i, region in enumerate(regions)])
            return f"CON Select Destination Market:\n{region_list}"
        elif len(parts) == 5:
            try:
                crop_name = crops[int(parts[1]) - 1]
                quantity = parts[2]
                pickup = pickup_locations[int(parts[3]) - 1]
                destination = regions[int(parts[4]) - 1]
            except (ValueError, IndexError):
                return "END Invalid transport selection."
            return f"CON Confirm Transport?\n{quantity} of {crop_name}\nFrom: {pickup}\nTo: {destination}\n1. Yes, Request\n2. Cancel"
        elif len(parts) == 6:
            if parts[5] == "1":
                try:
                    crop_name = crops[int(parts[1]) - 1]
                    quantity = parts[2]
                    pickup = pickup_locations[int(parts[3]) - 1]
                    destination = regions[int(parts[4]) - 1]
                except (ValueError, IndexError):
                    return "END Invalid transport selection."
                
                conn = get_db_connection()
                farmer = conn.execute("SELECT id FROM farmers WHERE phone = ?", (phone_number,)).fetchone()
                if farmer:
                    farmer_id = farmer["id"]
                else:
                    farmer_id = conn.execute(
                        "INSERT INTO farmers (name, phone, member_since) VALUES (?, ?, ?)",
                        (f"USSD Farmer ({phone_number[-4:]})", phone_number, datetime.now().isoformat())
                    ).lastrowid
                
                driver, eta = assign_driver(conn)
                driver_id = driver["id"] if driver else None
                status = "Pending"
                
                if driver_id:
                    conn.execute("UPDATE drivers SET availability = 'busy' WHERE id = ?", (driver_id,))
                
                request_id = conn.execute(
                    """
                    INSERT INTO requests (
                        farmer_id, pickup_location, destination, goods_type, quantity,
                        status, driver_id, eta_minutes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (farmer_id, pickup, destination, crop_name, quantity, status, driver_id, eta, datetime.now().isoformat())
                ).lastrowid
                
                msg = f"Transport Request #{request_id} created successfully."
                if driver_id:
                    msg += f" Driver {driver['name']} assigned (ETA: {eta} mins)."
                else:
                    msg += " Searching for available drivers."
                
                dispatch_notification(conn, msg, request_id)
                conn.commit()
                conn.close()
                
                return f"END Transport Request #{request_id} created successfully!\nWe are matching a driver. You will receive SMS updates."
            else:
                return "END Request cancelled."
                
    elif parts[0] == "3":
        if len(parts) == 1:
            crop_list = "\n".join([f"{i+1}. {crop}" for i, crop in enumerate(crops[:4])])
            return f"CON Select Crop to Sell:\n{crop_list}"
        elif len(parts) == 2:
            try:
                crop_idx = int(parts[1]) - 1
                if 0 <= crop_idx < 4:
                    crop_name = crops[crop_idx]
                    conn = get_db_connection()
                    offers = conn.execute(
                        "SELECT id, buyer_name, offered_price FROM buyer_offers WHERE crop_name = ? AND status = 'Active' LIMIT 3",
                        (crop_name,)
                    ).fetchall()
                    conn.close()
                    if offers:
                        offer_list = "\n".join([f"{i+1}. {o['buyer_name']} ({o['offered_price']:,} TZS)" for i, o in enumerate(offers)])
                        return f"CON Active Offers for {crop_name}:\n{offer_list}"
                    else:
                        return f"END No active buyer offers found for {crop_name}."
                else:
                    return "END Invalid crop selection."
            except ValueError:
                return "END Invalid input."
        elif len(parts) == 3:
            try:
                crop_idx = int(parts[1]) - 1
                offer_choice = int(parts[2]) - 1
                crop_name = crops[crop_idx]
                
                conn = get_db_connection()
                offers = conn.execute(
                    "SELECT * FROM buyer_offers WHERE crop_name = ? AND status = 'Active' LIMIT 3",
                    (crop_name,)
                ).fetchall()
                conn.close()
                
                if 0 <= offer_choice < len(offers):
                    selected = offers[offer_choice]
                    return f"END Details:\nBuyer: {selected['buyer_name']}\nPrice: {selected['offered_price']:,} TZS\nQty: {selected['quantity']}\nLocation: {selected['location']}"
                else:
                    return "END Invalid offer selection."
            except ValueError:
                return "END Invalid input."

    elif parts[0] == "4":
        if len(parts) == 1:
            return "CON Enter Request ID to track:"
        elif len(parts) == 2:
            try:
                req_id = int(parts[1])
                conn = get_db_connection()
                req_row = conn.execute(
                    """SELECT r.*, d.name as driver_name, d.phone as driver_phone 
                       FROM requests r LEFT JOIN drivers d ON r.driver_id = d.id 
                       WHERE r.id = ?""",
                    (req_id,)
                ).fetchone()
                conn.close()
                if req_row:
                    driver_info = f"{req_row['driver_name']} ({req_row['driver_phone']})" if req_row['driver_name'] else "Searching..."
                    return f"END Request #{req_id} Status:\nStatus: {req_row['status']}\nDriver: {driver_info}\nETA: {req_row['eta_minutes'] or '—'} mins"
                else:
                    return f"END Request #{req_id} not found."
            except ValueError:
                return "END Invalid Request ID."

    elif parts[0] == "5":
        if len(parts) == 1:
            return "CON Enter crop name (e.g. Maize):"
        elif len(parts) == 2:
            return "CON Enter quantity (bags):"
        elif len(parts) == 3:
            return "CON Enter transport cost (TZS):"
        elif len(parts) == 4:
            region_list = "\n".join([f"{i+1}. {region}" for i, region in enumerate(regions)])
            return f"CON Select Destination Region:\n{region_list}"
        elif len(parts) == 5:
            try:
                crop = parts[1]
                quantity = float(parts[2])
                transport = float(parts[3])
                reg_idx = int(parts[4]) - 1
                if 0 <= reg_idx < len(regions):
                    dest = regions[reg_idx]
                    estimate = estimate_profit(crop, quantity, transport, "Local", dest)
                    if estimate:
                        return f"END Profit Estimate ({crop}):\nEst. Revenue: {estimate['estimated_revenue']:,} TZS\nEst. Cost: {estimate['total_costs']:,} TZS\nEst. Profit: {estimate['estimated_profit']:,} TZS\nMargin: {estimate['profit_margin']}%"
                    else:
                        return f"END Market {dest} has no price data for {crop}."
                else:
                    return "END Invalid region selection."
            except ValueError:
                return "END Invalid input."

    return "END Invalid option."

# ============== AI MARKET INTELLIGENCE ==============

@app.route("/market/insights")
def market_insights():
    """AI Market Intelligence Insights Screen"""
    conn = get_db_connection()
    
    crops_query = conn.execute("SELECT DISTINCT crop_name FROM market_prices").fetchall()
    best_markets = []
    
    for crop_row in crops_query:
        crop = crop_row[0]
        best = conn.execute(
            "SELECT region, price, demand_level, trend FROM market_prices WHERE crop_name = ? ORDER BY price DESC LIMIT 1",
            (crop,)
        ).fetchone()
        if best:
            best_markets.append({
                "crop": crop,
                "region": best["region"],
                "price": best["price"],
                "demand": best["demand_level"],
                "trend": best["trend"]
            })
            
    hotspots = conn.execute(
        "SELECT crop_name, region, price, trend FROM market_prices WHERE demand_level = 'High' ORDER BY price DESC LIMIT 5"
    ).fetchall()
    
    projections = []
    for bm in best_markets:
        proj_pct = random.randint(6, 16) if bm["trend"] == "Rising" else random.randint(-4, 4)
        proj_price = bm["price"] * (1 + proj_pct/100)
        projections.append({
            "crop": bm["crop"],
            "region": bm["region"],
            "current_price": bm["price"],
            "projected_price": int(proj_price),
            "proj_percent": proj_pct,
            "trend": bm["trend"]
        })
        
    drivers = conn.execute("SELECT * FROM drivers WHERE availability = 'available' LIMIT 3").fetchall()
    transport_recs = []
    
    if drivers:
        for idx, bm in enumerate(best_markets[:3]):
            if idx < len(drivers):
                drv = drivers[idx]
                discount = random.randint(5, 15)
                transport_recs.append({
                    "crop": bm["crop"],
                    "region": bm["region"],
                    "driver_name": drv["name"],
                    "vehicle": drv["vehicle_type"].capitalize(),
                    "benefit": f"Consolidate and save {discount}% using {drv['name']} ({drv['vehicle_type']}) nearby."
                })
                
    alerts = []
    for bm in best_markets:
        if bm["trend"] == "Rising":
            alerts.append(f"AI Alert: {bm['crop']} prices rising in {bm['region']}. Projected spike next week!")
        if bm["demand"] == "High":
            alerts.append(f"AI Alert: High {bm['crop']} demand detected in {bm['region']} region.")
            
    conn.close()
    
    return render_template(
        "market_insights.html",
        active="insights",
        heading="AI Market Intelligence",
        subheading="Real-time predictive models, demand tracking, and smart routes.",
        best_markets=best_markets,
        hotspots=hotspots,
        projections=projections,
        transport_recs=transport_recs,
        alerts=alerts
    )


# ============== ADMIN DASHBOARD ==============


def advance_gps_simulation(conn, request_id):
    """Move a request one simulated GPS step toward its destination."""
    req = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not req:
        return None
    
    count = conn.execute("SELECT COUNT(*) FROM tracking WHERE request_id = ?", (request_id,)).fetchone()[0]

    dest_name = req["destination"]
    dest_coord = LOCATION_COORDS.get(dest_name, LOCATION_COORDS["Dar es Salaam"])
    start_coord = LOCATION_COORDS.get(req["pickup_location"], LOCATION_COORDS["Morogoro Farm Gate"])
    
    steps = 6
    if count >= steps:
        progress = 1.0
        if req["status"] != "Delivered":
            conn.execute("UPDATE requests SET status = 'Delivered', completed_at = ? WHERE id = ?", (datetime.now().isoformat(), request_id))
            if req["driver_id"]:
                conn.execute("UPDATE drivers SET availability = 'available' WHERE id = ?", (req["driver_id"],))
            create_notification(conn, f"Delivery Completed! Shipment #{request_id} has arrived at {dest_name}.", request_id, "success")
    else:
        progress = (count + 1) / steps
        if req["status"] in ["Accepted", "Pending"] and count > 0:
            conn.execute("UPDATE requests SET status = 'In Transit' WHERE id = ?", (request_id,))
            create_notification(conn, f"Shipment #{request_id} is now In Transit to {dest_name}.", request_id, "info")
            
    latitude = round(start_coord[0] + progress * (dest_coord[0] - start_coord[0]), 4)
    longitude = round(start_coord[1] + progress * (dest_coord[1] - start_coord[1]), 4)
    
    disp_status = "delivered" if progress >= 1.0 else ("in_transit" if count > 0 else "pickup")
    
    conn.execute(
        "INSERT INTO tracking (request_id, latitude, longitude, status, timestamp) VALUES (?, ?, ?, ?, ?)",
        (request_id, latitude, longitude, disp_status, datetime.now().isoformat())
    )
    conn.commit()
    
    updated_req = conn.execute("SELECT status FROM requests WHERE id = ?", (request_id,)).fetchone()
    return {
        "success": True, 
        "latitude": latitude, 
        "longitude": longitude, 
        "progress": int(progress * 100),
        "status": updated_req["status"]
    }


@app.post("/simulate/gps/<int:request_id>")
def simulate_gps(request_id):
    """Simulate GPS tracking coordinates along path to destination"""
    conn = get_db_connection()
    result = advance_gps_simulation(conn, request_id)
    if not result:
        conn.close()
        abort(404)
    conn.close()
    return jsonify(result)


@app.post("/simulate/gps/<int:request_id>/full")
def simulate_full_gps(request_id):
    """Run the full GPS journey simulation in one sandbox action."""
    conn = get_db_connection()
    result = None
    for _ in range(7):
        result = advance_gps_simulation(conn, request_id)
        if not result:
            conn.close()
            abort(404)
        if result["status"] == "Delivered":
            break
    conn.close()
    return jsonify(result)


@app.get("/notifications")
def notifications_hub():
    """View all notifications"""
    conn = get_db_connection()
    notifications = conn.execute(
        "SELECT * FROM notifications ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return render_template("notifications.html", notifications=notifications)


@app.post("/notifications/clear")
def clear_notifications():
    """Clear all notifications"""
    conn = get_db_connection()
    conn.execute("DELETE FROM notifications")
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.get("/help")
def help_page():
    """Help and support page"""
    return render_template("help.html")


@app.get("/api/notifications")
def api_notifications():
    """Get recent notifications"""
    conn = get_db_connection()
    notifications = conn.execute(
        "SELECT * FROM notifications ORDER BY created_at DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in notifications])


def create_notification(conn, message, request_id=None, notification_type="info"):
    """Create notification in database"""
    conn.execute(
        "INSERT INTO notifications (request_id, message, type, created_at) VALUES (?, ?, ?, ?)",
        (request_id, message, notification_type, datetime.now().isoformat())
    )
    conn.commit()


@app.route("/admin")
def admin_dashboard():
    """Main admin dashboard with price and buyer management data."""
    conn = get_db_connection()
    requests_rows = conn.execute(
        """
        SELECT r.*, f.name AS farmer_name, f.phone AS farmer_phone,
               d.name AS driver_name, d.phone AS driver_phone
        FROM requests r
        JOIN farmers f ON r.farmer_id = f.id
        LEFT JOIN drivers d ON r.driver_id = d.id
        ORDER BY r.id DESC
        """
    ).fetchall()
    drivers = conn.execute("SELECT * FROM drivers ORDER BY name").fetchall()
    notifications = conn.execute(
        "SELECT * FROM notifications ORDER BY id DESC LIMIT 10"
    ).fetchall()
    
    # Query prices and buyers for administration tabs
    prices = conn.execute("SELECT * FROM market_prices ORDER BY crop_name, region").fetchall()
    buyers = conn.execute("SELECT * FROM trusted_buyers ORDER BY buyer_name").fetchall()
    
    counts = summarize_statuses(requests_rows)
    active_drivers = len(
        [d for d in drivers if d["availability"] == "available"]
    )
    conn.close()

    return render_template(
        "admin_dashboard.html",
        active="admin",
        heading="Admin Dashboard",
        subheading="System overview, analytics, and request management.",
        requests=requests_rows,
        drivers=drivers,
        notifications=notifications,
        counts=counts,
        active_drivers=active_drivers,
        prices=prices,
        buyers=buyers
    )


@app.route("/admin/analytics")
def admin_analytics():
    """Analytics and charts page."""
    conn = get_db_connection()
    requests_rows = conn.execute("SELECT * FROM requests").fetchall()
    conn.close()
    counts = summarize_statuses(requests_rows)

    return render_template(
        "admin_analytics.html",
        active="admin",
        heading="Analytics & Reports",
        subheading="Delivery statistics, trends, and performance metrics.",
        counts=counts,
    )


# ============== ADMIN MANAGEMENT ACTIONS --------------

@app.post("/admin/prices/add")
def admin_add_price():
    crop = request.form.get("crop_name", "").strip()
    region = request.form.get("region", "").strip()
    price = request.form.get("price", "0").strip()
    demand = request.form.get("demand_level", "Medium")
    trend = request.form.get("trend", "Stable")
    
    if not crop or not region or not price:
        flash("Please fill in all fields", "danger")
        return redirect(url_for("admin_dashboard"))
        
    try:
        price_val = float(price)
        conn = get_db_connection()
        conn.execute(
            """INSERT OR REPLACE INTO market_prices (crop_name, region, price, demand_level, trend, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (crop, region, price_val, demand, trend, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        flash(f"Price for {crop} in {region} added/updated successfully.", "success")
    except ValueError:
        flash("Invalid price value", "danger")
        
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/prices/edit")
def admin_edit_price():
    price_id = request.form.get("price_id")
    price = request.form.get("price", "0").strip()
    demand = request.form.get("demand_level", "Medium")
    trend = request.form.get("trend", "Stable")
    
    if not price_id or not price:
        flash("Missing details for price update", "danger")
        return redirect(url_for("admin_dashboard"))
        
    try:
        price_val = float(price)
        conn = get_db_connection()
        conn.execute(
            "UPDATE market_prices SET price = ?, demand_level = ?, trend = ?, updated_at = ? WHERE id = ?",
            (price_val, demand, trend, datetime.now().isoformat(), price_id)
        )
        conn.commit()
        conn.close()
        flash("Market price updated successfully.", "success")
    except ValueError:
        flash("Invalid price value", "danger")
        
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/prices/delete/<int:price_id>")
def admin_delete_price(price_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM market_prices WHERE id = ?", (price_id,))
    conn.commit()
    conn.close()
    flash("Market price entry deleted successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/buyers/verify/<int:buyer_id>")
def admin_verify_buyer(buyer_id):
    status = request.form.get("status", "Verified")
    conn = get_db_connection()
    conn.execute(
        "UPDATE trusted_buyers SET verification_status = ?, verified_by = 'Admin', verified_at = ? WHERE id = ?",
        (status, datetime.now().isoformat(), buyer_id)
    )
    conn.commit()
    conn.close()
    flash(f"Buyer status updated to {status} successfully.", "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
