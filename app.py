import os
import random
import sqlite3
from datetime import datetime, timedelta
import json

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

from flask import Flask, Response, abort, flash, jsonify, make_response, redirect, render_template, request, session, url_for
from i18n import get_lang, status_label, t
from sms_service import (
    check_simulator_reachable,
    farmer_transport_sms,
    init_sms_client,
    normalize_phone,
    send_sms,
    sms_status,
    verify_at_credentials,
)

init_sms_client()

app = Flask(__name__)
app.secret_key = "agrimove-ai-secret"


@app.context_processor
def inject_i18n():
    lang = get_lang()
    return {"lang": lang, "t": t, "status_label": status_label}


@app.post("/api/set-language")
def set_language():
    data = request.get_json(silent=True) or {}
    lang = data.get("lang", "en")
    if lang not in ("en", "sw"):
        lang = "en"
    resp = make_response(jsonify({"ok": True, "lang": lang}))
    resp.set_cookie("agrimove_lang", lang, max_age=365 * 24 * 3600)
    return resp

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


# SMS integration — see sms_service.py


def dispatch_notification(conn, message, request_id=None, phone=None):
    """Send SMS via Africa's Talking sandbox (admin/driver flows may still log in-app)."""
    create_notification(conn, message, request_id)

    target_phone = phone
    if not target_phone and request_id:
        row = conn.execute(
            """
            SELECT f.phone FROM requests r
            JOIN farmers f ON r.farmer_id = f.id
            WHERE r.id = ?
            """,
            (request_id,),
        ).fetchone()
        if row:
            target_phone = row["phone"]

    if target_phone:
        return send_sms(target_phone, message, request_id, conn=conn)
    return {"success": False, "mode": sms_status["mode"], "error": "No phone number"}


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
        CREATE TABLE IF NOT EXISTS sms_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            provider_response TEXT,
            request_id INTEGER,
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
            crop_name_swahili TEXT,
            region TEXT NOT NULL,
            market_name TEXT,
            price REAL NOT NULL,
            price_per_kg_tzs REAL DEFAULT 0.0,
            demand_level TEXT DEFAULT 'Medium',
            trend TEXT DEFAULT 'Stable',
            price_trend TEXT DEFAULT 'stable',
            updated_at TEXT NOT NULL,
            last_updated TEXT,
            UNIQUE(crop_name, region, market_name)
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transport_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT NOT NULL,
            farmer_phone TEXT NOT NULL,
            village TEXT NOT NULL,
            ward TEXT NOT NULL,
            district TEXT NOT NULL,
            crop_type TEXT NOT NULL,
            quantity_bags INTEGER NOT NULL,
            pickup_date TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transport_pools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            truck_capacity_bags INTEGER NOT NULL,
            driver_name TEXT NOT NULL,
            driver_phone TEXT NOT NULL,
            route_from TEXT NOT NULL,
            route_to TEXT NOT NULL,
            departure_date TEXT NOT NULL,
            cost_per_bag_tzs REAL NOT NULL,
            available_slots INTEGER NOT NULL,
            status TEXT DEFAULT 'open'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_name TEXT NOT NULL,
            buyer_phone TEXT NOT NULL,
            farmer_name TEXT NOT NULL,
            farmer_phone TEXT NOT NULL,
            crop_type TEXT NOT NULL,
            quantity_kg REAL NOT NULL,
            amount_tzs REAL NOT NULL,
            mpesa_reference TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS storage_facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            facility_type TEXT NOT NULL,
            region TEXT NOT NULL,
            district TEXT NOT NULL,
            village TEXT NOT NULL,
            gps_lat REAL NOT NULL,
            gps_lng REAL NOT NULL,
            capacity_tons REAL NOT NULL,
            available_tons REAL NOT NULL,
            contact_phone TEXT NOT NULL,
            cost_per_bag_per_month_tzs REAL NOT NULL,
            accepts_wrs INTEGER DEFAULT 0
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
    """Seed two featured market prices for admin and demos."""
    conn = get_db_connection()
    featured = [
        ("Maize", "Dar es Salaam", 95000, "High", "Stable"),
        ("Tomatoes", "Dodoma", 145500, "High", "Rising"),
    ]
    for crop, region, price, demand, trend in featured:
        conn.execute(
            """INSERT OR IGNORE INTO market_prices
               (crop_name, region, price, demand_level, trend, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (crop, region, price, demand, trend, datetime.now().isoformat()),
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


@app.get("/api/africas-talking/status")
def africas_talking_status():
    """Return current Africa's Talking integration mode without exposing secrets."""
    sim_ok = check_simulator_reachable()
    cred_ok, cred_msg = verify_at_credentials()
    return jsonify({
        "sms_enabled": sms_status["enabled"],
        "credentials_valid": cred_ok,
        "username": sms_status["username"],
        "mode": sms_status["mode"],
        "message": sms_status["message"],
        "verify_detail": cred_msg if not cred_ok else "OK",
        "simulator_url": sms_status.get("simulator_url"),
        "simulator_reachable": sim_ok,
        "sandbox_outbox_url": sms_status.get("sandbox_outbox_url"),
        "register_phone_url": sms_status.get("register_phone_url"),
        "simulator_hint": (
            "Simulator port 1517 is reachable. Open the link, enter your phone, click Connect, then send SMS."
            if sim_ok
            else (
                "Simulator Connect failed: outbound port 1517 is blocked on your network/firewall. "
                "SMS still sends via API (check sandbox SMS Outbox in AT dashboard), or try mobile hotspot."
            )
        ),
    })


@app.get("/api/sms/logs")
def sms_logs():
    """Recent SMS log entries for debugging sandbox delivery."""
    limit = min(int(request.args.get("limit", 10)), 50)
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM sms_logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


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
    try:
        conn = get_db_connection()
        farmers_count = conn.execute("SELECT COUNT(*) FROM farmers").fetchone()[0]
        
        maize_row = conn.execute(
            "SELECT price_per_kg_tzs FROM market_prices WHERE LOWER(crop_name) = 'maize' OR LOWER(crop_name_swahili) = 'mahindi' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        maize_price = maize_row[0] if (maize_row and maize_row[0]) else 950.0
        
        loads_count = conn.execute("SELECT COUNT(*) FROM transport_requests").fetchone()[0]
        conn.close()
    except Exception as e:
        farmers_count = 0
        maize_price = 950.0
        loads_count = 0
        
    return render_template(
        "index.html",
        farmers_count=farmers_count,
        maize_price=maize_price,
        loads_count=loads_count
    )


@app.route("/farmer", methods=["GET", "POST"])
def farmer_dashboard():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            phone = normalize_phone(request.form.get("phone", "").strip()) or request.form.get("phone", "").strip()
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
                driver_name = driver["name"]
                sms_msg = farmer_transport_sms(
                    get_lang(), request_id, name, pickup, destination, goods_type, quantity,
                    driver_name=driver_name, eta=eta,
                )
            else:
                sms_msg = farmer_transport_sms(
                    get_lang(), request_id, name, pickup, destination, goods_type, quantity,
                )

            sms_result = send_sms(phone, sms_msg, request_id, conn=conn)

            conn.commit()
            conn.close()

            session["sms_toast"] = {
                "phone": sms_result.get("phone", phone),
                "message": sms_msg,
                "simulated": bool(sms_result.get("auth_failed")),
            }

            flash(t("transport_submitted"), "success")
            if sms_result.get("success"):
                flash(t("sms_sent_sandbox", phone=sms_result.get("phone", phone)), "success")
            elif sms_result.get("auth_failed"):
                flash(t("sms_auth_failed"), "error")
            else:
                flash(
                    t("sms_send_failed", error=sms_result.get("error", "Unknown error")),
                    "error",
                )
        except Exception as exc:
            flash(t("sms_send_failed", error=str(exc)), "error")
        return redirect(url_for("farmer_dashboard"))

    sms_toast = session.pop("sms_toast", None)

    return render_template(
        "farmer_dashboard.html",
        active="farmer",
        heading="Farmer Dashboard",
        subheading="Request transport and track the movement of your harvest.",
        pickup_locations=PICKUP_LOCATIONS,
        destination_regions=MARKET_REGIONS,
        crops=CROPS,
        at_sms_status=sms_status,
        sms_toast=sms_toast,
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
    flash(t("job_accepted"), "success")
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
    flash(t("delivery_started"), "success")
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
    flash(t("delivery_completed"), "success")
    return redirect(url_for("driver_dashboard"))


init_db()
seed_drivers()
seed_market_prices()
seed_buyers()


# ============== FEATURE 1: BEI ZA SOKO (Market Price Board) ==============

@app.get("/api/prices")
def api_prices():
    try:
        conn = get_db_connection()
        prices = conn.execute("SELECT * FROM market_prices ORDER BY crop_name, region, market_name").fetchall()
        conn.close()
        data = [dict(row) for row in prices]
        return jsonify({"success": True, "data": data, "message": "Bei za soko zimepatikana."})
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.get("/api/prices/<crop>")
def api_crop_price(crop):
    try:
        conn = get_db_connection()
        prices = conn.execute(
            "SELECT * FROM market_prices WHERE LOWER(crop_name) = ? OR LOWER(crop_name_swahili) = ? ORDER BY region, market_name",
            (crop.lower(), crop.lower())
        ).fetchall()
        conn.close()
        data = [dict(row) for row in prices]
        if not data:
            return jsonify({"success": False, "data": None, "message": f"Bei ya zao '{crop}' haikupatikana."}), 404
        return jsonify({"success": True, "data": data, "message": f"Bei za '{crop}' zimepatikana."})
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.get("/market-prices")
def market_prices_board():
    try:
        conn = get_db_connection()
        prices = conn.execute("SELECT * FROM market_prices ORDER BY crop_name, region, market_name").fetchall()
        conn.close()
        return render_template(
            "bei_za_soko.html",
            prices=prices,
            active="market_prices",
            heading="Bei za Soko",
            subheading="Bodi ya bei za mazao katika masoko makuu ya Tanzania."
        )
    except Exception as e:
        return render_template(
            "bei_za_soko.html",
            prices=[],
            error=str(e),
            active="market_prices",
            heading="Bei za Soko",
            subheading="Bodi ya bei za mazao."
        )


# ============== FEATURE 2: SHAMBA CONNECT (Load Pooling) ==============

def find_matching_requests(conn, ward, district, crop_type, pickup_date_str, current_req_id=None):
    query = """
        SELECT * FROM transport_requests 
        WHERE status = 'open' AND LOWER(crop_type) = ?
    """
    params = [crop_type.lower()]
    if current_req_id:
        query += " AND id != ?"
        params.append(current_req_id)
    
    rows = conn.execute(query, params).fetchall()
    matches = []
    
    try:
        target_date = datetime.strptime(pickup_date_str[:10], "%Y-%m-%d")
    except ValueError:
        target_date = None
        
    for row in rows:
        same_location = (row["ward"].lower() == ward.lower()) or (row["district"].lower() == district.lower())
        if not same_location:
            continue
            
        if target_date:
            try:
                row_date = datetime.strptime(row["pickup_date"][:10], "%Y-%m-%d")
                diff_days = abs((row_date - target_date).days)
                if diff_days <= 3:
                    matches.append(dict(row))
            except ValueError:
                matches.append(dict(row))
        else:
            matches.append(dict(row))
    return matches


@app.post("/api/transport/request")
def api_transport_request():
    try:
        data = request.get_json() or request.form
        farmer_name = data.get("farmer_name")
        farmer_phone = data.get("farmer_phone")
        village = data.get("village")
        ward = data.get("ward")
        district = data.get("district")
        crop_type = data.get("crop_type")
        quantity_bags = int(data.get("quantity_bags", 0))
        pickup_date = data.get("pickup_date")
        
        if not all([farmer_name, farmer_phone, village, ward, district, crop_type, quantity_bags, pickup_date]):
            return jsonify({"success": False, "data": None, "message": t("transport_fill_all")}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transport_requests 
            (farmer_name, farmer_phone, village, ward, district, crop_type, quantity_bags, pickup_date, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (farmer_name, farmer_phone, village, ward, district, crop_type, quantity_bags, pickup_date, 'open', datetime.now().isoformat())
        )
        req_id = cursor.lastrowid
        
        matches = find_matching_requests(conn, ward, district, crop_type, pickup_date, req_id)
        
        # Log notification
        create_notification(conn, f"Ombi jipya #REQ-{req_id} la {crop_type} limeundwa na {farmer_name} kule {village}.", req_id, "info")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True, 
            "data": {
                "request_id": req_id,
                "farmer_name": farmer_name,
                "crop_type": crop_type,
                "quantity_bags": quantity_bags,
                "pickup_date": pickup_date,
                "matches": matches
            }, 
            "message": t("transport_registered")
        })
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.get("/api/transport/pool/<ward>")
def api_transport_pools(ward):
    try:
        conn = get_db_connection()
        pools = conn.execute(
            "SELECT * FROM transport_pools WHERE status = 'open' AND (LOWER(route_from) LIKE ? OR LOWER(route_from) = ?)",
            (f"%{ward.lower()}%", ward.lower())
        ).fetchall()
        conn.close()
        data = [dict(row) for row in pools]
        return jsonify({"success": True, "data": data, "message": t("transport_pool_found", ward=ward)})
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.post("/api/transport/join/<int:pool_id>")
def api_join_pool(pool_id):
    try:
        data = request.get_json() or request.form
        farmer_name = data.get("farmer_name")
        farmer_phone = data.get("farmer_phone")
        bags = int(data.get("bags", 1))
        
        if not farmer_name or not farmer_phone:
            return jsonify({"success": False, "data": None, "message": t("transport_join_fill")}), 400
            
        conn = get_db_connection()
        pool = conn.execute("SELECT * FROM transport_pools WHERE id = ?", (pool_id,)).fetchone()
        
        if not pool:
            conn.close()
            return jsonify({"success": False, "data": None, "message": t("transport_not_found")}), 404
            
        if pool["available_slots"] < bags:
            conn.close()
            return jsonify({"success": False, "data": None, "message": t("transport_slots_insufficient", slots=pool["available_slots"])}), 400
            
        new_slots = pool["available_slots"] - bags
        new_status = 'matched' if new_slots == 0 else 'open'
        
        conn.execute(
            "UPDATE transport_pools SET available_slots = ?, status = ? WHERE id = ?",
            (new_slots, new_status, pool_id)
        )
        
        sms_msg = f"Ndugu {farmer_name}, umefanikiwa kujiunga na safari ya {pool['driver_name']} ({pool['driver_phone']}). Gharama ni TSh {bags * pool['cost_per_bag_tzs']:,}. Mzigo: mifuko {bags}."
        dispatch_notification(conn, sms_msg)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "pool_id": pool_id,
                "driver_name": pool["driver_name"],
                "driver_phone": pool["driver_phone"],
                "total_cost": bags * pool["cost_per_bag_tzs"],
                "sms_confirmation": sms_msg
            },
            "message": t("transport_join_success")
        })
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.get("/transport")
def transport_page():
    try:
        conn = get_db_connection()
        pools = conn.execute("SELECT * FROM transport_pools WHERE status = 'open'").fetchall()
        requests = conn.execute("SELECT * FROM transport_requests ORDER BY id DESC LIMIT 10").fetchall()
        conn.close()
        return render_template(
            "shamba_connect.html",
            pools=pools,
            requests=requests,
            active="transport",
            heading="Shamba Connect",
            subheading="Ungana na wakulima wenzako kusafirisha mazao kwa pamoja na kupunguza gharama."
        )
    except Exception as e:
        return render_template(
            "shamba_connect.html",
            pools=[],
            requests=[],
            error=str(e),
            active="transport",
            heading="Shamba Connect",
            subheading="Ungana na wakulima wenzako."
        )


# ============== FEATURE 3: MALANGO SALAMA (Safe M-Pesa Payment) ==============

def simulate_mpesa_payment(phone, amount):
    digits = "".join(random.choices("0123456789", k=8))
    return f"MPE{digits}"


@app.post("/api/payment/initiate")
def api_payment_initiate():
    try:
        data = request.get_json() or request.form
        buyer_name = data.get("buyer_name")
        buyer_phone = data.get("buyer_phone")
        farmer_name = data.get("farmer_name")
        farmer_phone = data.get("farmer_phone")
        crop_type = data.get("crop_type")
        quantity_kg = float(data.get("quantity_kg", 0))
        amount_tzs = float(data.get("amount_tzs", 0))
        
        if not all([buyer_name, buyer_phone, farmer_name, farmer_phone, crop_type, quantity_kg, amount_tzs]):
            return jsonify({"success": False, "data": None, "message": "Tafadhali jaza sehemu zote za malipo."}), 400
            
        ref = simulate_mpesa_payment(buyer_phone, amount_tzs)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions 
            (buyer_name, buyer_phone, farmer_name, farmer_phone, crop_type, quantity_kg, amount_tzs, mpesa_reference, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (buyer_name, buyer_phone, farmer_name, farmer_phone, crop_type, quantity_kg, amount_tzs, ref, 'escrowed', datetime.now().isoformat())
        )
        tx_id = cursor.lastrowid
        
        # Log simulated notification
        msg = f"MALIPO SALAMA: TSh {amount_tzs:,} kutoka kwa {buyer_name} yamepokelewa na kuwekwa dhamana (Escrow) kwa ajili ya {farmer_name}. Ref: {ref}."
        create_notification(conn, msg, None, "success")
        
        # Trigger SMS notification to farmer
        sms_msg = f"AgriMove: Malipo ya TSh {amount_tzs:,} kutoka kwa Mnunuzi {buyer_name} yamepokelewa salama kwenye mfuko wa dhamana. Ref: {ref}. Yatatumwa kwako punde utakapothibitisha mzigo kupokelewa."
        dispatch_notification(conn, sms_msg)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "transaction_id": tx_id,
                "mpesa_reference": ref,
                "status": "escrowed",
                "sms_text": sms_msg
            },
            "message": "Malipo yamewekwa dhamana (Escrow) kwa ufanisi!"
        })
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.post("/api/payment/confirm")
def api_payment_confirm():
    try:
        data = request.get_json() or request.form
        tx_id = data.get("transaction_id")
        
        if not tx_id:
            return jsonify({"success": False, "data": None, "message": "Namba ya muamala inahitajika."}), 400
            
        conn = get_db_connection()
        tx = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,)).fetchone()
        if not tx:
            conn.close()
            return jsonify({"success": False, "data": None, "message": "Muamala haukupatikana."}), 404
            
        conn.execute(
            "UPDATE transactions SET status = 'released' WHERE id = ?",
            (tx_id,)
        )
        
        # Log notification
        msg = f"MALIPO SALAMA: Pesa TSh {tx['amount_tzs']:,} zimeachiwa kwa mkulima {tx['farmer_name']}. Ref: {tx['mpesa_reference']}."
        create_notification(conn, msg, None, "success")
        
        # Trigger SMS to farmer
        sms_msg = f"AgriMove: Malipo ya dhamana ya TSh {tx['amount_tzs']:,} yameachiwa na mnunuzi na kutumwa kwenye namba yako ya M-Pesa. Ref: {tx['mpesa_reference']}."
        dispatch_notification(conn, sms_msg)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "transaction_id": tx_id,
                "status": "released",
                "sms_text": sms_msg
            },
            "message": "Gharama zimelipwa kwa mkulima na muamala umekamilika!"
        })
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.get("/api/payment/status/<int:tx_id>")
def api_payment_status(tx_id):
    try:
        conn = get_db_connection()
        tx = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,)).fetchone()
        conn.close()
        if not tx:
            return jsonify({"success": False, "data": None, "message": "Muamala haukupatikana."}), 404
        return jsonify({"success": True, "data": dict(tx), "message": "Hali ya muamala imepatikana."})
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.get("/payments")
def payments_page():
    try:
        conn = get_db_connection()
        transactions = conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 15").fetchall()
        conn.close()
        return render_template(
            "malango_salama.html",
            transactions=transactions,
            active="payments",
            heading="Malango Salama",
            subheading="Lipa na upokee malipo salama kwa kutumia M-Pesa Escrow bila hofu ya kupoteza fedha."
        )
    except Exception as e:
        return render_template(
            "malango_salama.html",
            transactions=[],
            error=str(e),
            active="payments",
            heading="Malango Salama",
            subheading="Lipa na upokee malipo salama."
        )


# ============== FEATURE 4: HIFADHI YANGU (Storage Finder) ==============

@app.get("/api/storage")
def api_storage_all():
    try:
        conn = get_db_connection()
        facilities = conn.execute("SELECT * FROM storage_facilities ORDER BY name").fetchall()
        conn.close()
        data = [dict(row) for row in facilities]
        return jsonify({"success": True, "data": data, "message": "Ghala zote zimepatikana."})
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.get("/api/storage/<region>")
def api_storage_by_region(region):
    try:
        conn = get_db_connection()
        facilities = conn.execute(
            "SELECT * FROM storage_facilities WHERE LOWER(region) = ? ORDER BY name",
            (region.lower(),)
        ).fetchall()
        conn.close()
        data = [dict(row) for row in facilities]
        return jsonify({"success": True, "data": data, "message": f"Ghala za mkoa wa {region} zimepatikana."})
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.get("/api/storage/nearest")
def api_storage_nearest():
    try:
        lat_str = request.args.get("lat")
        lng_str = request.args.get("lng")
        if not lat_str or not lng_str:
            return jsonify({"success": False, "data": None, "message": "Kigezo cha lat na lng kinahitajika."}), 400
            
        lat = float(lat_str)
        lng = float(lng_str)
        
        conn = get_db_connection()
        facilities = conn.execute("SELECT * FROM storage_facilities").fetchall()
        conn.close()
        
        import math
        data = []
        for row in facilities:
            d_row = dict(row)
            dist_km = math.sqrt((lat - d_row["gps_lat"])**2 + (lng - d_row["gps_lng"])**2) * 111.0
            d_row["distance_km"] = round(dist_km, 2)
            data.append(d_row)
            
        data.sort(key=lambda x: x["distance_km"])
        
        return jsonify({"success": True, "data": data, "message": "Ghala za karibu zaidi zimepatikana."})
    except Exception as e:
        return jsonify({"success": False, "data": None, "message": f"Hitilafu: {str(e)}"}), 500


@app.get("/storage")
def storage_page():
    try:
        conn = get_db_connection()
        facilities = conn.execute("SELECT * FROM storage_facilities ORDER BY name").fetchall()
        
        regions_rows = conn.execute("SELECT DISTINCT region FROM storage_facilities ORDER BY region").fetchall()
        regions = [r["region"] for r in regions_rows]
        
        conn.close()
        return render_template(
            "hifadhi_yangu.html",
            facilities=facilities,
            regions=regions,
            active="storage",
            heading="Hifadhi Yangu",
            subheading="Tafuta maghala ya karibu ya kuhifadhia mazao yako na mifumo ya Warehouse Receipt (WRS)."
        )
    except Exception as e:
        return render_template(
            "hifadhi_yangu.html",
            facilities=[],
            regions=[],
            error=str(e),
            active="storage",
            heading="Hifadhi Yangu",
            subheading="Tafuta maghala."
        )


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
    flash(t("rating_thanks"), "success")
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
    """Create notification in database (caller commits)."""
    conn.execute(
        "INSERT INTO notifications (request_id, message, type, created_at) VALUES (?, ?, ?, ?)",
        (request_id, message, notification_type, datetime.now().isoformat()),
    )


ADMIN_PRICE_LIMIT = 2


def get_admin_prices(conn):
    """Return the two featured prices shown on the admin dashboard."""
    return conn.execute(
        """
        SELECT * FROM market_prices
        ORDER BY updated_at DESC, id DESC
        LIMIT ?
        """,
        (ADMIN_PRICE_LIMIT,),
    ).fetchall()


@app.route("/admin")
def admin_dashboard():
    """Main admin dashboard with price and buyer management data."""
    conn = get_db_connection()
    drivers = conn.execute("SELECT * FROM drivers ORDER BY name").fetchall()
    buyers = conn.execute("SELECT * FROM trusted_buyers ORDER BY buyer_name").fetchall()
    prices = get_admin_prices(conn)
    driver_total = len(drivers) or 1
    active_drivers = len(
        [d for d in drivers if d["availability"] == "available"]
    )
    conn.close()

    return render_template(
        "admin_dashboard.html",
        active="admin",
        heading=t("admin_heading"),
        subheading=t("admin_subheading"),
        drivers=drivers,
        active_drivers=active_drivers,
        fleet_availability_pct=int((active_drivers / driver_total) * 100),
        buyers=buyers,
        prices=prices,
        price_slots=ADMIN_PRICE_LIMIT,
        active_tab=request.args.get("tab", "prices"),
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
        active="analytics",
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
        flash(t("fill_all_fields"), "danger")
        return redirect(url_for("admin_dashboard", tab="prices"))
        
    try:
        price_val = float(price)
        conn = get_db_connection()
        existing = conn.execute(
            "SELECT id FROM market_prices WHERE crop_name = ? AND region = ?",
            (crop, region),
        ).fetchone()
        total = conn.execute("SELECT COUNT(*) FROM market_prices").fetchone()[0]
        if not existing and total >= ADMIN_PRICE_LIMIT:
            conn.close()
            flash(t("price_limit_reached"), "error")
            return redirect(url_for("admin_dashboard", tab="prices"))

        conn.execute(
            """INSERT OR REPLACE INTO market_prices (crop_name, region, price, demand_level, trend, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (crop, region, price_val, demand, trend, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        flash(t("price_added", crop=crop, region=region), "success")
    except ValueError:
        flash(t("invalid_price"), "danger")

    return redirect(url_for("admin_dashboard", tab="prices"))


@app.post("/admin/prices/edit")
def admin_edit_price():
    price_id = request.form.get("price_id")
    price = request.form.get("price", "0").strip()
    demand = request.form.get("demand_level", "Medium")
    trend = request.form.get("trend", "Stable")
    
    if not price_id or not price:
        flash(t("missing_price_details"), "danger")
        return redirect(url_for("admin_dashboard", tab="prices"))
        
    try:
        price_val = float(price)
        conn = get_db_connection()
        conn.execute(
            "UPDATE market_prices SET price = ?, demand_level = ?, trend = ?, updated_at = ? WHERE id = ?",
            (price_val, demand, trend, datetime.now().isoformat(), price_id)
        )
        conn.commit()
        conn.close()
        flash(t("price_updated"), "success")
    except ValueError:
        flash(t("invalid_price"), "danger")
        
    return redirect(url_for("admin_dashboard", tab="prices"))


@app.post("/admin/prices/delete/<int:price_id>")
def admin_delete_price(price_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM market_prices WHERE id = ?", (price_id,))
    conn.commit()
    conn.close()
    flash(t("price_deleted"), "success")
    return redirect(url_for("admin_dashboard", tab="prices"))


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
    flash(t("buyer_status_updated", status=status), "success")
    return redirect(url_for("admin_dashboard"))



# ============== DEMO RESET ROUTE ==============

@app.get("/setup-demo")
def setup_demo():
    """
    Hackathon demo reset: clears and reseeds ALL tables with realistic
    Tanzanian sample data. Visit /setup-demo in a browser to trigger.
    """
    conn = get_db_connection()
    now = datetime.now().isoformat(timespec="seconds")

    try:
        # ── 1. Clear all seeded tables (order respects FK constraints) ──
        for tbl in [
            "notifications", "tracking", "requests",
            "price_alerts", "buyer_offers", "profit_estimates",
            "trusted_buyers", "market_prices",
            "transactions", "transport_pools", "transport_requests",
            "storage_facilities", "drivers", "farmers",
        ]:
            conn.execute(f"DELETE FROM {tbl}")
            conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{tbl}'")

        # ── 2. Farmers ──
        farmers = [
            ("Amina Mwangi",    "+255 712 111 001", 4.8, 12, 10, now, 340),
            ("Juma Kikwete",    "+255 754 222 002", 4.5, 8,  7,  now, 210),
            ("Grace Msellem",   "+255 689 333 003", 4.9, 20, 18, now, 580),
            ("Hassan Nyerere",  "+255 763 444 004", 4.2, 5,  4,  now, 120),
            ("Fatuma Salim",    "+255 621 555 005", 4.7, 15, 13, now, 420),
        ]
        conn.executemany(
            """INSERT INTO farmers
               (name, phone, rating, total_requests, total_delivered, member_since, points)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            farmers,
        )

        # ── 3. Drivers ──
        drivers = [
            ("Serikali Mwamba",   "+255 712 600 101", "available", 4.9, 210, 6, 4_200_000, "truck"),
            ("Baraka Juma",       "+255 754 600 102", "available", 4.7, 145, 4, 2_900_000, "truck"),
            ("Neema Odhiambo",    "+255 689 600 103", "available", 4.6,  98, 3, 1_960_000, "van"),
            ("Daniel Msigwa",     "+255 763 600 104", "busy",       4.5,  67, 2, 1_340_000, "pickup"),
        ]
        conn.executemany(
            """INSERT INTO drivers
               (name, phone, availability, rating, total_deliveries, completed_today, earnings, vehicle_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            drivers,
        )

        # ── 4. Delivery requests ──
        sample_requests = [
            (1, "Morogoro Farm Gate",    "Dar es Salaam",  "Maize",    "50 bags",    "Delivered",   1, 45,  42, 280.0, 1_950_000, now),
            (2, "Mvomero Cooperative",   "Dodoma",         "Rice",     "30 bags",    "In Transit",  2, 90,  None, 320.0, 1_600_000, now),
            (3, "Ifakara Collection Point","Mwanza",        "Beans",    "20 bags",    "Accepted",    3, 120, None, 410.0, 1_200_000, now),
            (4, "Moshi Highland Farms",  "Arusha",         "Tomatoes", "15 bags",    "Pending",     None, None, None, 80.0, 600_000, now),
            (5, "Morogoro Farm Gate",    "Nairobi",        "Maize",    "100 bags",   "Delivered",   1, 180, 175, 640.0, 6_400_000, now),
        ]
        conn.executemany(
            """INSERT INTO requests
               (farmer_id, pickup_location, destination, goods_type, quantity,
                status, driver_id, eta_minutes, actual_time, distance_km, price, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            sample_requests,
        )

        # ── 5. Notifications ──
        notifs = [
            (1, "Delivery completed! Maize delivered to Dar es Salaam.", "success", now),
            (2, "Your goods are on the way. Driver: Baraka Juma.",       "info",    now),
            (3, "Driver assigned. ETA: 120 minutes.",                     "info",    now),
            (4, "Request received. Searching for available drivers.",     "info",    now),
        ]
        conn.executemany(
            "INSERT INTO notifications (request_id, message, type, created_at) VALUES (?,?,?,?)",
            notifs,
        )

        # ── 6. Market prices (Bei za Soko) ──
        tz_prices = [
            # (crop_name, crop_name_swahili, region, market_name, price, price_per_kg_tzs, demand_level, trend, price_trend)
            ("Maize",    "Mahindi",  "Dar es Salaam", "Kariakoo Market",   95_000, 950,  "High",   "Rising", "up",     now),
            ("Maize",    "Mahindi",  "Arusha",        "Arusha Market",     88_000, 880,  "Medium", "Stable", "stable", now),
            ("Maize",    "Mahindi",  "Mwanza",        "Mwanza Market",     82_000, 820,  "Medium", "Stable", "stable", now),
            ("Maize",    "Mahindi",  "Mbeya",         "Mbeya Market",      78_000, 780,  "Low",    "Falling","down",   now),
            ("Maize",    "Mahindi",  "Dodoma",        "Dodoma Market",     90_000, 900,  "High",   "Rising", "up",     now),
            ("Rice",     "Mpunga",   "Dar es Salaam", "Kariakoo Market",  200_000,2000,  "High",   "Rising", "up",     now),
            ("Rice",     "Mpunga",   "Arusha",        "Arusha Market",    185_000,1850,  "Medium", "Stable", "stable", now),
            ("Rice",     "Mpunga",   "Mwanza",        "Mwanza Market",    175_000,1750,  "Medium", "Falling","down",   now),
            ("Rice",     "Mpunga",   "Mbeya",         "Mbeya Market",     170_000,1700,  "Low",    "Stable", "stable", now),
            ("Rice",     "Mpunga",   "Dodoma",        "Dodoma Market",    195_000,1950,  "High",   "Rising", "up",     now),
            ("Cassava",  "Muhogo",   "Dar es Salaam", "Kariakoo Market",   55_000, 550,  "High",   "Stable", "stable", now),
            ("Cassava",  "Muhogo",   "Mwanza",        "Mwanza Market",     45_000, 450,  "Medium", "Falling","down",   now),
            ("Tomatoes", "Nyanya",   "Dar es Salaam", "Kariakoo Market",  150_000,1500,  "High",   "Rising", "up",     now),
            ("Tomatoes", "Nyanya",   "Arusha",        "Arusha Market",    130_000,1300,  "Medium", "Stable", "stable", now),
            ("Tomatoes", "Nyanya",   "Dodoma",        "Dodoma Market",    140_000,1400,  "High",   "Rising", "up",     now),
            ("Onions",   "Vitunguu", "Dar es Salaam", "Kariakoo Market",  180_000,1800,  "High",   "Rising", "up",     now),
            ("Onions",   "Vitunguu", "Arusha",        "Arusha Market",    160_000,1600,  "Medium", "Stable", "stable", now),
            ("Coffee",   "Kahawa",   "Arusha",        "Arusha Auction",   850_000,8500,  "High",   "Rising", "up",     now),
            ("Coffee",   "Kahawa",   "Mbeya",         "Mbeya Market",     820_000,8200,  "High",   "Stable", "stable", now),
            ("Cashews",  "Korosho",  "Dar es Salaam", "Kariakoo Market",  600_000,6000,  "High",   "Rising", "up",     now),
            ("Cashews",  "Korosho",  "Mtwara",        "Mtwara Port",      550_000,5500,  "Medium", "Stable", "stable", now),
            ("Beans",    "Maharagwe","Dar es Salaam", "Kariakoo Market",  180_000,1800,  "High",   "Rising", "up",     now),
            ("Beans",    "Maharagwe","Dodoma",        "Dodoma Market",    165_000,1650,  "Medium", "Stable", "stable", now),
        ]
        conn.executemany(
            """INSERT OR IGNORE INTO market_prices
               (crop_name, crop_name_swahili, region, market_name, price,
                price_per_kg_tzs, demand_level, trend, price_trend, updated_at, last_updated)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            [(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[9]) for r in tz_prices],
        )

        # ── 7. Transport pools (Shamba Connect) ──
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day2      = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        pools = [
            (200, "Baraka Juma",     "+255 754 600 102", "Morogoro",  "Dar es Salaam",  tomorrow,  800,  80, "open"),
            (150, "Serikali Mwamba", "+255 712 600 101", "Moshi",     "Arusha",         tomorrow, 1000,  60, "open"),
            (300, "Daniel Msigwa",   "+255 763 600 104", "Iringa",    "Dar es Salaam",  day2,      750, 120, "open"),
            (100, "Neema Odhiambo",  "+255 689 600 103", "Dodoma",    "Mwanza",         day2,     1200,  40, "open"),
        ]
        conn.executemany(
            """INSERT INTO transport_pools
               (truck_capacity_bags, driver_name, driver_phone, route_from, route_to,
                departure_date, cost_per_bag_tzs, available_slots, status)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            pools,
        )

        # ── 8. Transport requests ──
        tr_requests = [
            ("Amina Mwangi",  "+255 712 111 001", "Kimara",    "Kimara",    "Ilala",    "Maize",   40, tomorrow, "open", now),
            ("Juma Kikwete",  "+255 754 222 002", "Kibosho",   "Kibosho",   "Moshi",    "Coffee",  20, tomorrow, "open", now),
            ("Grace Msellem", "+255 689 333 003", "Mafinga",   "Mafinga",   "Iringa",   "Beans",   60, day2,     "open", now),
            ("Hassan Nyerere","+255 763 444 004", "Chamwino",  "Chamwino",  "Dodoma",   "Rice",    35, day2,     "open", now),
        ]
        conn.executemany(
            """INSERT INTO transport_requests
               (farmer_name, farmer_phone, village, ward, district, crop_type,
                quantity_bags, pickup_date, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            tr_requests,
        )

        # ── 9. Transactions / Malango Salama ──
        txns = [
            ("Salim Corp",       "+255 712 999 111", "Amina Mwangi",  "+255 712 111 001",
             "Maize",   500, 475_000, "MP-2024-001", "released",  now),
            ("Mwangi Traders",   "+254 722 888 222", "Grace Msellem", "+255 689 333 003",
             "Beans",   200, 360_000, "MP-2024-002", "pending",   now),
            ("Dodoma Harvests",  "+255 688 111 222", "Juma Kikwete",  "+255 754 222 002",
             "Rice",    150, 300_000, "MP-2024-003", "confirmed", now),
            ("Kigali Wholesalers","+250 788 333 444","Fatuma Salim",  "+255 621 555 005",
             "Coffee",   50, 425_000, "MP-2024-004", "pending",   now),
        ]
        conn.executemany(
            """INSERT INTO transactions
               (buyer_name, buyer_phone, farmer_name, farmer_phone, crop_type,
                quantity_kg, amount_tzs, mpesa_reference, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            txns,
        )

        # ── 10. Storage facilities (Hifadhi Yangu) ──
        stores = [
            ("Kariakoo Cold Store",   "cold_storage",   "Dar es Salaam","Ilala",   "Kariakoo",   -6.8161, 39.2780, 500,  180, "+255 22 218 0001", 3_500, 1),
            ("Arusha Grain Depot",    "warehouse",      "Arusha",       "Arusha",  "Sakina",     -3.3670, 36.6956, 800,  400, "+255 27 254 3322", 2_800, 1),
            ("Mwanza Lake Store",     "warehouse",      "Mwanza",       "Nyamagana","Mbugani",   -2.5100, 32.9105, 300,   90, "+255 28 250 0110", 2_200, 0),
            ("Mbeya Highland Silo",   "silo",           "Mbeya",        "Mbeya",   "Forest",     -8.9060, 33.4440, 1200, 700, "+255 25 250 1234", 1_800, 1),
            ("Dodoma Central Store",  "warehouse",      "Dodoma",       "Dodoma",  "Makole",     -6.1800, 35.7400, 600,  250, "+255 26 232 0089", 2_500, 0),
            ("Morogoro Farmers Hub",  "warehouse",      "Morogoro",     "Morogoro","Mazimbu",    -6.8210, 37.6610, 400,  200, "+255 23 261 4456", 2_000, 1),
            ("Iringa Grain Centre",   "silo",           "Iringa",       "Iringa",  "Mlandege",   -7.7700, 35.7000, 700,  380, "+255 26 270 2233", 1_900, 1),
        ]
        conn.executemany(
            """INSERT INTO storage_facilities
               (name, facility_type, region, district, village, gps_lat, gps_lng,
                capacity_tons, available_tons, contact_phone, cost_per_bag_per_month_tzs, accepts_wrs)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            stores,
        )

        # ── 11. Trusted buyers ──
        t_buyers = [
            (1, "Salim Corp",          "+255 712 999 111", "Verified", "Admin", now, 4.5, 34),
            (2, "Mwangi Traders",      "+254 722 888 222", "Verified", "Admin", now, 4.8, 120),
            (3, "Dodoma Harvests",     "+255 688 111 222", "Pending",  None,    now, 4.2, 12),
            (4, "Kigali Wholesalers",  "+250 788 333 444", "Verified", "Admin", now, 4.9, 210),
        ]
        conn.executemany(
            """INSERT OR IGNORE INTO trusted_buyers
               (buyer_id, buyer_name, phone, verification_status, verified_by, verified_at,
                rating, total_purchases, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            [(b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7],now) for b in t_buyers],
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": (
                "Demo reset complete! Seeded: 5 farmers, 4 drivers, 5 delivery requests, "
                "23 market prices (Bei za Soko), 4 transport pools, 4 transport requests, "
                "4 M-Pesa transactions, 7 storage facilities, 4 trusted buyers."
            ),
            "data": {
                "farmers": 5,
                "drivers": 4,
                "delivery_requests": 5,
                "market_prices": 23,
                "transport_pools": 4,
                "transport_requests": 4,
                "transactions": 4,
                "storage_facilities": 7,
                "trusted_buyers": 4,
            },
            "navigate": {
                "home":             "/",
                "bei_za_soko":      "/market-prices",
                "shamba_connect":   "/transport",
                "malango_salama":   "/payments",
                "hifadhi_yangu":    "/storage",
                "admin":            "/admin",
            }
        })

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "message": str(e), "data": {}}), 500


# ============== IVR VOICE — Africa's Talking (Feature Phones / 2G / No Internet) ==============

def save_transport_callback(phone):
    """Save caller number for transport callback"""
    import sqlite3
    conn = sqlite3.connect(DATABASE)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS transport_callbacks (
           phone TEXT UNIQUE,
           created_at TEXT)"""
    )
    conn.execute(
        """INSERT OR IGNORE INTO transport_callbacks 
           (phone, created_at) VALUES (?, datetime('now'))""",
        (phone,)
    )
    conn.commit()
    conn.close()


def get_price_from_db(crop_key):
    # Map Swahili crop keys to English
    mapping = {
        'mahindi': 'Maize',
        'mpunga': 'Rice',
        'nyanya': 'Tomatoes',
        'vitunguu': 'Beans'
    }
    english_name = mapping.get(crop_key.lower(), 'Maize')
    
    prices = {}
    try:
        conn = get_db_connection()
        for region in ['Dar es Salaam', 'Arusha', 'Mbeya', 'Dodoma']:
            row = conn.execute(
                "SELECT price FROM market_prices WHERE (LOWER(crop_name) = ? OR LOWER(crop_name_swahili) = ?) AND LOWER(region) = ?",
                (english_name.lower(), english_name.lower(), region.lower())
            ).fetchone()
            if row:
                prices[region.lower().replace(" ", "")] = int(row['price'] / 100)
        conn.close()
    except Exception as e:
        print(f"Error querying price: {e}")
        
    if 'daressalaam' in prices:
        prices['kariakoo'] = prices['daressalaam']
    if 'kariakoo' not in prices:
        prices['kariakoo'] = 950 if english_name == 'Maize' else 1500
    if 'arusha' not in prices:
        prices['arusha'] = 880 if english_name == 'Maize' else 1400
    if 'mbeya' not in prices:
        prices['mbeya'] = 850 if english_name == 'Maize' else 1350
        
    return prices


def get_storage_from_db(region):
    try:
        conn = get_db_connection()
        row = conn.execute(
            "SELECT * FROM storage_facilities WHERE LOWER(region) = ? ORDER BY id DESC LIMIT 1",
            (region.lower(),)
        ).fetchone()
        conn.close()
        if row:
            return {
                'name': row['name'],
                'available': row['available_tons'],
                'cost': row['cost_per_bag_per_month_tzs'],
                'phone': row['contact_phone']
            }
    except Exception as e:
        print(f"Error querying storage: {e}")
        
    defaults = {
        'Mbeya': {
            'name': 'Ghala la Ushirika Mbeya',
            'available': 120,
            'cost': 1500,
            'phone': '0754 111 222'
        },
        'Arusha': {
            'name': 'Arusha Grains Silo',
            'available': 80,
            'cost': 1800,
            'phone': '0784 333 444'
        },
        'Dar es Salaam': {
            'name': 'Kurasini Cold Storage',
            'available': 45,
            'cost': 2500,
            'phone': '0715 555 666'
        },
        'Dodoma': {
            'name': 'Dodoma National Reserve',
            'available': 300,
            'cost': 1200,
            'phone': '0768 777 888'
        }
    }
    return defaults.get(region, {
        'name': f'Ghala la Mkoa wa {region}',
        'available': 50,
        'cost': 2000,
        'phone': '0800 000 000'
    })


@app.route('/voice', methods=['POST', 'GET'])
def ivr_handler():
    """
    Africa's Talking calls this when farmer dials your number.
    We respond with XML that tells AT what to say and do.
    """
    response = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <GetDigits timeout="15" 
                   finishOnKey="#" 
                   callbackUrl="/voice/handle">
            <Say voice="woman" playBeep="false">
                Karibu AgriMove Tanzania. 
                Msaada wa wakulima.
                Bonyeza moja kwa bei za mazao.
                Bonyeza mbili kwa kutafuta gari.
                Bonyeza tatu kwa hifadhi karibu nawe.
                Bonyeza nne kuzungumza na wakala.
                Kisha bonyeza gridi.
            </Say>
        </GetDigits>
    </Response>"""
    return response, 200, {'Content-Type': 'text/plain'}


@app.route('/voice/handle', methods=['POST'])
def ivr_handle():
    """Handle farmer's keypad selection"""
    digits = request.form.get('dtmfDigits', '')
    caller = request.form.get('callerNumber', '')
    
    if digits == '1':
        response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <GetDigits timeout="10" 
                       finishOnKey="#"
                       callbackUrl="/voice/prices">
                <Say voice="woman">
                    Bei za mazao leo.
                    Bonyeza moja kwa mahindi.
                    Bonyeza mbili kwa mpunga.
                    Bonyeza tatu kwa nyanya.
                    Bonyeza nne kwa vitunguu.
                    Kisha bonyeza gridi.
                </Say>
            </GetDigits>
        </Response>"""
    
    elif digits == '2':
        response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">
                Huduma ya kutafuta gari.
                Tutakupigia simu ndani ya dakika kumi
                kukuunganisha na gari karibu nawe.
                Nambari yako imehifadhiwa.
                Asante kwa kutumia AgriMove Tanzania.
            </Say>
        </Response>"""
        save_transport_callback(caller)
    
    elif digits == '3':
        response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <GetDigits timeout="10"
                       finishOnKey="#"
                       callbackUrl="/voice/storage">
                <Say voice="woman">
                    Hifadhi karibu nawe.
                    Bonyeza moja kwa Mbeya.
                    Bonyeza mbili kwa Arusha.
                    Bonyeza tatu kwa Dar es Salaam.
                    Bonyeza nne kwa Dodoma.
                    Kisha bonyeza gridi.
                </Say>
            </GetDigits>
        </Response>"""
    
    elif digits == '4':
        response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">
                Tunakupeleka kwa wakala wetu.
                Subiri kidogo tafadhali.
            </Say>
            <Dial record="false">
                <Number>+255XXXXXXXXX</Number>
            </Dial>
        </Response>"""
    
    else:
        response = """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Redirect>/voice</Redirect>
        </Response>"""
    
    return response, 200, {'Content-Type': 'text/plain'}


@app.route('/voice/prices', methods=['POST'])
def ivr_prices():
    """Speak crop price when farmer selects crop"""
    digits = request.form.get('dtmfDigits', '')
    
    crops = {
        '1': ('Mahindi', 'mahindi'),
        '2': ('Mpunga', 'mpunga'),
        '3': ('Nyanya', 'nyanya'),
        '4': ('Vitunguu', 'vitunguu')
    }
    
    crop_display, crop_key = crops.get(
        digits, ('Mahindi', 'mahindi')
    )
    
    price = get_price_from_db(crop_key)
    
    price_text = f"""Bei ya {crop_display} leo.
        Kariakoo Dar es Salaam, 
        shilingi {price.get('kariakoo', 600)} kwa kilo.
        Soko la Arusha, 
        shilingi {price.get('arusha', 550)} kwa kilo.
        Soko la Mbeya, 
        shilingi {price.get('mbeya', 500)} kwa kilo.
        Asante kwa kutumia AgriMove Tanzania.
        Piga tena kupata bei nyingine."""
    
    response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="woman">{price_text}</Say>
        <Redirect>/voice</Redirect>
    </Response>"""
    
    return response, 200, {'Content-Type': 'text/plain'}


@app.route('/voice/storage', methods=['POST'])
def ivr_storage():
    """Speak storage info for selected region"""
    digits = request.form.get('dtmfDigits', '')
    
    regions = {
        '1': 'Mbeya', '2': 'Arusha',
        '3': 'Dar es Salaam', '4': 'Dodoma'
    }
    region = regions.get(digits, 'Mbeya')
    storage = get_storage_from_db(region)
    
    text = f"""Hifadhi katika {region}.
        Jina: {storage.get('name', 'Ghala la Mkoa')}.
        Nafasi iliyobaki: 
        tani {storage.get('available', 50)}.
        Bei: shilingi 
        {storage.get('cost', 2000)} kwa gunia kwa mwezi.
        Piga simu: {storage.get('phone', '0800 000 000')}.
        Asante. Tutaonana tena."""
    
    response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="woman">{text}</Say>
    </Response>"""
    
    return response, 200, {'Content-Type': 'text/plain'}


if __name__ == "__main__":
    app.run(debug=True)

