"""
Pocket Cash Cards - Shop Showcase eBay Image & Inventory Sync
==============================================================
Zero-token script that:
1. Queries pocket_cash_cards.db to verify active status and live prices for
   the 8 Featured Live Hits and 8 eBay Store Department showcase cards.
   If a featured item has sold/ended, automatically replaces it with the
   next highest-value active 12-digit Pocket Cash listing from the DB.
2. Pulls the actual front (and back) high-resolution card scans from eBay
   using EbayClient (Trading GetItem with OAuth IAF token).
3. Converts and saves optimized .webp card images in assets/images/shop/
   so getpocketcash.com loads fast and never breaks on hotlink changes.
4. Updates the PRODUCTS array in shop.html between explicit marker comments
   and cleans up any orphaned images in assets/images/shop/.
"""

import io
import json
import os
import re
import sqlite3
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHOP_HTML_PATH = os.path.join(BASE_DIR, "shop.html")
SHOP_IMG_DIR = os.path.join(BASE_DIR, "assets", "images", "shop")
DB_PATH = r"G:\Tools\data\pocket_cash_cards.db"
EBAY_CLIENT_DIR = r"G:\AI\scratch\ebay_batch_auditor"

MAX_IMAGE_DIM = 720
WEBP_QUALITY = 85

# Curated defaults for the 8 Featured Live Hits (auto-replaced if sold)
FEATURED_PRESETS: List[Dict[str, Any]] = [
    {
        "item_id": "227507968586",
        "badge": "1/1 Masterpiece SSP",
        "title": "2026 Parkside IndyCar Jonathan Browne 1/1 ONE OF ONE",
        "subtitle": "Chip Ganassi Racing Indy NXT • True 1/1 Grail",
        "specs": ["Exact card scanned front & back", "True 1-of-1 pack-pulled SSP", "Armored Ground Advantage shipping"],
        "icon": "🏎️",
        "imageBg": "from-amber-950/70 to-slate-900",
    },
    {
        "item_id": "227507968574",
        "badge": "On-Card Auto /100",
        "title": "2026 Choice Banana Ball Mo'ne Davis RC AUTO /100 #29",
        "subtitle": "Indianapolis Clowns • Serial Numbered /100 Rookie Auto",
        "specs": ["Authenticated Choice BBCL Autograph", "Flagship #29 Rookie Card", "Ships in magnetic One-Touch armor"],
        "icon": "🍌",
        "imageBg": "from-yellow-950/70 to-slate-900",
    },
    {
        "item_id": "298672170731",
        "badge": "Case Hit SSP 3/6",
        "title": "2026 Parkside IndyCar Nolan Siegel Numerics SSP 3/6",
        "subtitle": "Arrow McLaren • Ultra-Rare Serial Numbered 3/6 Insert",
        "specs": ["Serial-numbered 3 of only 6 made", "Arrow McLaren IndyCar rising star", "High-res front & back scans"],
        "icon": "🏁",
        "imageBg": "from-orange-950/70 to-slate-900",
    },
    {
        "item_id": "227507968583",
        "badge": "Game-Used Relic",
        "title": "2026 Choice Banana Ball Coach RAC Jersey Relic",
        "subtitle": "Savannah Bananas • Robertanthony Cruz Relic Insert",
        "specs": ["Authentic Savannah Bananas relic swatch", "Fan-favorite Coach RAC chase hit", "Armored tracked shipping"],
        "icon": "👕",
        "imageBg": "from-emerald-950/70 to-slate-900",
    },
    {
        "item_id": "227507968570",
        "badge": "On-Card Auto /100",
        "title": "2026 Choice Banana Ball Marshall Shill AUTO /100",
        "subtitle": "Firefighters • Serial Numbered /100 Certified Auto",
        "specs": ["Certified on-card signature /100", "Firefighters pitching standout", "Fast Top-Rated Seller dispatch"],
        "icon": "🔥",
        "imageBg": "from-red-950/70 to-slate-900",
    },
    {
        "item_id": "298648724771",
        "badge": "Phantoms SSP /50",
        "title": "2026 Parkside IndyCar Graham Rahal Phantoms /50 #PH7",
        "subtitle": "Rahal Letterman Lanigan • Case Hit SSP /50",
        "specs": ["Serial-numbered to /50", "Case-hit Phantoms insert #PH7", "$1 Tracked Standard Envelope"],
        "icon": "👻",
        "imageBg": "from-indigo-950/70 to-slate-900",
    },
    {
        "item_id": "298648724768",
        "badge": "Foil Parallel 1/14",
        "title": "2026 Choice Banana Ball Eli Paton RC Foil 1/14 #16",
        "subtitle": "Indianapolis Clowns • 1-of-14 Rookie Foil Parallel",
        "specs": ["Print run of only 14 copies", "Bookend 1/14 serial stamp", "$1 Tracked Standard Envelope"],
        "icon": "✨",
        "imageBg": "from-amber-950/70 to-slate-900",
    },
    {
        "item_id": "227509086198",
        "badge": "PBA HOF RC Slab",
        "title": "1990 Collect-A-Card Kingpins Earl Anthony RC #1 (C3 8)",
        "subtitle": "PBA Bowling Hall of Fame Legend • Flagship #1 Card",
        "specs": ["Key #1 card in the 1990 Kingpins set", "6-time PBA Player of the Year", "Protected in C3 8 holder"],
        "icon": "🎳",
        "imageBg": "from-purple-950/70 to-slate-900",
    },
]

# 8 eBay Store Departments with SQL patterns to pull a real representative Pocket Cash listing
EBAY_DEPTS: List[Dict[str, Any]] = [
    {
        "key": "dept_indy",
        "sql_where": "title LIKE '%2026 Parkside IndyCar%'",
        "badge": "160+ Cards Live",
        "statusBadge": "$1 Shipping",
        "title": "2026 Parkside IndyCar & Indy NXT Singles",
        "subtitle": "Base, P1 Polesitters, Helmet Hardware, Foils & Autos",
        "price": "From $1.99",
        "specs": ["160+ active singles in stock now", "Complete your master set fast", "$1 flat tracked ESE shipping"],
        "icon": "🏎️",
        "imageBg": "from-emerald-950/60 to-slate-900",
        "ctaText": "Shop 160+ IndyCar Singles ↗",
        "searchQuery": "2026 Parkside IndyCar",
        "customId": "shop_dept_indy",
    },
    {
        "key": "dept_banana",
        "sql_where": "title LIKE '%Banana Ball%'",
        "badge": "125+ Cards Live",
        "statusBadge": "$1 Shipping",
        "title": "2026 Choice Banana Ball & Savannah Bananas",
        "subtitle": "Bananas, Party Animals, Firefighters, Tailgaters & Clowns",
        "price": "From $1.50",
        "specs": ["125+ active singles, SPs & autos", "All 6 BBCL teams represented", "$1 flat tracked ESE shipping"],
        "icon": "🍌",
        "imageBg": "from-yellow-950/60 to-slate-900",
        "ctaText": "Shop 125+ Banana Ball Cards ↗",
        "searchQuery": "Banana Ball",
        "customId": "shop_dept_banana",
    },
    {
        "key": "dept_intl",
        "sql_where": "(title LIKE '%CPBL%' OR title LIKE '%Czech%' OR title LIKE '%KBO%')",
        "badge": "520+ Cards Live",
        "statusBadge": "$1 Shipping",
        "title": "International Baseball (CPBL Taiwan, Czech WBC & KBO)",
        "subtitle": "1994 CPBL, 2023 Czech Baseball & 2025 SCC Korean KBO",
        "price": "From $1.99",
        "specs": ["275+ 1994 CPBL Taiwan singles", "245+ Czech Baseball & 70+ KBO cards", "Rare imports shipped from Oklahoma"],
        "icon": "🌍",
        "imageBg": "from-cyan-950/60 to-slate-900",
        "ctaText": "Shop International Baseball ↗",
        "searchQuery": "CPBL Czech KBO",
        "customId": "shop_dept_intl",
    },
    {
        "key": "dept_ocho",
        "sql_where": "(title LIKE '%High Gear%' OR title LIKE '%Kingpins%' OR title LIKE '%Sumo%' OR title LIKE '%UFA%')",
        "badge": "380+ Cards Live",
        "statusBadge": "$1 Shipping",
        "title": "PRCA Rodeo, PBA Bowling & The Ocho Sports",
        "subtitle": "1995 High Gear Rodeo, 1990 Kingpins, Sumo & UFA Frisbee",
        "price": "From $1.99",
        "specs": ["220+ 1995 High Gear PRCA Rodeo cards", "95+ 1990 Kingpins & 65+ UFA Frisbee", "100+ BBM Japanese Sumo legends"],
        "icon": "🤠",
        "imageBg": "from-amber-950/60 to-slate-900",
        "ctaText": "Shop Rodeo & The Ocho ↗",
        "searchQuery": "Rodeo Kingpins UFA Sumo",
        "customId": "shop_dept_ocho",
    },
    {
        "key": "dept_milb",
        "sql_where": "(title LIKE '%Lugnuts%' OR title LIKE '%Danbury%' OR title LIKE '%Midwest%')",
        "badge": "100+ Cards Live",
        "statusBadge": "$1 Shipping",
        "title": "Minor League Baseball & FPHL Hockey Team Sets",
        "subtitle": "Lansing Lugnuts, Midwest League Prospects & Danbury Hat Tricks",
        "price": "From $1.99",
        "specs": ["2018-2023 Lansing Lugnuts singles", "2025-26 Danbury Hat Tricks FPHL (50+)", "1999 Multi-Ad Midwest Prospects"],
        "icon": "⚾",
        "imageBg": "from-blue-950/60 to-slate-900",
        "ctaText": "Shop MiLB & FPHL Singles ↗",
        "searchQuery": "Lansing Lugnuts Danbury Midwest",
        "customId": "shop_dept_milb",
    },
    {
        "key": "dept_womens",
        "sql_where": "(title LIKE '%PWHL%' OR title LIKE '%Athletes Unlimited%')",
        "badge": "45+ Cards Live",
        "statusBadge": "$1 Shipping",
        "title": "Women's Pro Sports (PWHL Hockey & AU Softball)",
        "subtitle": "2025-26 Fleer Ultra PWHL & 2023 Topps Athletes Unlimited",
        "price": "From $1.99",
        "specs": ["27+ Topps AU Softball (OU & OSU stars)", "20+ Fleer Ultra PWHL Hockey singles", "$1 flat tracked ESE shipping"],
        "icon": "🥎",
        "imageBg": "from-teal-950/60 to-slate-900",
        "ctaText": "Shop PWHL & AU Softball ↗",
        "searchQuery": "Athletes Unlimited PWHL",
        "customId": "shop_dept_womens",
    },
    {
        "key": "dept_political",
        "sql_where": "title LIKE '%2016 Decision%'",
        "badge": "50+ Cards Live",
        "statusBadge": "$1 Shipping",
        "title": "2016 Decision Political & Pop Culture Non-Sports",
        "subtitle": "Candidates, Influencers, Political Gems & Historical Cards",
        "price": "From $1.99",
        "specs": ["50+ 2016 Decision Political singles", "Candidates, Finalists & Influencers", "Fast combined shipping discounts"],
        "icon": "🏛️",
        "imageBg": "from-rose-950/60 to-slate-900",
        "ctaText": "Shop Decision Political ↗",
        "searchQuery": "2016 Decision",
        "customId": "shop_dept_political",
    },
    {
        "key": "dept_all",
        "sql_where": "list_price >= 100",
        "badge": "10,500+ Total",
        "statusBadge": "Full Catalog",
        "title": "Full Pocket Cash eBay Storefront (All Sports)",
        "subtitle": "MLB, NFL, NBA, NCAA, Vintage & Niche Singles",
        "price": "From $1.49",
        "specs": ["Over 10,500 live fixed-price singles", "New cards uploaded daily", "Top-Rated Seller service"],
        "icon": "🏪",
        "imageBg": "from-slate-800 to-slate-950",
        "ctaText": "Browse All 10,500+ Cards ↗",
        "ctaUrlLiteral": "https://www.ebay.com/str/pocketcash?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339204284&customid=shop_dept_all&toolid=10001&mkevt=1",
    },
]

ARDMORE_BOOTH_ITEMS: List[Dict[str, Any]] = [
    {
        "category": "ardmore-booth",
        "badge": "Booth #64 Exclusive",
        "statusBadge": "In-Store at Ardmore",
        "title": "$5 Pocket Cash Mystery Vault Packs",
        "subtitle": "Curated Repacks with Stars, Rookies, Parallels & Vintage",
        "price": "$5.00",
        "specs": ["Loaded with MLB, NFL & NBA stars", "Zero junk-era filler bloat", "Available at 219 W. Main St. #64"],
        "icon": "🎁",
        "image": "assets/images/ardmore/baseball-cards-wax-packs-booth-64-ardmore-ok.webp",
        "imageFit": "cover",
        "imageAlt": "$5 Pocket Cash Mystery Vault Packs & wax at Ardmore Booth #64",
        "imageBg": "from-emerald-950/70 to-slate-900",
        "ctaText": "📍 Visit Booth #64 in Ardmore →",
        "ctaUrl": "ardmore.html",
        "external": False,
    },
    {
        "category": "ardmore-booth",
        "badge": "Booth #64 Showcase",
        "statusBadge": "In-Store at Ardmore",
        "title": "MLB, NFL, NBA & Oklahoma Sooners Star Singles",
        "subtitle": "Hand-Priced $1–$50 Raw Singles in Sleeves & One-Touches",
        "price": "$1.00 - $50+",
        "specs": ["Fresh inventory rotated every month", "Inspect condition in person before buying", "Zero shipping fees"],
        "icon": "⭐",
        "image": "assets/images/ardmore/modern-rookie-cards-stars-ardmore-ok-showcase.webp",
        "imageFit": "cover",
        "imageAlt": "Modern rookie cards and star singles showcase at Ardmore Booth #64",
        "imageBg": "from-red-950/70 to-slate-900",
        "ctaText": "📍 See Booth #64 Showcase →",
        "ctaUrl": "ardmore.html",
        "external": False,
    },
    {
        "category": "ardmore-booth",
        "badge": "Custom 3D Print",
        "statusBadge": "In-Store at Ardmore",
        "title": "3D-Printed Slab Stands, Stadium Risers & Caddies",
        "subtitle": "Heavy-Duty PLA+ Display Stands for PSA, SGC & One-Touches",
        "price": "$7.99 - $19.99",
        "specs": ["Single hex stands & 3-tier risers", "4-slot desk sorting caddies", "Pick up locally at Booth #64"],
        "icon": "🖨️",
        "image": "assets/images/ardmore/3d-printed-card-stands-booth-merchandising-ardmore-ok.webp",
        "imageFit": "cover",
        "imageAlt": "Custom 3D-printed card stands and risers at Booth #64",
        "imageBg": "from-blue-950/70 to-slate-900",
        "ctaText": "📍 Pick Up at Booth #64 →",
        "ctaUrl": "ardmore.html",
        "external": False,
    },
    {
        "category": "ardmore-booth",
        "badge": "Local Supply Hub",
        "statusBadge": "In-Store at Ardmore",
        "title": "In-Store Penny Sleeves, Toploaders & Storage Boxes",
        "subtitle": "Grab Essential Card Protection Right Off Main Street",
        "price": "Retail Packs",
        "specs": ["35pt toploaders & archival penny sleeves", "Magnetic One-Touch holders", "Open Mon-Sat at Texoma Trading Post"],
        "icon": "🛡️",
        "image": "assets/images/ardmore/hobby-supplies-toploaders-penny-sleeves-ardmore-ok.webp",
        "imageFit": "cover",
        "imageAlt": "Toploaders, penny sleeves, and hobby supplies at Ardmore Booth #64",
        "imageBg": "from-teal-950/70 to-slate-900",
        "ctaText": "📍 Directions & Hours →",
        "ctaUrl": "ardmore.html",
        "external": False,
    },
]

SUPPLIES_ITEMS: List[Dict[str, Any]] = [
    {
        "category": "supplies",
        "badge": "Daily Essential",
        "statusBadge": "Amazon Prime",
        "title": "Ultra PRO 35pt Toploaders & Penny Sleeves Bundle",
        "subtitle": "Crystal-Clear Acid-Free Protection for Standard Cards",
        "price": "Check Live Price",
        "specs": ['Fits standard 2.5" x 3.5" 35pt cards', "Zero PVC archival polypropylene", "Fast Prime delivery"],
        "icon": "🛡️",
        "image": "assets/images/supplies/ultra-pro-35pt-toploaders.webp",
        "imageFit": "contain",
        "imageAlt": "Ultra PRO 35pt Toploaders & Penny Sleeves",
        "imageBg": "from-slate-800 to-slate-950",
        "ctaText": "🛒 Buy on Amazon Prime ↗",
        "ctaUrl": "https://www.amazon.com/dp/B000CO82NA?tag=pocketcash01-20",
        "external": True,
    },
    {
        "category": "supplies",
        "badge": "Grading Standard",
        "statusBadge": "Amazon Prime",
        "title": "Cardboard Gold Card Saver 1 Semi-Rigid Holders",
        "subtitle": "Official Holder for PSA, SGC, BGS & eBay Standard Envelope",
        "price": "Check Live Price",
        "specs": ["Required for PSA/SGC submissions", "Ideal for $1 eBay Standard Envelope", "Crystal clear 9-mil archival plastic"],
        "icon": "📦",
        "image": "assets/images/supplies/card-saver-1-semi-rigid-holders.webp",
        "imageFit": "contain",
        "imageAlt": "Cardboard Gold Card Saver 1 Semi-Rigid Holders",
        "imageBg": "from-amber-950/60 to-slate-900",
        "ctaText": "🛒 Buy on Amazon Prime ↗",
        "ctaUrl": "https://www.amazon.com/s?k=Cardboard+Gold+Card+Saver+1&tag=pocketcash01-20",
        "external": True,
    },
    {
        "category": "supplies",
        "badge": "PC Showcase Favorite",
        "statusBadge": "Amazon Prime",
        "title": "Pro-Mold 35pt Magnetic One-Touch (Holds Sleeved Card)",
        "subtitle": "UV-Protected Magnetic Case Designed to Fit Penny Sleeves",
        "price": "Check Live Price",
        "specs": ["Holds card WITH a penny sleeve on", "Prevents chrome/refractor surface scratches", "5-year UV protection"],
        "icon": "💎",
        "image": "assets/images/supplies/pro-mold-35pt-magnetic-one-touch.webp",
        "imageFit": "contain",
        "imageAlt": "Pro-Mold 35pt Magnetic One-Touch Case",
        "imageBg": "from-emerald-950/60 to-slate-900",
        "ctaText": "🛒 Buy on Amazon Prime ↗",
        "ctaUrl": "https://www.amazon.com/s?k=Pro-Mold+MH35S+35pt+magnetic+holder+with+penny+sleeve&tag=pocketcash01-20",
        "external": True,
    },
    {
        "category": "supplies",
        "badge": "40+ Items Compared",
        "statusBadge": "Full Guide",
        "title": "Complete Archival Card Supplies & Grading Prep Guide",
        "subtitle": "Compare 40+ Card Holders, Loupes, Centering Tools & Storage Boxes",
        "price": "Free Guide",
        "specs": ["Side-by-side Amazon & eBay price links", "Thick relic & booklet point-gauge chart", "PSA & SGC submission prep checklist"],
        "icon": "📑",
        "image": "assets/images/supplies/bcw-3200-monster-storage-box.webp",
        "imageFit": "contain",
        "imageAlt": "Archival Card Storage & Supplies Guide",
        "imageBg": "from-purple-950/60 to-slate-900",
        "ctaText": "Open Full Supplies Guide →",
        "ctaUrl": "supplies.html",
        "external": False,
    },
]


def get_ebay_client():
    if EBAY_CLIENT_DIR not in sys.path:
        sys.path.insert(0, EBAY_CLIENT_DIR)
    from ebay_client import EbayClient

    client = EbayClient()
    if not client.is_configured():
        raise RuntimeError("eBay API credentials not configured.")
    client.refresh_access_token()
    return client


def fetch_ebay_item_details(client, item_id: str) -> Dict[str, Any]:
    """Fetch live listing title, price, status, and PictureURLs via Trading GetItem."""
    xml_req = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
        f"<ItemID>{item_id}</ItemID>"
        "<DetailLevel>ReturnAll</DetailLevel>"
        "</GetItemRequest>"
    )
    resp = client._request_with_retry(
        "POST",
        client.trading_endpoint,
        data=xml_req.encode("utf-8"),
        headers=client._get_trading_headers("GetItem"),
        timeout=30,
    )
    root = ET.fromstring(resp.content)
    ns = {"e": "urn:ebay:apis:eBLBaseComponents"}
    ack = root.findtext("e:Ack", "", ns)
    if ack not in ("Success", "Warning"):
        errs = [e.findtext("e:LongMessage", "", ns) for e in root.findall(".//e:Errors", ns)]
        raise RuntimeError(f"GetItem({item_id}) failed ({ack}): {'; '.join(errs)}")

    title = root.findtext(".//e:Item/e:Title", "", ns)
    status = root.findtext(".//e:Item/e:SellingStatus/e:ListingStatus", "", ns)
    price_text = root.findtext(".//e:Item/e:SellingStatus/e:CurrentPrice", "", ns)
    price = float(price_text) if price_text else None
    pics = [
        p.text.strip()
        for p in root.findall(".//e:Item/e:PictureDetails/e:PictureURL", ns)
        if p.text and p.text.strip()
    ]
    return {"item_id": item_id, "title": title, "status": status, "price": price, "pictures": pics}


def upgrade_ebay_img_url(url: str) -> str:
    """Prefer higher-res 1600px EPS image when eBay returns $_1.JPG thumbnail size."""
    return re.sub(r"/\$_1\.(JPG|PNG|WEBP)", r"/$_57.\1", url, flags=re.IGNORECASE)


def download_and_optimize_webp(url: str, dest_path: str, force: bool = False) -> bool:
    """Download an image URL and save as a fast, crisp .webp thumbnail."""
    if os.path.exists(dest_path) and not force:
        return True

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    candidates = [upgrade_ebay_img_url(url)]
    if candidates[0] != url:
        candidates.append(url)

    for candidate_url in candidates:
        try:
            r = requests.get(candidate_url, timeout=25, headers={"User-Agent": "PocketCashSiteSync/1.0"})
            if r.status_code != 200 or not r.content:
                continue
            img = Image.open(io.BytesIO(r.content))
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            elif img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (15, 24, 38))
                bg.paste(img, mask=img.split()[3])
                img = bg
            img.thumbnail((MAX_IMAGE_DIM, MAX_IMAGE_DIM), Image.Resampling.LANCZOS)
            img.save(dest_path, "WEBP", quality=WEBP_QUALITY, method=6)
            return True
        except Exception as exc:
            print(f"  [!] Failed {candidate_url}: {exc}")
    return False


def pick_replacement_hit(cur: sqlite3.Cursor, used_ids: set) -> Optional[Tuple[str, str, float]]:
    placeholders = ",".join("?" for _ in used_ids) if used_ids else "''"
    sql = f"""
        SELECT ebay_item_id, title, list_price
        FROM inventory
        WHERE status='ACTIVE'
          AND ebay_item_id IS NOT NULL
          AND length(ebay_item_id)=12
          AND ebay_item_id NOT LIKE '9000%'
          AND ebay_item_id NOT IN ({placeholders})
        ORDER BY list_price DESC
        LIMIT 1
    """
    return cur.execute(sql, tuple(used_ids)).fetchone()


def pick_dept_item(cur: sqlite3.Cursor, where_clause: str, exclude_ids: set) -> Optional[Tuple[str, str, float]]:
    placeholders = ",".join("?" for _ in exclude_ids) if exclude_ids else "''"
    sql = f"""
        SELECT ebay_item_id, title, list_price
        FROM inventory
        WHERE status='ACTIVE'
          AND ebay_item_id IS NOT NULL
          AND length(ebay_item_id)=12
          AND ebay_item_id NOT LIKE '9000%'
          AND ebay_item_id NOT IN ({placeholders})
          AND ({where_clause})
        ORDER BY list_price DESC
        LIMIT 1
    """
    return cur.execute(sql, tuple(exclude_ids)).fetchone()


def epn_item_url(item_id: str) -> str:
    return (
        f"https://www.ebay.com/itm/{item_id}"
        f"?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339204284"
        f"&customid=shop_hit_{item_id}&toolid=10001&mkevt=1"
    )


def epn_store_search_url(nkw: str, custom_id: str) -> str:
    from urllib.parse import quote

    return (
        f"https://www.ebay.com/sch/i.html?_ssn=pocketcash&_nkw={quote(nkw)}"
        f"&_sop=12&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339204284"
        f"&customid={custom_id}&toolid=10001&mkevt=1"
    )


def sync_shop_showcase(force_images: bool = False, deploy: bool = True) -> bool:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    if not os.path.exists(SHOP_HTML_PATH):
        raise FileNotFoundError(f"shop.html not found: {SHOP_HTML_PATH}")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    client = get_ebay_client()

    referenced_files = set()
    products: List[Dict[str, Any]] = []
    used_hit_ids = set()

    print("[*] Syncing 8 Featured Live Hits from eBay...")
    for preset in FEATURED_PRESETS:
        item_id = preset["item_id"]
        row = cur.execute(
            "SELECT status, list_price, title FROM inventory WHERE ebay_item_id = ?", (item_id,)
        ).fetchone()
        is_preset = True

        if not row or str(row[0]).upper() != "ACTIVE":
            repl = pick_replacement_hit(cur, used_hit_ids | {p["item_id"] for p in FEATURED_PRESETS})
            if repl:
                item_id, repl_title, repl_price = repl
                is_preset = False
                print(f"  [!] Preset {preset['item_id']} no longer active -> swapped in {item_id} ({repl_title})")

        details = fetch_ebay_item_details(client, item_id)
        if details["status"] != "Active":
            repl = pick_replacement_hit(cur, used_hit_ids | {item_id})
            if repl:
                item_id, repl_title, repl_price = repl
                is_preset = False
                details = fetch_ebay_item_details(client, item_id)

        used_hit_ids.add(item_id)
        price_val = details["price"] if details["price"] is not None else (float(row[1]) if row else 0.0)
        price_str = f"${price_val:.2f}"
        title = preset["title"] if is_preset else re.sub(r"\s+\d{6}$", "", details["title"]).strip()
        subtitle = preset["subtitle"] if is_preset else "Live Active Pocket Cash eBay Listing • Direct Scan"
        badge = preset["badge"] if is_preset else "Featured Live Hit"
        specs = (
            preset["specs"]
            if is_preset
            else ["Exact card scanned front & back", "Verified active in Pocket Cash store", "Fast Top-Rated Seller dispatch"]
        )

        pics = details["pictures"]
        front_rel = None
        back_rel = None
        if pics:
            front_name = f"{item_id}_front.webp"
            if download_and_optimize_webp(pics[0], os.path.join(SHOP_IMG_DIR, front_name), force=force_images):
                front_rel = f"assets/images/shop/{front_name}"
                referenced_files.add(front_name)
        if len(pics) > 1:
            back_name = f"{item_id}_back.webp"
            if download_and_optimize_webp(pics[1], os.path.join(SHOP_IMG_DIR, back_name), force=force_images):
                back_rel = f"assets/images/shop/{back_name}"
                referenced_files.add(back_name)

        print(f"  [+] Hit {item_id} ({price_str}): front={'OK' if front_rel else 'NONE'}, back={'OK' if back_rel else 'NONE'}")

        products.append(
            {
                "category": "featured-hits",
                "ebayItemId": item_id,
                "badge": badge,
                "statusBadge": "In Stock on eBay",
                "title": title,
                "subtitle": subtitle,
                "price": price_str,
                "specs": specs,
                "icon": preset["icon"],
                "image": front_rel,
                "backImage": back_rel,
                "imageFit": "contain",
                "imageAlt": f"{title} - actual eBay card scan",
                "imageBg": preset["imageBg"],
                "ctaText": f"⚡ Buy on eBay ({price_str}) ↗",
                "ctaUrl": epn_item_url(item_id),
                "external": True,
            }
        )

    print("[*] Syncing 8 eBay Store Department sample scans from eBay...")
    for dept in EBAY_DEPTS:
        row = pick_dept_item(cur, dept["sql_where"], used_hit_ids)
        front_rel = None
        back_rel = None
        sample_id = None
        if row:
            sample_id = str(row[0]).strip()
            used_hit_ids.add(sample_id)
            details = fetch_ebay_item_details(client, sample_id)
            pics = details["pictures"]
            if pics:
                front_name = f"{dept['key']}_{sample_id}_front.webp"
                if download_and_optimize_webp(pics[0], os.path.join(SHOP_IMG_DIR, front_name), force=force_images):
                    front_rel = f"assets/images/shop/{front_name}"
                    referenced_files.add(front_name)
            if len(pics) > 1:
                back_name = f"{dept['key']}_{sample_id}_back.webp"
                if download_and_optimize_webp(pics[1], os.path.join(SHOP_IMG_DIR, back_name), force=force_images):
                    back_rel = f"assets/images/shop/{back_name}"
                    referenced_files.add(back_name)

        print(f"  [+] {dept['key']} (sample {sample_id}): front={'OK' if front_rel else 'NONE'}, back={'OK' if back_rel else 'NONE'}")
        cta_url = dept.get("ctaUrlLiteral") or epn_store_search_url(dept["searchQuery"], dept["customId"])
        products.append(
            {
                "category": "ebay-depts",
                "badge": dept["badge"],
                "statusBadge": dept["statusBadge"],
                "title": dept["title"],
                "subtitle": dept["subtitle"],
                "price": dept["price"],
                "specs": dept["specs"],
                "icon": dept["icon"],
                "image": front_rel,
                "backImage": back_rel,
                "imageFit": "contain",
                "imageAlt": f"{dept['title']} - live store card scan",
                "imageBg": dept["imageBg"],
                "ctaText": dept["ctaText"],
                "ctaUrl": cta_url,
                "external": True,
            }
        )

    products.extend(ARDMORE_BOOTH_ITEMS)
    products.extend(SUPPLIES_ITEMS)
    con.close()

    # Prune orphaned files in assets/images/shop/
    if os.path.isdir(SHOP_IMG_DIR):
        for fname in os.listdir(SHOP_IMG_DIR):
            if fname not in referenced_files:
                try:
                    os.remove(os.path.join(SHOP_IMG_DIR, fname))
                    print(f"  [-] Removed orphaned image: {fname}")
                except OSError as exc:
                    print(f"  [!] Could not remove {fname}: {exc}")

    # Inject updated PRODUCTS JSON between markers in shop.html
    with open(SHOP_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    marker_pattern = re.compile(
        r"(// SHOP_PRODUCTS_START\r?\n).*?(// SHOP_PRODUCTS_END)",
        re.DOTALL,
    )
    if not marker_pattern.search(html):
        raise RuntimeError("Missing // SHOP_PRODUCTS_START / // SHOP_PRODUCTS_END markers in shop.html")

    products_json = json.dumps(products, indent=6, ensure_ascii=False)
    replacement = f"\\1    const PRODUCTS = {products_json};\n    \\2"
    new_html = marker_pattern.sub(lambda m: f"{m.group(1)}    const PRODUCTS = {products_json};\n    {m.group(2)}", html, count=1)

    changed = new_html != html
    if changed:
        with open(SHOP_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("[*] Updated shop.html with live eBay images & prices.")
    else:
        print("[*] shop.html already up to date.")

    if deploy:
        subprocess.run(["git", "add", "shop.html", "assets/images/shop"], cwd=BASE_DIR, check=False)
        status = subprocess.run(["git", "status", "--porcelain", "shop.html", "assets/images/shop"], cwd=BASE_DIR, capture_output=True, text=True)
        if status.stdout.strip():
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            subprocess.run(["git", "commit", "-m", f"Sync shop.html eBay card scans [{stamp}]"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
            print("[*] Pushed updated shop.html and card scans to origin/main.")

    return changed


if __name__ == "__main__":
    force = "--force" in sys.argv
    do_deploy = "--no-deploy" not in sys.argv
    sync_shop_showcase(force_images=force, deploy=do_deploy)
