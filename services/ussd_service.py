"""Africa's Talking USSD menu handler for AgriMove."""

from datetime import datetime


def handle_ussd(
    text,
    phone_number,
    session_id=None,
    service_code=None,
    *,
    crops,
    regions,
    pickup_locations,
    get_db_connection,
    assign_driver,
    dispatch_notification,
    estimate_profit,
):
    """
    Build a USSD response string for Africa's Talking.

    AT sends cumulative input in `text` (e.g. "", "1", "1*2", "1*2*3").
    Responses must start with CON (continue session) or END (terminate).
    """
    parts = [p.strip() for p in text.split("*")] if text else []

    if len(parts) == 0 or not text:
        return (
            "CON Karibu AgriMove Tanzania.\n"
            "Chagua huduma:\n"
            "1. Bei za Soko\n"
            "2. Omba Usafiri\n"
            "3. Tafuta Wanunuzi\n"
            "4. Fuatilia Ombi\n"
            "5. Kadiria Faida"
        )

    if parts[0] == "1":
        if len(parts) == 1:
            crop_list = "\n".join(f"{i + 1}. {crop}" for i, crop in enumerate(crops))
            return f"CON Chagua Mazao:\n{crop_list}"
        if len(parts) == 2:
            try:
                crop_idx = int(parts[1]) - 1
                if 0 <= crop_idx < len(crops):
                    region_list = "\n".join(f"{i + 1}. {region}" for i, region in enumerate(regions))
                    return f"CON Chagua Mkoa wa {crops[crop_idx]}:\n{region_list}"
                return "END Chaguo la mazao si sahihi."
            except ValueError:
                return "END Ingizo si sahihi."
        if len(parts) == 3:
            try:
                crop_idx = int(parts[1]) - 1
                region_idx = int(parts[2]) - 1
                if 0 <= crop_idx < len(crops) and 0 <= region_idx < len(regions):
                    crop_name = crops[crop_idx]
                    region_name = regions[region_idx]
                    conn = get_db_connection()
                    price_row = conn.execute(
                        "SELECT price, demand_level, trend FROM market_prices WHERE crop_name = ? AND region = ?",
                        (crop_name, region_name),
                    ).fetchone()
                    conn.close()
                    if price_row:
                        return (
                            f"END {crop_name} ({region_name}):\n"
                            f"Bei: {price_row['price']:,} TZS\n"
                            f"Mahitaji: {price_row['demand_level']}\n"
                            f"Mwenendo: {price_row['trend']}"
                        )
                    return f"END Hakuna bei ya {crop_name} katika {region_name}."
                return "END Chaguo si sahihi."
            except ValueError:
                return "END Ingizo si sahihi."

    elif parts[0] == "2":
        if len(parts) == 1:
            crop_list = "\n".join(f"{i + 1}. {crop}" for i, crop in enumerate(crops))
            return f"CON Chagua Mazao ya Kusafirisha:\n{crop_list}"
        if len(parts) == 2:
            return "CON Ingiza idadi (mf. mifuko 50):"
        if len(parts) == 3:
            pickup_list = "\n".join(f"{i + 1}. {place}" for i, place in enumerate(pickup_locations))
            return f"CON Chagua Mahali pa Kuchukua:\n{pickup_list}"
        if len(parts) == 4:
            region_list = "\n".join(f"{i + 1}. {region}" for i, region in enumerate(regions))
            return f"CON Chagua Soko la Kwenda:\n{region_list}"
        if len(parts) == 5:
            try:
                crop_name = crops[int(parts[1]) - 1]
                quantity = parts[2]
                pickup = pickup_locations[int(parts[3]) - 1]
                destination = regions[int(parts[4]) - 1]
            except (ValueError, IndexError):
                return "END Chaguo la usafiri si sahihi."
            return (
                f"CON Thibitisha Usafiri?\n"
                f"{quantity} ya {crop_name}\n"
                f"Kutoka: {pickup}\n"
                f"Kwenda: {destination}\n"
                f"1. Ndiyo\n"
                f"2. Ghairi"
            )
        if len(parts) == 6:
            if parts[5] == "1":
                try:
                    crop_name = crops[int(parts[1]) - 1]
                    quantity = parts[2]
                    pickup = pickup_locations[int(parts[3]) - 1]
                    destination = regions[int(parts[4]) - 1]
                except (ValueError, IndexError):
                    return "END Chaguo la usafiri si sahihi."

                conn = get_db_connection()
                farmer = conn.execute(
                    "SELECT id FROM farmers WHERE phone = ?", (phone_number,)
                ).fetchone()
                if farmer:
                    farmer_id = farmer["id"]
                else:
                    farmer_id = conn.execute(
                        "INSERT INTO farmers (name, phone, member_since) VALUES (?, ?, ?)",
                        (
                            f"USSD Farmer ({phone_number[-4:]})",
                            phone_number,
                            datetime.now().isoformat(),
                        ),
                    ).lastrowid

                driver, eta = assign_driver(conn)
                driver_id = driver["id"] if driver else None
                status = "Pending"

                if driver_id:
                    conn.execute(
                        "UPDATE drivers SET availability = 'busy' WHERE id = ?",
                        (driver_id,),
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
                        crop_name,
                        quantity,
                        status,
                        driver_id,
                        eta,
                        datetime.now().isoformat(),
                    ),
                ).lastrowid

                msg = f"Transport Request #{request_id} created successfully."
                if driver_id:
                    msg += f" Driver {driver['name']} assigned (ETA: {eta} mins)."
                else:
                    msg += " Searching for available drivers."

                dispatch_notification(conn, msg, request_id)
                conn.commit()
                conn.close()

                return (
                    f"END Ombi la usafiri #{request_id} limeundwa!\n"
                    f"Tunatafuta dereva."
                )
            return "END Ombi limeghairiwa."

    elif parts[0] == "3":
        if len(parts) == 1:
            crop_list = "\n".join(f"{i + 1}. {crop}" for i, crop in enumerate(crops[:4]))
            return f"CON Chagua Mazao ya Kuuza:\n{crop_list}"
        if len(parts) == 2:
            try:
                crop_idx = int(parts[1]) - 1
                if 0 <= crop_idx < 4:
                    crop_name = crops[crop_idx]
                    conn = get_db_connection()
                    offers = conn.execute(
                        "SELECT id, buyer_name, offered_price FROM buyer_offers WHERE crop_name = ? AND status = 'Active' LIMIT 3",
                        (crop_name,),
                    ).fetchall()
                    conn.close()
                    if offers:
                        offer_list = "\n".join(
                            f"{i + 1}. {o['buyer_name']} ({o['offered_price']:,} TZS)"
                            for i, o in enumerate(offers)
                        )
                        return f"CON Ofa za {crop_name}:\n{offer_list}"
                    return f"END Hakuna ofa za {crop_name}."
                return "END Chaguo la mazao si sahihi."
            except ValueError:
                return "END Ingizo si sahihi."
        if len(parts) == 3:
            try:
                crop_idx = int(parts[1]) - 1
                offer_choice = int(parts[2]) - 1
                crop_name = crops[crop_idx]

                conn = get_db_connection()
                offers = conn.execute(
                    "SELECT * FROM buyer_offers WHERE crop_name = ? AND status = 'Active' LIMIT 3",
                    (crop_name,),
                ).fetchall()
                conn.close()

                if 0 <= offer_choice < len(offers):
                    selected = offers[offer_choice]
                    return (
                        f"END Mnunuzi: {selected['buyer_name']}\n"
                        f"Bei: {selected['offered_price']:,} TZS\n"
                        f"Kiasi: {selected['quantity']}\n"
                        f"Mahali: {selected['location']}"
                    )
                return "END Chaguo la ofa si sahihi."
            except ValueError:
                return "END Ingizo si sahihi."

    elif parts[0] == "4":
        if len(parts) == 1:
            return "CON Ingiza namba ya ombi:"
        if len(parts) == 2:
            try:
                req_id = int(parts[1])
                conn = get_db_connection()
                req_row = conn.execute(
                    """
                    SELECT r.*, d.name as driver_name, d.phone as driver_phone
                    FROM requests r
                    LEFT JOIN drivers d ON r.driver_id = d.id
                    WHERE r.id = ?
                    """,
                    (req_id,),
                ).fetchone()
                conn.close()
                if req_row:
                    driver_info = (
                        f"{req_row['driver_name']} ({req_row['driver_phone']})"
                        if req_row["driver_name"]
                        else "Inatafutwa..."
                    )
                    return (
                        f"END Ombi #{req_id}:\n"
                        f"Hali: {req_row['status']}\n"
                        f"Dereva: {driver_info}\n"
                        f"ETA: {req_row['eta_minutes'] or '—'} dak"
                    )
                return f"END Ombi #{req_id} halipatikani."
            except ValueError:
                return "END Namba ya ombi si sahihi."

    elif parts[0] == "5":
        if len(parts) == 1:
            return "CON Ingiza jina la mazao (mf. Maize):"
        if len(parts) == 2:
            return "CON Ingiza idadi (mifuko):"
        if len(parts) == 3:
            return "CON Ingiza gharama ya usafiri (TZS):"
        if len(parts) == 4:
            region_list = "\n".join(f"{i + 1}. {region}" for i, region in enumerate(regions))
            return f"CON Chagua Mkoa wa Kwenda:\n{region_list}"
        if len(parts) == 5:
            try:
                crop = parts[1]
                quantity = float(parts[2])
                transport = float(parts[3])
                reg_idx = int(parts[4]) - 1
                if 0 <= reg_idx < len(regions):
                    dest = regions[reg_idx]
                    estimate = estimate_profit(crop, quantity, transport, "Local", dest)
                    if estimate:
                        return (
                            f"END Makadirio ya Faida ({crop}):\n"
                            f"Mapato: {estimate['estimated_revenue']:,} TZS\n"
                            f"Gharama: {estimate['total_costs']:,} TZS\n"
                            f"Faida: {estimate['estimated_profit']:,} TZS\n"
                            f"Kiasi: {estimate['profit_margin']}%"
                        )
                    return f"END Hakuna bei ya {crop} katika {dest}."
                return "END Mkoa si sahihi."
            except ValueError:
                return "END Ingizo si sahihi."

    return "END Chaguo si sahihi."
