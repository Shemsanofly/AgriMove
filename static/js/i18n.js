/**
 * AgriMove AI — bilingual UI (English / Swahili)
 * Usage: data-i18n="key" | data-i18n-placeholder="key" | data-i18n-title="key"
 * Status badges: class="i18n-status" data-status="Pending"
 */
(function () {
  "use strict";

  const STORAGE_KEY = "agrimove_lang";
  const DEFAULT_LANG = "en";

  const STATUS = {
    en: { Pending: "Pending", Accepted: "Accepted", "In Transit": "In Transit", Delivered: "Delivered", available: "available", busy: "busy" },
    sw: { Pending: "Inasubiri", Accepted: "Imekubaliwa", "In Transit": "Inasafirishwa", Delivered: "Imewasili", available: "inapatikana", busy: "anafanya kazi" },
  };

  const T = {
    en: {
      /* Nav & layout */
      nav_market_prices: "Market Prices",
      nav_shamba_connect: "Shamba Connect",
      nav_payments: "Secure Payments",
      nav_storage: "My Storage",
      nav_insights: "AI Market Insights",
      nav_farmer: "Farmer Dashboard",
      nav_driver: "Driver Dashboard",
      nav_admin: "Admin Dashboard",
      nav_analytics: "Analytics",
      nav_home: "Back to Home",
      sidebar_tag: "Smart rural logistics suite",
      sidebar_footer: "AI Route Optimization Active",
      sidebar_footer_sub: "Adaptive planning for rural routes",
      btn_mode: "Mode",
      btn_menu: "Menu",
      btn_lang_sw: "🇹🇿 SW",
      btn_lang_en: "🇬🇧 EN",
      btn_dark: "🌙 Dark Mode",
      btn_light: "☀️ Light Mode",

      /* Page headings */
      heading_farmer: "Farmer Dashboard",
      sub_farmer: "Request transport and track the movement of your harvest.",
      heading_driver: "Driver Dashboard",
      sub_driver: "Accept jobs, manage delivery progress, and update statuses.",
      heading_admin: "Admin",
      sub_admin: "Manage prices and buyers.",
      heading_analytics: "Analytics & Reports",
      sub_analytics: "Delivery statistics, trends, and performance metrics.",
      heading_insights: "AI Market Intelligence",
      sub_insights: "Real-time predictive models, demand tracking, and smart routes.",
      heading_market_prices: "Market Prices",
      sub_market_prices: "Crop price board for major Tanzanian markets.",
      heading_shamba: "Shamba Connect",
      sub_shamba: "Connect with fellow farmers to pool transport and reduce costs.",
      heading_payments: "Secure Payments",
      sub_payments: "Pay and receive safely using M-Pesa Escrow without fear of losing money.",
      heading_storage: "My Storage",
      sub_storage: "Find nearby warehouses for your produce and Warehouse Receipt (WRS) systems.",

      /* Landing page */
      hero_eyebrow: "Smart Rural Logistics",
      hero_title: "Move harvests faster with AI-powered transport coordination",
      hero_desc: "AgriMove AI connects farmers with trusted drivers, optimizes village routes, and delivers real-time visibility from pickup to market.",
      hero_cta_transport: "Request Transport",
      hero_cta_features: "Explore Features",
      stat_faster: "faster delivery cycles",
      stat_drivers: "rural drivers onboarded",
      stat_success: "market arrival success",
      map_live: "Live Route",
      map_farm: "Farm pickup",
      map_hub: "Collection hub",
      map_market: "Market",
      fleet_avail: "Fleet Availability",
      fleet_ready: "Drivers ready in 20 minutes",
      freshness: "Freshness Window",
      freshness_sub: "Optimal arrival forecast",
      farmers_joined: "Farmers Joined",
      maize_price: "Today's Maize Price",
      loads_pooled: "Loads Pooled",
      features_title: "Smart features built for rural movement",
      features_desc: "Every shipment is matched, tracked, and optimized with AI so farmers focus on harvesting while drivers focus on safe delivery.",
      feat_matching: "Smart Transport Matching",
      feat_matching_desc: "Instantly pair farms with nearby vetted drivers and the right vehicle size.",
      feat_sms: "SMS Notifications",
      feat_sms_desc: "Keep farmers informed even with low data connectivity using SMS updates.",
      feat_tracking: "Real-Time Tracking",
      feat_tracking_desc: "Track shipments from village pickup to market arrival in real time.",
      feat_route: "AI Route Optimization",
      feat_route_desc: "Reduce delays with AI-assisted route planning that adapts to road conditions.",
      feat_connectivity: "Rural Connectivity",
      feat_connectivity_desc: "Offline-first workflows designed for rural network coverage and power limits.",
      about_eyebrow: "About AgriMove AI",
      about_title: "Empowering farmers with reliable, efficient logistics",
      about_desc: "AgriMove AI helps rural farmers move produce faster by connecting them to nearby drivers, coordinating routes, and ensuring transparent communication. The platform reduces spoilage, improves market prices, and builds trust across the supply chain.",
      tag_farmer: "Farmer-first design",
      tag_drivers: "Trusted driver network",
      tag_insights: "Market-ready insights",
      about_pickups: "Efficient pickups",
      about_pickups_desc: "Schedule transport in minutes, not hours, with automated matching.",
      about_pricing: "Transparent pricing",
      about_pricing_desc: "Clear rates and shared trip visibility help everyone plan better.",
      about_community: "Community growth",
      about_community_desc: "More deliveries mean stronger rural economies and better livelihoods.",
      contact_eyebrow: "Request transport",
      contact_title: "Move your harvest with confidence",
      contact_desc: "Share pickup details and our dispatch team will connect you with a driver within minutes.",
      contact_hotline: "Dispatch hotline",
      contact_email: "Email",
      contact_coverage: "Coverage",
      label_name: "Full name",
      label_phone: "Phone number",
      label_pickup: "Pickup location",
      label_produce: "Produce type",
      label_notes: "Delivery notes",
      ph_name: "Ama Mensah",
      ph_phone: "+255...",
      ph_location: "Village or farm",
      ph_produce: "Tomatoes, maize, cocoa",
      ph_notes: "Pickup date, quantity, market",
      btn_send_request: "Send request",
      footer_desc: "Smart rural logistics built for African agriculture.",
      footer_quick: "Quick links",
      footer_features: "Features",
      footer_about: "About",
      footer_contact: "Contact",
      footer_platform: "Platform",
      footer_help: "Help Center",
      footer_marketplace: "Buyer Marketplace",
      footer_support: "Support",
      footer_support_center: "Support Center",
      footer_notifications: "Notifications",
      footer_contact_us: "Contact Us",
      footer_rights: "AgriMove AI. All rights reserved.",
      nav_dashboard: "Dashboard",
      form_thanks: "Thanks! Our dispatch team will contact you shortly.",
      sms_toast: "💬 SIMULATED SMS",

      /* Dashboard common */
      total_requests: "Total Requests",
      all_submissions: "All transport submissions",
      all_submissions_short: "All submissions",
      pending: "Pending",
      accepted: "Accepted",
      in_transit: "In Transit",
      delivered: "Delivered",
      awaiting_driver: "Awaiting driver action",
      driver_assigned: "Driver assigned",
      en_route: "Currently en route",
      completed: "Completed deliveries",
      completed_short: "Completed",
      ai_route_active: "AI Route Optimization Active",
      eta_mins: "Estimated delivery time: {n} mins",
      ai_route_desc: "Real-time route planning is enabled for every request.",
      notifications: "Notifications",
      no_notifications: "No notifications yet.",
      request_status: "Request Status",
      status_overview: "Status overview for all submissions",
      th_request_id: "Request ID",
      th_pickup: "Pickup",
      th_destination: "Destination",
      th_goods: "Goods",
      th_quantity: "Quantity",
      th_driver: "Driver",
      th_status: "Status",
      searching: "Searching...",
      no_requests: "No requests submitted yet.",
      submit_transport: "Submit Transport Request",
      farmer_name: "Farmer Name",
      pickup_location: "Pickup Location",
      select_pickup: "Select pickup point",
      select_market: "Select market destination",
      goods_type: "Goods Type",
      select_crop: "Select crop",
      quantity: "Quantity",
      ph_quantity: "20 crates",
      btn_request_transport: "Request Transport",
      market_intel: "Market Intelligence & Buyer Offers",
      view_prices: "View Market Prices",
      calc_profit: "Calculate Profit",
      view_offers: "View Buyer Offers",
      marketplace_hub: "Marketplace Hub",

      /* Driver dashboard */
      available_drivers: "Available Drivers",
      ready_assignments: "Ready for assignments",
      busy_drivers: "Busy Drivers",
      on_deliveries: "Currently on deliveries",
      pending_requests: "Pending Requests",
      awaiting_acceptance: "Awaiting acceptance",
      active_deliveries: "Active deliveries",
      driver_ai_desc: "Drivers receive optimized routes and dynamic ETA updates.",
      available_requests: "Available Requests",
      accept_jobs_desc: "Accept, start, and complete delivery jobs",
      th_request: "Request",
      th_farmer: "Farmer",
      th_eta: "ETA",
      th_actions: "Actions",
      tbd: "TBD",
      btn_accept_job: "Accept Job",
      btn_start_delivery: "Start Delivery",
      btn_mark_delivered: "Mark Delivered",
      no_requests_available: "No requests available yet.",
      driver_availability: "Driver Availability",
      driver_roster: "Current driver roster",
      th_phone: "Phone",
      th_availability: "Availability",

      /* Admin dashboard */
      awaiting_assignment: "Awaiting assignment",
      active_drivers: "Drivers",
      fleet_health: "Fleet",
      tab_prices_short: "Prices",
      tab_buyers_short: "Buyers",
      tab_prices: "Prices",
      tab_buyers: "Buyers",
      admin_add_price_title: "Add Price",
      admin_crop_name: "Crop",
      admin_region: "Region",
      admin_price_tzs: "Price",
      admin_demand: "Demand",
      admin_trend: "Trend",
      admin_publish_price: "Add",
      admin_save_price: "Save",
      admin_delete_price: "Delete",
      admin_empty_price_slot: "Empty",
      admin_buyer_name: "Buyer",
      admin_rating: "Rating",
      admin_revoke: "Revoke",
      admin_verify_buyer: "Verify",
      admin_no_buyers: "None",
      admin_driver_roster: "Drivers",
      quick_search: "Quick Search",
      search_ph: "Search by request ID, farmer, or driver...",
      display_settings: "Display Settings",
      display_settings_desc: "Toggle dark/light theme for better visibility.",
      all_requests: "All Requests",
      realtime_mgmt: "Real-time request management",
      th_gps: "GPS Sim",
      unassigned: "Unassigned",
      no_requests_admin: "No requests yet.",
      btn_move_gps: "📍 Move GPS",
      add_crop_price: "Add New Crop Price",
      crop_name: "Crop Name",
      region: "Region",
      price_tzs: "Price (TZS/bag)",
      demand_level: "Demand Level",
      price_trend: "Price Trend",
      low: "Low",
      medium: "Medium",
      high: "High",
      stable: "Stable",
      rising: "Rising",
      falling: "Falling",
      btn_publish_price: "Publish Price",
      price_guidelines: "Price Guidelines",
      price_guidelines_desc: "Market intelligence algorithms rely on these values to suggest destination markets and optimize transport loads.",
      price_guidelines_sub: "Ensure prices are updated weekly to prevent farm spoilage and ensure buyer credibility.",

      /* Analytics */
      awaiting_driver_short: "Awaiting driver",
      en_route_short: "En route",
      delivery_status_dist: "Delivery Status Distribution",
      request_trend: "Request Trend (7 Days)",
      crop_demand: "Crop Demand Index",
      driver_deliveries: "Driver Deliveries Roster",
      market_price_activity: "Market Price Activity",
      completion_rate: "Completion Rate",
      pct_delivered: "{n}% of requests delivered",
      no_data: "No data yet",
      avg_eta: "Average ETA",
      mins_to_market: "minutes to market",
      chart_requests: "Requests",
      chart_demand: "Demand Index Score",
      chart_jobs: "Total Completed Jobs",
      chart_avg_price: "Average TZS per Bag",

      /* Shamba Connect */
      shamba_form_title: "Request Transport / Reserve Cargo",
      shamba_form_desc: "Enter your cargo details to find nearby fellow farmers and share transport costs.",
      shamba_full_name: "Your Full Name",
      shamba_phone: "Phone Number (M-Pesa)",
      shamba_district: "District",
      shamba_ward: "Ward",
      shamba_village: "Village",
      shamba_crop: "Crop to Transport",
      shamba_bags: "Number of Bags",
      shamba_date: "Transport Date",
      shamba_submit: "Submit & Find Match",
      shamba_ph_name: "e.g. Juma Hamisi",
      shamba_ph_district: "e.g. Rural Mbeya",
      shamba_ph_ward: "e.g. Mbeya Town",
      shamba_ph_village: "e.g. Uyole Village",
      crop_maize: "🌽 Maize",
      crop_rice: "🌾 Rice",
      crop_cassava: "🍠 Cassava",
      crop_tomato: "🍅 Tomatoes",
      crop_onion: "🧅 Onions",
      crop_coffee: "☕ Coffee",
      crop_cashew: "🥜 Cashews",
      shamba_matches_title: "Nearby Matching Farmers",
      shamba_matches_desc: "These farmers are shipping the same crop from your ward/district around the same time:",
      shamba_no_matches: "No other nearby farmers matched yet. You will be notified when matches are found.",
      shamba_pools_title: "Available Group Trucks (Pools)",
      shamba_pools_desc: "Click \"Join\" to reserve a slot and share transport costs.",
      shamba_route: "Route:",
      shamba_departure: "Departure:",
      shamba_slots: "Slots left:",
      shamba_driver: "Driver:",
      shamba_per_bag: "per bag",
      shamba_join: "Join",
      shamba_no_pools: "No open group trucks right now. Submit a request on the left to get one scheduled.",
      shamba_modal_title: "Join Group Truck",
      shamba_modal_cost: "Cost per bag is",
      shamba_modal_name: "Your name",
      shamba_modal_phone: "Phone number",
      shamba_modal_bags: "Number of bags",
      shamba_modal_slots: "Slots remaining:",
      shamba_modal_total: "Your total cost:",
      shamba_cancel: "Cancel",
      shamba_confirm: "Confirm",
      shamba_sms_inbox: "📱 SIMULATED SMS INBOX (2G SMS Receiver)",
      shamba_sms_close: "[Close]",
      shamba_sms_from: "FROM: AgriMove INFO\nMESSAGE:",
      shamba_match_partner: "Partner: {name} | Load: {bags} bags",
      shamba_match_village: "Village:",
      shamba_match_pickup: "Pickup date:",
      shamba_match_days: "Within 3 days",
      shamba_error: "Error:",
      transport_submit_failed: "Failed to register request.",
      transport_bags_exceed: "Bags cannot exceed available slots!",
      transport_join_failed: "Failed to join transport pool.",
      sms_inbox_title: "📱 SMS Simulation Inbox",
      sms_inbox_empty: "No SMS yet. Submit a transport request above to trigger a sandbox SMS notification.",
      sms_help_title: "SMS via Africa's Talking Sandbox",
      sms_help_body: "After you submit a transport request, the SMS is sent through Africa's Talking (username: sandbox). Open the AT simulator to read it — not this dashboard.",
      sms_help_step1: "1. Register your phone (+255...) in the AT sandbox dashboard.",
      sms_help_step2: "2. Submit the form below with the same phone number.",
      sms_help_step3: " to view the SMS.",
    },
    sw: {
      nav_market_prices: "Bei za Soko",
      nav_shamba_connect: "Shamba Connect",
      nav_payments: "Malango Salama",
      nav_storage: "Hifadhi Yangu",
      nav_insights: "Maarifa ya Soko ya AI",
      nav_farmer: "Dashibodi ya Mkulima",
      nav_driver: "Dashibodi ya Dereva",
      nav_admin: "Dashibodi ya Msimamizi",
      nav_analytics: "Takwimu",
      nav_home: "Rudi Nyumbani",
      sidebar_tag: "Mfumo wa usafirishaji wa vijijini",
      sidebar_footer: "Uboreshaji wa Njia wa AI Unaofanya Kazi",
      sidebar_footer_sub: "Mipango inayobadilika kwa njia za vijijini",
      btn_mode: "Muonekano",
      btn_menu: "Menyu",
      btn_lang_sw: "🇹🇿 SW",
      btn_lang_en: "🇬🇧 EN",
      btn_dark: "🌙 Hali ya Mchana",
      btn_light: "☀️ Hali ya Usiku",

      heading_farmer: "Dashibodi ya Mkulima",
      sub_farmer: "Omba usafirishaji na fuatilia harakati za mavuno yako.",
      heading_driver: "Dashibodi ya Dereva",
      sub_driver: "Kubali kazi, simamia maendeleo ya usafirishaji, na sasisha hali.",
      heading_admin: "Msimamizi",
      sub_admin: "Simamia bei na wanunuzi.",
      heading_analytics: "Takwimu na Ripoti",
      sub_analytics: "Takwimu za usafirishaji, mwenendo, na vipimo vya utendaji.",
      heading_insights: "Akili ya Soko ya AI",
      sub_insights: "Modeli za utabiri wa wakati halisi, ufuatiliaji wa mahitaji, na njia mahiri.",
      heading_market_prices: "Bei za Soko",
      sub_market_prices: "Bodi ya bei za mazao katika masoko makuu ya Tanzania.",
      heading_shamba: "Shamba Connect",
      sub_shamba: "Ungana na wakulima wenzako kusafirisha mazao kwa pamoja na kupunguza gharama.",
      heading_payments: "Malango Salama",
      sub_payments: "Lipa na upokee malipo salama kwa kutumia M-Pesa Escrow bila hofu ya kupoteza fedha.",
      heading_storage: "Hifadhi Yangu",
      sub_storage: "Tafuta maghala ya karibu ya kuhifadhia mazao yako na mifumo ya Warehouse Receipt (WRS).",

      hero_eyebrow: "Usafirishaji Mahiri wa Vijijini",
      hero_title: "Songesha mavuno haraka kwa usafirishaji unaotumia AI",
      hero_desc: "AgriMove AI inaunganisha wakulima na madereva wa kuaminika, kuboresha njia za vijijini, na kutoa uonekano wa wakati halisi kutoka shambani hadi sokoni.",
      hero_cta_transport: "Omba Usafirishaji",
      hero_cta_features: "Gundua Vipengele",
      stat_faster: "mzunguko wa usafirishaji wa haraka",
      stat_drivers: "madereva wa vijijini waliounganishwa",
      stat_success: "mafanikio ya kuwasili sokoni",
      map_live: "Njia Hai",
      map_farm: "Kuchukua shambani",
      map_hub: "Kituo cha ukusanyaji",
      map_market: "Soko",
      fleet_avail: "Upatikanaji wa Magari",
      fleet_ready: "Madereva tayari ndani ya dakika 20",
      freshness: "Dirisha la Uboreshaji",
      freshness_sub: "Utabiri bora wa kuwasili",
      farmers_joined: "Wakulima Waliojiunga",
      maize_price: "Bei ya Leo ya Mahindi",
      loads_pooled: "Mzigo Uliounganishwa",
      features_title: "Vipengele mahiri vilivyojengwa kwa usafirishaji wa vijijini",
      features_desc: "Kila mzigo unalinganishwa, unafuatiliwa, na kuboreshwa na AI ili wakulima wazingatie mavuno na madereva wazingatie usafirishaji salama.",
      feat_matching: "Ulinganisho Mahiri wa Usafirishaji",
      feat_matching_desc: "Unganisha shamba na madereva walio karibu na ukubwa sahihi wa gari papo hapo.",
      feat_sms: "Arifa za SMS",
      feat_sms_desc: "Wajulishe wakulima hata kwa muunganisho mdogo wa data kupitia SMS.",
      feat_tracking: "Ufuatiliaji wa Wakati Halisi",
      feat_tracking_desc: "Fuatilia mizigo kutoka kuchukuliwa vijijini hadi kuwasili sokoni kwa wakati halisi.",
      feat_route: "Uboreshaji wa Njia wa AI",
      feat_route_desc: "Punguza ucheleweshaji kwa mipango ya njia inayosaidiwa na AI.",
      feat_connectivity: "Muunganisho wa Vijijini",
      feat_connectivity_desc: "Mifumo ya kwanza nje ya mtandao iliyoundwa kwa mitandao na umeme mdogo wa vijijini.",
      about_eyebrow: "Kuhusu AgriMove AI",
      about_title: "Kuwezesha wakulima kwa usafirishaji wa kuaminika na wenye ufanisi",
      about_desc: "AgriMove AI inawasaidia wakulima wa vijijini kusafirisha mazao haraka kwa kuwaunganisha na madereva wa karibu, kuratibu njia, na kuhakikisha mawasiliano wazi. Jukwaa hili hupunguza uharibifu, kuboresha bei za soko, na kujenga uaminifu katika mlolongo wa usambazaji.",
      tag_farmer: "Muundo unaowawezesha wakulima",
      tag_drivers: "Mtandao wa madereva wa kuaminika",
      tag_insights: "Maarifa tayari kwa soko",
      about_pickups: "Kuchukua kwa ufanisi",
      about_pickups_desc: "Panga usafirishaji ndani ya dakika, si masaa, kwa ulinganisho wa kiotomatiki.",
      about_pricing: "Bei wazi",
      about_pricing_desc: "Viwango wazi na uonekano wa safari husaidia kila mtu kupanga vizuri.",
      about_community: "Ukuaji wa jamii",
      about_community_desc: "Usafirishaji zaidi unamaanisha uchumi imara wa vijijini na maisha bora.",
      contact_eyebrow: "Omba usafirishaji",
      contact_title: "Safirisha mavuno yako kwa ujasiri",
      contact_desc: "Shiriki maelezo ya kuchukua na timu yetu ya usafirishaji itakuunganisha na dereva ndani ya dakika chache.",
      contact_hotline: "Simu ya usafirishaji",
      contact_email: "Barua pepe",
      contact_coverage: "Maeneo yanayohudumiwa",
      label_name: "Jina kamili",
      label_phone: "Nambari ya simu",
      label_pickup: "Mahali pa kuchukua",
      label_produce: "Aina ya mazao",
      label_notes: "Maelezo ya usafirishaji",
      ph_name: "Ama Mensah",
      ph_phone: "+255...",
      ph_location: "Kijiji au shamba",
      ph_produce: "Nyanya, mahindi, kakao",
      ph_notes: "Tarehe ya kuchukua, kiasi, soko",
      btn_send_request: "Tuma ombi",
      footer_desc: "Usafirishaji mahiri wa vijijini ulioundwa kwa kilimo cha Afrika.",
      footer_quick: "Viungo vya haraka",
      footer_features: "Vipengele",
      footer_about: "Kuhusu",
      footer_contact: "Wasiliana",
      footer_platform: "Jukwaa",
      footer_help: "Kituo cha Msaada",
      footer_marketplace: "Soko la Wanunuzi",
      footer_support: "Msaada",
      footer_support_center: "Kituo cha Msaada",
      footer_notifications: "Arifa",
      footer_contact_us: "Wasiliana Nasi",
      footer_rights: "AgriMove AI. Haki zote zimehifadhiwa.",
      nav_dashboard: "Dashibodi",
      form_thanks: "Asante! Timu yetu ya usafirishaji itawasiliana nawe hivi karibuni.",
      sms_toast: "💬 SMS ILIYOSADIFISHWA",

      total_requests: "Jumla ya Maombi",
      all_submissions: "Maombi yote ya usafirishaji",
      all_submissions_short: "Maombi yote",
      pending: "Inasubiri",
      accepted: "Imekubaliwa",
      in_transit: "Inasafirishwa",
      delivered: "Imewasili",
      awaiting_driver: "Inasubiri hatua ya dereva",
      driver_assigned: "Dereva ameteuliwa",
      en_route: "Inaendelea njiani",
      completed: "Usafirishaji ulio kamilika",
      completed_short: "Imekamilika",
      ai_route_active: "Uboreshaji wa Njia wa AI Unaofanya Kazi",
      eta_mins: "Muda unaokadiriwa wa kuwasili: dakika {n}",
      ai_route_desc: "Mipango ya njia ya wakati halisi imewashwa kwa kila ombi.",
      notifications: "Arifa",
      no_notifications: "Hakuna arifa bado.",
      request_status: "Hali ya Ombi",
      status_overview: "Muhtasari wa hali kwa maombi yote",
      th_request_id: "Nambari ya Ombi",
      th_pickup: "Kuchukua",
      th_destination: "Marudio",
      th_goods: "Bidhaa",
      th_quantity: "Kiasi",
      th_driver: "Dereva",
      th_status: "Hali",
      searching: "Inatafuta...",
      no_requests: "Hakuna maombi yaliyowasilishwa bado.",
      submit_transport: "Wasilisha Ombi la Usafirishaji",
      farmer_name: "Jina la Mkulima",
      pickup_location: "Mahali pa Kuchukua",
      select_pickup: "Chagua mahali pa kuchukua",
      select_market: "Chagua soko lengwa",
      goods_type: "Aina ya Bidhaa",
      select_crop: "Chagua zao",
      quantity: "Kiasi",
      ph_quantity: "Masanduku 20",
      btn_request_transport: "Omba Usafirishaji",
      market_intel: "Akili ya Soko na Matoleo ya Wanunuzi",
      view_prices: "Angalia Bei za Soko",
      calc_profit: "Kokotoa Faida",
      view_offers: "Angalia Matoleo ya Wanunuzi",
      marketplace_hub: "Kitovu cha Soko",

      available_drivers: "Madereva Waliopo",
      ready_assignments: "Tayari kwa kazi",
      busy_drivers: "Madereva Wenye Kazi",
      on_deliveries: "Wanasafirisha sasa",
      pending_requests: "Maombi Yanayosubiri",
      awaiting_acceptance: "Yanasubiri kukubaliwa",
      active_deliveries: "Usafirishaji unaendelea",
      driver_ai_desc: "Madereva hupokea njia zilizoboreshwa na masasisho ya ETA.",
      available_requests: "Maombi Yanayopatikana",
      accept_jobs_desc: "Kubali, anza, na kamilisha kazi za usafirishaji",
      th_request: "Ombi",
      th_farmer: "Mkulima",
      th_eta: "ETA",
      th_actions: "Vitendo",
      tbd: "Haijulikani",
      btn_accept_job: "Kubali Kazi",
      btn_start_delivery: "Anza Usafirishaji",
      btn_mark_delivered: "Weka Alama Imewasili",
      no_requests_available: "Hakuna maombi yanayopatikana bado.",
      driver_availability: "Upatikanaji wa Madereva",
      driver_roster: "Orodha ya madereva wa sasa",
      th_phone: "Simu",
      th_availability: "Upatikanaji",

      awaiting_assignment: "Inasubiri kuteuliwa",
      active_drivers: "Madereva",
      fleet_health: "Magari",
      tab_prices_short: "Bei",
      tab_buyers_short: "Wanunuzi",
      tab_prices: "Bei",
      tab_buyers: "Wanunuzi",
      admin_add_price_title: "Ongeza Bei",
      admin_crop_name: "Zao",
      admin_region: "Mkoa",
      admin_price_tzs: "Bei",
      admin_demand: "Mahitaji",
      admin_trend: "Mwenendo",
      admin_publish_price: "Ongeza",
      admin_save_price: "Hifadhi",
      admin_delete_price: "Futa",
      admin_empty_price_slot: "Tupu",
      admin_buyer_name: "Mnunuzi",
      admin_rating: "Ukadiriaji",
      admin_revoke: "Batilisha",
      admin_verify_buyer: "Thibitisha",
      admin_no_buyers: "Hakuna",
      admin_driver_roster: "Madereva",
      quick_search: "Tafuta Haraka",
      search_ph: "Tafuta kwa nambari ya ombi, mkulima, au dereva...",
      display_settings: "Mipangilio ya Onyesho",
      display_settings_desc: "Badilisha mandhari ya giza/mwanga kwa uonekano bora.",
      all_requests: "Maombi Yote",
      realtime_mgmt: "Usimamizi wa maombi wa wakati halisi",
      th_gps: "GPS Sim",
      unassigned: "Hajateuliwa",
      no_requests_admin: "Hakuna maombi bado.",
      btn_move_gps: "📍 Songesha GPS",
      add_crop_price: "Ongeza Bei Mpya ya Zao",
      crop_name: "Jina la Zao",
      region: "Mkoa",
      price_tzs: "Bei (TZS/mfuko)",
      demand_level: "Kiwango cha Mahitaji",
      price_trend: "Mwenendo wa Bei",
      low: "Chini",
      medium: "Wastani",
      high: "Juu",
      stable: "Imara",
      rising: "Inapanda",
      falling: "Inashuka",
      btn_publish_price: "Chapisha Bei",
      price_guidelines: "Miongozo ya Bei",
      price_guidelines_desc: "Algoriti za akili ya soko hutegemea thamani hizi kupendekeza masoko na kuboresha mizigo.",
      price_guidelines_sub: "Hakikisha bei zinasasishwa kila wiki kuzuia uharibifu wa mazao.",

      awaiting_driver_short: "Inasubiri dereva",
      en_route_short: "Njiani",
      delivery_status_dist: "Usambazaji wa Hali ya Usafirishaji",
      request_trend: "Mwenendo wa Maombi (Siku 7)",
      crop_demand: "Kielelezo cha Mahitaji ya Mazao",
      driver_deliveries: "Orodha ya Usafirishaji wa Madereva",
      market_price_activity: "Shughuli za Bei za Soko",
      completion_rate: "Kiwango cha Ukamilifu",
      pct_delivered: "{n}% ya maombi yamewasili",
      no_data: "Hakuna data bado",
      avg_eta: "Wastani wa ETA",
      mins_to_market: "dakika hadi sokoni",
      chart_requests: "Maombi",
      chart_demand: "Alama ya Kielelezo cha Mahitaji",
      chart_jobs: "Jumla ya Kazi Zilizokamilika",
      chart_avg_price: "Wastani wa TZS kwa Mfuko",

      shamba_form_title: "Omba Usafiri / Tenga Mzigo",
      shamba_form_desc: "Weka maelezo ya mzigo wako ili kupata wakulima wenzako wa karibu na kugawana gharama za usafiri.",
      shamba_full_name: "Jina lako Kamili",
      shamba_phone: "Namba ya Simu (M-Pesa)",
      shamba_district: "Wilaya",
      shamba_ward: "Kata",
      shamba_village: "Kijiji",
      shamba_crop: "Zao la Kusafirisha",
      shamba_bags: "Idadi ya Mifuko (Bags)",
      shamba_date: "Tarehe ya Usafirishaji",
      shamba_submit: "🚀 Tuma Ombi & Tafuta Mechi",
      shamba_ph_name: "Mh. Juma Hamisi",
      shamba_ph_district: "Mbeya Vijijini",
      shamba_ph_ward: "Mbeya Mjini",
      shamba_ph_village: "Kijiji cha Uyole",
      crop_maize: "🌽 Mahindi",
      crop_rice: "🌾 Mpunga / Mchele",
      crop_cassava: "🍠 Muhogo",
      crop_tomato: "🍅 Nyanya",
      crop_onion: "🧅 Vitunguu",
      crop_coffee: "☕ Kahawa",
      crop_cashew: "🥜 Korosho",
      shamba_matches_title: "🤝 Wakulima Waliolingana Karibu Nawe",
      shamba_matches_desc: "Wakulima hawa wanasafirisha zao kama lako kutoka kata/wilaya yako ndani ya muda unaofanana:",
      shamba_no_matches: "Hakuna wakulima wengine wa karibu waliolingana kwa sasa. Utajulishwa mara wakipatikana.",
      shamba_pools_title: "🚛 Magari ya Kikundi Yanayopatikana (Pools)",
      shamba_pools_desc: "Bofya \"Jiunge\" ili kuchukua nafasi na kusafirisha mizigo yako kwa pamoja.",
      shamba_route: "Njia:",
      shamba_departure: "Tarehe ya kuondoka:",
      shamba_slots: "Nafasi zilizobaki:",
      shamba_driver: "Dereva:",
      shamba_per_bag: "kwa kila mfuko",
      shamba_join: "Jiunge",
      shamba_no_pools: "Hakuna magari ya kikundi yaliyo wazi kwa sasa. Unda ombi kushoto ili magari yapangwe.",
      shamba_modal_title: "Jiunge na Gari la Kikundi",
      shamba_modal_cost: "Gharama ya kila mfuko ni",
      shamba_modal_name: "Jina lako",
      shamba_modal_phone: "Namba ya Simu",
      shamba_modal_bags: "Idadi ya Mifuko",
      shamba_modal_slots: "Nafasi zilizobaki:",
      shamba_modal_total: "Jumla ya Gharama yako:",
      shamba_cancel: "Ghairi",
      shamba_confirm: "Thibitisha",
      shamba_sms_inbox: "📱 SIMULATED SMS INBOX (2G SMS Receiver)",
      shamba_sms_close: "[Funga]",
      shamba_sms_from: "KUTOKA: AgriMove INFO\nUJUMBE:",
      shamba_match_partner: "Mshirika: {name} | Mzigo: mifuko {bags}",
      shamba_match_village: "Kijiji:",
      shamba_match_pickup: "Tarehe ya Pickup:",
      shamba_match_days: "Umbali wa siku 3",
      shamba_error: "Hitilafu:",
      transport_submit_failed: "Imeshindikana kusajili ombi.",
      transport_bags_exceed: "Mifuko haiwezi kuzidi nafasi zilizobaki!",
      transport_join_failed: "Imeshindikana kujiunga na gari.",
      sms_inbox_title: "📱 Simulated SMS Inbox",
      sms_inbox_empty: "Hakuna SMS bado. Wasilisha ombi la usafirishaji hapo juu ili kupokea arifa ya SMS.",
      sms_help_title: "SMS kupitia Sandbox ya Africa's Talking",
      sms_help_body: "Baada ya kuwasilisha ombi la usafirishaji, SMS inatumwa kupitia Africa's Talking (username: sandbox). Fungua simulator ya AT kuuisoma — si kwenye dashibodi hii.",
      sms_help_step1: "1. Sajili namba yako (+255...) kwenye sandbox ya AT.",
      sms_help_step2: "2. Wasilisha fomu hapa chini kwa namba ile ile.",
      sms_help_step3: " kuona SMS.",
    },
  };

  function getLang() {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === "sw" || stored === "en" ? stored : DEFAULT_LANG;
  }

  function hasTranslation(lang, key) {
    return Boolean(T[lang]?.[key] || T[DEFAULT_LANG]?.[key]);
  }

  function lookup(lang, key) {
    const catalog = T[lang] || T[DEFAULT_LANG];
    return catalog[key] ?? T[DEFAULT_LANG][key] ?? null;
  }

  /** Translate a key — usable from other scripts */
  window.__ = function (key, vars) {
    let text = lookup(getLang(), key);
    if (text == null) text = key;
    if (vars) {
      Object.keys(vars).forEach((k) => {
        text = text.replace(`{${k}}`, vars[k]);
      });
    }
    return text;
  };

  window.i18nStatus = function (status) {
    const lang = getLang();
    return (STATUS[lang] && STATUS[lang][status]) || status;
  };

  function syncCookie(lang) {
    fetch("/api/set-language", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang }),
    }).catch(() => {});
  }

  function applyLanguage(lang) {
    if (lang !== "en" && lang !== "sw") lang = DEFAULT_LANG;
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang === "sw" ? "sw" : "en";
    syncCookie(lang);

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (!hasTranslation(lang, key)) return;
      let text = lookup(lang, key);
      const eta = el.getAttribute("data-i18n-eta");
      if (eta) text = text.replace("{n}", eta);
      const pct = el.getAttribute("data-i18n-pct");
      if (pct) text = text.replace("{n}", pct);
      el.textContent = text;
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (!hasTranslation(lang, key)) return;
      el.placeholder = lookup(lang, key);
    });

    document.querySelectorAll("[data-i18n-title]").forEach((el) => {
      const key = el.getAttribute("data-i18n-title");
      if (!hasTranslation(lang, key)) return;
      el.title = lookup(lang, key);
    });

    document.querySelectorAll(".i18n-status[data-status]").forEach((el) => {
      const status = el.getAttribute("data-status");
      el.textContent = (STATUS[lang] && STATUS[lang][status]) || status;
    });

    document.querySelectorAll(".i18n-status-text").forEach((el) => {
      const status = el.textContent.trim();
      if (STATUS[lang] && STATUS[lang][status]) {
        el.textContent = STATUS[lang][status];
      } else if (STATUS[lang] && STATUS[lang][status.toLowerCase()]) {
        el.textContent = STATUS[lang][status.toLowerCase()];
      }
    });

    const langBtn = document.getElementById("langToggleBtn");
    if (langBtn) {
      langBtn.textContent = lang === "sw" ? lookup("sw", "btn_lang_en") : lookup("en", "btn_lang_sw");
    }

    const adminModeToggle = document.getElementById("darkModeToggle");
    if (adminModeToggle && !document.getElementById("admin-dashboard")) {
      if (document.body.classList.contains("dark-mode")) {
        adminModeToggle.textContent = lookup(lang, "btn_light");
      } else {
        adminModeToggle.textContent = lookup(lang, "btn_dark");
      }
    }

    window.dispatchEvent(new CustomEvent("agrimove:languagechange", { detail: { lang } }));
  }

  function toggleLanguage() {
    const next = getLang() === "en" ? "sw" : "en";
    applyLanguage(next);
    if (document.getElementById("admin-dashboard")) {
      window.location.reload();
    }
  }

  window.applyAgriMoveLanguage = applyLanguage;
  window.toggleAgriMoveLanguage = toggleLanguage;

  document.addEventListener("DOMContentLoaded", () => {
    applyLanguage(getLang());
    const langBtn = document.getElementById("langToggleBtn");
    if (langBtn) {
      langBtn.addEventListener("click", toggleLanguage);
    }
  });
})();
