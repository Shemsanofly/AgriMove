"""Bilingual (English / Swahili) translation helpers for AgriMove AI."""

from flask import request

SUPPORTED_LANGS = ("en", "sw")
DEFAULT_LANG = "en"

# Status keys stored in DB remain English; translate at display time.
STATUS_LABELS = {
    "en": {
        "Pending": "Pending",
        "Accepted": "Accepted",
        "In Transit": "In Transit",
        "Delivered": "Delivered",
        "available": "Available",
        "busy": "Busy",
        "Verified": "Verified",
        "Low": "Low",
        "Medium": "Medium",
        "High": "High",
        "Stable": "Stable",
        "Rising": "Rising",
        "Falling": "Falling",
    },
    "sw": {
        "Pending": "Inasubiri",
        "Accepted": "Imekubaliwa",
        "In Transit": "Inasafirishwa",
        "Delivered": "Imewasili",
        "available": "Inapatikana",
        "busy": "Anafanya kazi",
        "Verified": "Imethibitishwa",
        "Low": "Chini",
        "Medium": "Wastani",
        "High": "Juu",
        "Stable": "Imara",
        "Rising": "Inapanda",
        "Falling": "Inashuka",
    },
}

MESSAGES = {
    "en": {
        "transport_submitted": "Transport request submitted successfully.",
        "job_accepted": "Job accepted successfully.",
        "delivery_started": "Delivery started.",
        "delivery_completed": "Delivery marked as completed.",
        "rating_thanks": "Thank you for your rating!",
        "fill_all_fields": "Please fill in all fields",
        "price_added": "Price for {crop} in {region} added/updated successfully.",
        "invalid_price": "Invalid price value",
        "missing_price_details": "Missing details for price update",
        "price_updated": "Market price updated successfully.",
        "price_deleted": "Market price entry deleted successfully.",
        "price_limit_reached": "Only 2 featured prices are allowed. Edit or delete an existing record first.",
        "buyer_status_updated": "Buyer status updated to {status} successfully.",
        "transport_fill_all": "Please fill in all fields.",
        "transport_registered": "Your transport request was registered successfully!",
        "transport_pool_found": "Transport routes for {ward} ward found.",
        "transport_join_fill": "Please enter your name and phone number.",
        "transport_not_found": "Transport pool not found.",
        "transport_slots_insufficient": "Not enough slots. Only {slots} slots remaining.",
        "transport_join_success": "You successfully joined the transport pool!",
        "transport_join_name_phone": "Please enter name and phone.",
        "transport_bags_exceed": "Bags cannot exceed available slots!",
        "transport_submit_failed": "Failed to register request.",
        "transport_join_failed": "Failed to join transport pool.",
        "sms_sent_sandbox": "SMS sent to {phone}. Open the Africa's Talking simulator or SMS Outbox to read it.",
        "sms_send_failed": "SMS could not be sent: {error}",
        "sms_auth_failed": "SMS API key rejected. Update AT_API_KEY in .env and restart the app.",
        "admin_heading": "Admin",
        "admin_subheading": "Prices and buyers",
        "admin_drivers": "Drivers",
        "admin_fleet": "Fleet",
        "admin_prices_tab": "Prices",
        "admin_buyers_tab": "Buyers",
        "admin_add_price": "Add price",
        "admin_crop": "Crop",
        "admin_region": "Region",
        "admin_price": "Price",
        "admin_demand": "Demand",
        "admin_trend": "Trend",
        "admin_add": "Add",
        "admin_save": "Save",
        "admin_delete": "Delete",
        "admin_empty": "Empty",
        "admin_buyer": "Buyer",
        "admin_phone": "Phone",
        "admin_rating": "Rating",
        "admin_status": "Status",
        "admin_verify": "Verify",
        "admin_revoke": "Revoke",
        "admin_none": "None",
        "admin_driver": "Driver",
    },
    "sw": {
        "transport_submitted": "Ombi la usafirishaji limewasilishwa kwa mafanikio.",
        "job_accepted": "Kazi imekubaliwa kwa mafanikio.",
        "delivery_started": "Usafirishaji umeanza.",
        "delivery_completed": "Usafirishaji umewekwa alama kuwa umekamilika.",
        "rating_thanks": "Asante kwa ukadiriaji wako!",
        "fill_all_fields": "Tafadhali jaza sehemu zote",
        "price_added": "Bei ya {crop} katika {region} imeongezwa/kusasishwa kwa mafanikio.",
        "invalid_price": "Thamani ya bei si sahihi",
        "missing_price_details": "Maelezo ya kusasisha bei hayapo",
        "price_updated": "Bei ya soko imesasishwa kwa mafanikio.",
        "price_deleted": "Ingizo la bei ya soko limefutwa kwa mafanikio.",
        "price_limit_reached": "Bei 2 tu zinaweza kuonyeshwa. Hariri au futa rekodi iliyopo kwanza.",
        "buyer_status_updated": "Hali ya mnunuzi imesasishwa kuwa {status} kwa mafanikio.",
        "transport_fill_all": "Tafadhali jaza sehemu zote.",
        "transport_registered": "Ombi lako la kusafirisha mizigo limesajiliwa kikamilifu!",
        "transport_pool_found": "Njia za usafirishaji za kata ya {ward} zimepatikana.",
        "transport_join_fill": "Tafadhali weka jina na namba ya simu.",
        "transport_not_found": "Usafiri haukupatikana.",
        "transport_slots_insufficient": "Nafasi hazitoshi. Nafasi zilizobaki ni {slots} tu.",
        "transport_join_success": "Umefanikiwa kujiunga na gari la usafirishaji!",
        "transport_join_name_phone": "Tafadhali weka jina na namba ya simu.",
        "transport_bags_exceed": "Mifuko haiwezi kuzidi nafasi zilizobaki!",
        "transport_submit_failed": "Imeshindikana kusajili ombi.",
        "transport_join_failed": "Imeshindikana kujiunga na gari.",
        "sms_sent_sandbox": "SMS imetumwa kwa {phone}. Fungua simulator au SMS Outbox ya Africa's Talking kuuisoma.",
        "sms_send_failed": "SMS haikutumwa: {error}",
        "sms_auth_failed": "Ufunguo wa SMS umekataliwa. Sasisha AT_API_KEY kwenye .env kisha anzisha tena programu.",
        "admin_heading": "Msimamizi",
        "admin_subheading": "Bei na wanunuzi",
        "admin_drivers": "Madereva",
        "admin_fleet": "Magari",
        "admin_prices_tab": "Bei",
        "admin_buyers_tab": "Wanunuzi",
        "admin_add_price": "Ongeza bei",
        "admin_crop": "Zao",
        "admin_region": "Mkoa",
        "admin_price": "Bei",
        "admin_demand": "Mahitaji",
        "admin_trend": "Mwenendo",
        "admin_add": "Ongeza",
        "admin_save": "Hifadhi",
        "admin_delete": "Futa",
        "admin_empty": "Tupu",
        "admin_buyer": "Mnunuzi",
        "admin_phone": "Simu",
        "admin_rating": "Ukadiriaji",
        "admin_status": "Hali",
        "admin_verify": "Thibitisha",
        "admin_revoke": "Batilisha",
        "admin_none": "Hakuna",
        "admin_driver": "Dereva",
    },
}


def get_lang():
    cookie_lang = request.cookies.get("agrimove_lang", DEFAULT_LANG)
    return cookie_lang if cookie_lang in SUPPORTED_LANGS else DEFAULT_LANG


def t(key, lang=None, **kwargs):
    lang = lang or get_lang()
    catalog = MESSAGES.get(lang, MESSAGES[DEFAULT_LANG])
    text = catalog.get(key, MESSAGES[DEFAULT_LANG].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text


def status_label(status, lang=None):
    lang = lang or get_lang()
    return STATUS_LABELS.get(lang, STATUS_LABELS[DEFAULT_LANG]).get(
        status, status
    )
