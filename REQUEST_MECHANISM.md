# 🔄 AgriMove AI - Complete Request & Approval Mechanism

## 📊 System Overview Diagram

```
FARMER SUBMITS REQUEST
        ↓
   [Database: requests table created]
   [AI assigns nearest driver]
   [ETA calculated]
        ↓
NOTIFICATION SENT
        ↓
DRIVER SEES PENDING REQUEST
        ↓
DRIVER CLICKS "ACCEPT JOB"
        ↓
[Status changes: Pending → Accepted]
[Driver marked as "busy"]
   [Notification updated]
        ↓
DRIVER CLICKS "START DELIVERY"
        ↓
[Status changes: Accepted → In Transit]
   [Notification sent]
        ↓
DRIVER CLICKS "MARK DELIVERED"
        ↓
[Status changes: In Transit → Delivered]
[Driver marked as "available" again]
   [Notification sent]
        ↓
CYCLE COMPLETE ✅
```

---

## 📝 STEP 1: FARMER SUBMITS REQUEST

### **What Farmer Does:**
1. Go to http://127.0.0.1:5000/farmer
2. Fill form:
   - Farmer Name
   - Phone Number
   - Pickup Location
   - Destination
   - Goods Type
   - Quantity
3. Click "Request Transport" button

### **What Happens in Backend:**

#### **Route Handler** (app.py - Line ~170)
```python
@app.route("/farmer", methods=["GET", "POST"])
def farmer_dashboard():
    if request.method == "POST":
        # STEP 1: Extract form data
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        pickup = request.form.get("pickup_location", "").strip()
        destination = request.form.get("destination", "").strip()
        goods_type = request.form.get("goods_type", "").strip()
        quantity = request.form.get("quantity", "").strip()
```

#### **STEP 2: Check if Farmer Exists**
```python
conn = get_db_connection()
farmer = conn.execute(
    "SELECT id FROM farmers WHERE phone = ?", (phone,)
).fetchone()

if farmer:
    farmer_id = farmer["id"]  # Existing farmer
else:
    # New farmer - insert into database
    farmer_id = conn.execute(
        "INSERT INTO farmers (name, phone) VALUES (?, ?)", 
        (name, phone)
    ).lastrowid
```

#### **Database Action:**
```
farmers table:
┌────┬──────────────┬──────────────────┐
│ id │ name         │ phone            │
├────┼──────────────┼──────────────────┤
│ 1  │ John Doe     │ +233555123456    │
└────┴──────────────┴──────────────────┘
```

---

## 🤖 STEP 2: AI ASSIGNS DRIVER (Automatic)

### **What Happens:**
The system uses AI simulation to find the "nearest" available driver.

#### **Code** (app.py - Line ~105)
```python
def assign_driver(conn):
    # Get all available drivers
    drivers = conn.execute(
        "SELECT * FROM drivers WHERE availability = 'available'"
    ).fetchall()
    
    if not drivers:
        return None, None  # No drivers available
    
    # SIMULATE DISTANCE: Random 6-45 km
    distances = {
        driver["id"]: random.randint(6, 45) 
        for driver in drivers
    }
    
    # SELECT NEAREST DRIVER
    selected = min(drivers, key=lambda driver: distances[driver["id"]])
    
    # CALCULATE ETA: distance * speed + overhead
    eta = distances[selected["id"]] * random.randint(2, 4) + random.randint(12, 28)
    
    return selected, eta  # Returns (driver_object, eta_in_minutes)
```

**Example:**
```
Driver 1 (Kwame): 12 km → ETA: 12*3 + 20 = 56 minutes
Driver 2 (Amina):  8 km → ETA: 8*2 + 15 = 31 minutes ✅ SELECTED (closest)
Driver 3 (Tunde): 25 km → ETA: 25*3 + 22 = 97 minutes
```

---

## 💾 STEP 3: CREATE REQUEST IN DATABASE

#### **Code:**
```python
request_id = conn.execute(
    """
    INSERT INTO requests (
        farmer_id, 
        pickup_location, 
        destination, 
        goods_type, 
        quantity,
        status,           # "Pending"
        driver_id,        # Auto-assigned
        eta_minutes,      # 31 min (example)
        created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        farmer_id,        # 1
        pickup,           # "Kumasi Village"
        destination,      # "Central Market"
        goods_type,       # "Tomatoes"
        quantity,         # "50 crates"
        "Pending",        # Initial status
        driver_id,        # 2 (Amina)
        eta,              # 31
        datetime.utcnow().isoformat()  # Timestamp
    ),
).lastrowid
```

#### **Database Result:**
```
requests table:
┌────┬───────────┬──────────────────┬──────────────────┬────────┬──────────┬──────────────┬─────────────┐
│ id │ farmer_id │ pickup_location  │ destination      │ goods  │ quantity │ driver_id    │ status      │
├────┼───────────┼──────────────────┼──────────────────┼────────┼──────────┼──────────────┼─────────────┤
│ 1  │ 1         │ Kumasi Village   │ Central Market   │ Tomato │ 50 crate │ 2 (Amina)    │ "Pending"   │
└────┴───────────┴──────────────────┴──────────────────┴────────┴──────────┴──────────────┴─────────────┘
```

---

## 📱 STEP 4: MARK DRIVER AS BUSY

#### **Code:**
```python
# Update driver availability
conn.execute(
    "UPDATE drivers SET availability = 'busy' WHERE id = ?", 
    (driver_id,)
)
```

#### **Database Before:**
```
drivers table:
┌────┬───────┬──────────────────┬──────────────┐
│ id │ name  │ phone            │ availability │
├────┼───────┼──────────────────┼──────────────┤
│ 2  │ Amina │ +254712490330    │ "available"  │
└────┴───────┴──────────────────┴──────────────┘
```

#### **Database After:**
```
┌────┬───────┬──────────────────┬──────────────┐
│ id │ name  │ phone            │ availability │
├────┼───────┼──────────────────┼──────────────┤
│ 2  │ Amina │ +254712490330    │ "busy"       │ ← Changed!
└────┴───────┴──────────────────┴──────────────┘
```

---

## 🔔 STEP 5: CREATE NOTIFICATION

#### **Code:**
```python
dispatch_notification(
    conn,
    f"Driver assigned successfully. Estimated delivery time: 31 mins.",
    request_id=1
)
```

#### **Database:**
```
notifications table:
┌────┬──────────┬────────────────────────────────────────┬───────────────┐
│ id │ req_id   │ message                                │ created_at    │
├────┼──────────┼────────────────────────────────────────┼───────────────┤
│ 1  │ 1        │ "Driver assigned. ETA: 31 mins."       │ 2026-05-28... │
└────┴──────────┴────────────────────────────────────────┴───────────────┘
```

---

## 👨‍🌾 FARMER SEES UPDATED REQUEST

### **What Farmer Sees on Dashboard:**

When farmer refreshes `/farmer` page:

#### **Request Table:**
```
Request ID  | Farmer     | Driver | Pickup Location | Destination   | Status    |
#1          | John Doe   | Amina  | Kumasi Village  | Central Market | Pending   |
```

#### **Notification Card:**
```
"Driver assigned successfully. Estimated delivery time: 31 mins."
2026-05-28 13:45:20
```

---

## 🚗 STEP 6: DRIVER SEES PENDING REQUEST

### **What Happens:**
Driver goes to http://127.0.0.1:5000/driver

### **Driver Dashboard Code** (app.py - Line ~215)
```python
@app.route("/driver")
def driver_dashboard():
    conn = get_db_connection()
    
    # Get ALL requests (filtered by status in template)
    requests_rows = conn.execute(
        """
        SELECT r.*, 
               f.name AS farmer_name,
               d.name AS driver_name
        FROM requests r
        JOIN farmers f ON r.farmer_id = f.id
        LEFT JOIN drivers d ON r.driver_id = d.id
        ORDER BY r.id DESC
        """
    ).fetchall()
    
    return render_template("driver_dashboard.html", requests=requests_rows)
```

### **Driver Sees in Table:**

```
Request | Farmer    | Pickup            | Destination    | Status   | ETA | Actions
#1      | John Doe  | Kumasi Village    | Central Market  | Pending  | 31m | [Accept Job]
```

---

## ✅ STEP 7: DRIVER ACCEPTS JOB

### **What Driver Does:**
On driver dashboard, clicks **"Accept Job"** button

### **HTML Button** (driver_dashboard.html)
```html
<form method="post" action="{{ url_for('accept_job', request_id=1) }}">
    <button class="btn btn-outline btn-small" type="submit">
        Accept Job
    </button>
</form>
```

### **Backend Route** (app.py - Line ~267)
```python
@app.post("/driver/accept/<int:request_id>")
def accept_job(request_id):
    conn = get_db_connection()
    
    # Get the request
    req = conn.execute(
        "SELECT * FROM requests WHERE id = ?", 
        (request_id,)
    ).fetchone()
    
    if not req:
        abort(404)  # Request doesn't exist
    
    # UPDATE REQUEST STATUS
    conn.execute(
        "UPDATE requests SET status = 'Accepted' WHERE id = ?", 
        (request_id,)
    )
    
    # CREATE NOTIFICATION
    dispatch_notification(
        conn, 
        "Driver assigned successfully.", 
        request_id
    )
    
    conn.commit()
    conn.close()
    
    flash("Job accepted successfully.", "success")
    return redirect(url_for("driver_dashboard"))
```

### **Database Changes:**

**Before Accept:**
```
requests table:
┌────┬───────────┬────────────────┬────────┐
│ id │ status    │ driver_id      │ eta    │
├────┼───────────┼────────────────┼────────┤
│ 1  │ "Pending" │ 2 (Amina)      │ 31     │
└────┴───────────┴────────────────┴────────┘
```

**After Accept:**
```
┌────┬───────────┬────────────────┬────────┐
│ id │ status    │ driver_id      │ eta    │
├────┼───────────┼────────────────┼────────┤
│ 1  │ "Accepted"│ 2 (Amina)      │ 31     │ ← Status changed!
└────┴───────────┴────────────────┴────────┘
```

### **What Both See Now:**

**Driver Dashboard:**
```
Request | Farmer    | Status   | Actions
#1      | John Doe  | Accepted | [Start Delivery]  ← Button changed
```

**Farmer Dashboard:**
```
Request | Farmer   | Driver | Status   
#1      | John Doe | Amina  | Accepted  ← Updated status

Notification:
"Driver assigned successfully."
```

---

## 🚗 STEP 8: DRIVER STARTS DELIVERY

### **What Driver Does:**
Clicks **"Start Delivery"** button

### **Backend Route** (app.py - Line ~308)
```python
@app.post("/driver/start/<int:request_id>")
def start_delivery(request_id):
    conn = get_db_connection()
    
    req = conn.execute(
        "SELECT * FROM requests WHERE id = ?", 
        (request_id,)
    ).fetchone()
    
    if not req:
        abort(404)
    
    # UPDATE STATUS
    conn.execute(
        "UPDATE requests SET status = 'In Transit' WHERE id = ?", 
        (request_id,)
    )
    
    # SEND NOTIFICATION
    dispatch_notification(
        conn, 
        "Your goods are on the way.", 
        request_id
    )
    
    conn.commit()
    conn.close()
    
    flash("Delivery started.", "success")
    return redirect(url_for("driver_dashboard"))
```

### **Database Changes:**

```
Before:
┌────┬─────────┐
│ id │ status  │
├────┼─────────┤
│ 1  │ Accepted│
└────┴─────────┘

After:
┌────┬──────────┐
│ id │ status   │
├────┼──────────┤
│ 1  │ In Transit│ ← Status updated
└────┴──────────┘
```

### **What Farmer Sees:**
```
Request | Status    | 
#1      | In Transit | ← Updated! Goods are moving

Notification:
"Your goods are on the way."
```

---

## 🎉 STEP 9: DRIVER MARKS DELIVERED

### **What Driver Does:**
Clicks **"Mark Delivered"** button

### **Backend Route** (app.py - Line ~327)
```python
@app.post("/driver/deliver/<int:request_id>")
def mark_delivered(request_id):
    conn = get_db_connection()
    
    req = conn.execute(
        "SELECT * FROM requests WHERE id = ?", 
        (request_id,)
    ).fetchone()
    
    if not req:
        abort(404)
    
    # UPDATE STATUS
    conn.execute(
        "UPDATE requests SET status = 'Delivered' WHERE id = ?", 
        (request_id,)
    )
    
    # MARK DRIVER AS AVAILABLE AGAIN (KEY!)
    if req["driver_id"]:
        conn.execute(
            "UPDATE drivers SET availability = 'available' WHERE id = ?",
            (req["driver_id"],)
        )
    
    # SEND NOTIFICATION
    dispatch_notification(
        conn, 
        "Delivery completed.", 
        request_id
    )
    
    conn.commit()
    conn.close()
    
    flash("Delivery marked as completed.", "success")
    return redirect(url_for("driver_dashboard"))
```

### **Database Changes:**

**Requests Table:**
```
Before:
┌────┬──────────┐
│ id │ status   │
├────┼──────────┤
│ 1  │ In Transit│
└────┴──────────┘

After:
┌────┬───────────┐
│ id │ status    │
├────┼───────────┤
│ 1  │ Delivered │ ← Completed!
└────┴───────────┘
```

**Drivers Table:**
```
Before:
┌────┬──────────────────┐
│ id │ availability     │
├────┼──────────────────┤
│ 2  │ "busy"           │ (Amina was busy)
└────┴──────────────────┘

After:
┌────┬──────────────────┐
│ id │ availability     │
├────┼──────────────────┤
│ 2  │ "available"      │ ← Available again! Can take new jobs
└────┴──────────────────┘
```

---

## 📊 COMPLETE STATE TRANSITIONS

### **Request Status Flow:**
```
┌─────────┐     Farmer         ┌─────────┐     Driver         ┌──────────┐
│ PENDING │  submits request   │ ACCEPTED│   starts delivery  │ IN TRANSIT│
└─────────┘──────────────────→ └─────────┘──────────────────→ └──────────┘
                               ^                                    │
                               │                                    │
                               └────────────────────────────────────┘
                                  Driver marks delivered
                                         │
                                         ↓
                                   ┌───────────┐
                                   │ DELIVERED │
                                   └───────────┘
                                   (Cycle Complete)
```

### **Driver Availability Flow:**
```
┌──────────┐                      ┌──────┐                    ┌──────────┐
│ Available│ → accepts job →      │ Busy │ → delivers good → │ Available│
└──────────┘                      └──────┘                    └──────────┘
  (Can take jobs)             (Busy with current job)    (Ready for next job)
```

---

## 🔔 NOTIFICATION FLOW

### **All Notifications Generated:**

| Trigger | Message | Who Sees |
|---------|---------|----------|
| Request submitted | "Driver assigned successfully. ETA: X mins." | Farmer |
| Driver accepts | "Driver assigned successfully." | Farmer + System Log |
| Driver starts delivery | "Your goods are on the way." | Farmer + System Log |
| Driver completes | "Delivery completed." | Farmer + System Log |
| Route optimization | "AI Route Optimization Active." | Farmer + System Log |

---

## 📈 ADMIN SEES EVERYTHING

### **Admin Dashboard** (http://127.0.0.1:5000/admin)

Shows all requests with statuses:
```
All Requests Table:
┌────┬───────────┬───────┬──────────────────┬─────────────────┬────────┬───────────┐
│ ID │ Farmer    │ Driver│ Pickup           │ Destination     │ Goods  │ Status    │
├────┼───────────┼───────┼──────────────────┼─────────────────┼────────┼───────────┤
│ 1  │ John Doe  │ Amina │ Kumasi Village   │ Central Market  │ Tomato │ Delivered │
│ 2  │ Jane Smith│ Kwame │ Tema Port        │ Accra Market    │ Fish   │ Accepted  │
│ 3  │ Bob Jones │ —     │ Cape Coast       │ Sekondi Market  │ Maize  │ Pending   │
└────┴───────────┴───────┴──────────────────┴─────────────────┴────────┴───────────┘

Driver Roster:
┌───────┬──────────────────┬──────────────┐
│ Name  │ Phone            │ Status       │
├───────┼──────────────────┼──────────────┤
│ Amina │ +254712490330    │ Available    │ (just delivered)
│ Kwame │ +233555210120    │ Busy         │ (doing request #2)
│ Tunde │ +234802301556    │ Available    │ (can take job)
│ Zola  │ +27712555010     │ Available    │ (can take job)
└───────┴──────────────────┴──────────────┘

Statistics:
Total Requests: 3
Pending: 1 (Bob's request waiting for driver)
Accepted: 1 (Jane's request - driver assigned)
In Transit: 0
Delivered: 1 (John's request completed)
Active Drivers: 3 out of 4
```

---

## 💾 COMPLETE DATABASE STATE AT END

### **After One Complete Cycle:**

```sql
-- Farmers
INSERT INTO farmers (id, name, phone) VALUES
(1, 'John Doe', '+233555123456'),
(2, 'Jane Smith', '+233555234567'),
(3, 'Bob Jones', '+233555345678');

-- Drivers
INSERT INTO drivers (id, name, phone, availability) VALUES
(1, 'Kwame Boateng', '+233555210120', 'available'),
(2, 'Amina Njeri', '+254712490330', 'available'),
(3, 'Tunde Okafor', '+234802301556', 'available'),
(4, 'Zola Mbeki', '+27712555010', 'available');

-- Requests (showing journey)
INSERT INTO requests (...) VALUES
(1, 1, 'Kumasi Village', 'Central Market', 'Tomatoes', '50 crates', 
 'Delivered', 2, 31, '2026-05-28T13:30:00'),
(2, 2, 'Tema Port', 'Accra Market', 'Fish', '100 kg', 
 'Accepted', 1, 45, '2026-05-28T13:35:00'),
(3, 3, 'Cape Coast', 'Sekondi Market', 'Maize', '75 bags', 
 'Pending', NULL, NULL, '2026-05-28T13:40:00');

-- Notifications
INSERT INTO notifications (...) VALUES
(1, 1, 'Driver assigned. ETA: 31 mins', '2026-05-28T13:30:05'),
(2, 1, 'Driver assignment accepted', '2026-05-28T13:31:00'),
(3, 1, 'Goods on the way', '2026-05-28T13:35:00'),
(4, 1, 'Delivery completed', '2026-05-28T13:55:00');
```

---

## 🎯 KEY POINTS

✅ **Farmer submits** → Request created in DB
✅ **AI assigns driver** → Nearest driver selected, ETA calculated
✅ **Driver marked busy** → Cannot take other jobs
✅ **Notification sent** → Both see updates
✅ **Driver accepts** → Status: Pending → Accepted
✅ **Driver starts** → Status: Accepted → In Transit
✅ **Driver completes** → Status: In Transit → Delivered
✅ **Driver becomes available** → Can take next job
✅ **Admin sees everything** → All requests, drivers, statuses
✅ **Analytics update** → Charts show delivery completion rates

---

## 🔄 CYCLE REPEATS

Once driver marks delivered:
- Driver status: "available" ✅
- Ready to accept new requests
- Process starts again with next farmer

**This is how the logistics ecosystem works!** 🚀
