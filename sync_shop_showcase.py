"""
Pocket Cash Cards - Top 10 Most Expensive Live eBay Showcase Sync
=================================================================
Zero-token script that:
1. Queries eBay's live Trading API (GetMyeBaySelling sorted by
   CurrentPriceDescending) for the 10 most expensive active listings in the
   Pocket Cash eBay store.
2. Fetches each listing's exact front & back high-resolution scans and
   condition/category metadata via GetItem.
3. Optimizes and caches front/back .webp scans in assets/images/shop/ and
   prunes any scans no longer in the current Top 10.
4. Updates the PRODUCTS array in shop.html between explicit marker comments.
"""

import io
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List

import requests
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHOP_HTML_PATH = os.path.join(BASE_DIR, "shop.html")
SHOP_IMG_DIR = os.path.join(BASE_DIR, "assets", "images", "shop")
EBAY_CLIENT_DIR = r"G:\AI\scratch\ebay_batch_auditor"

TOP_N = 10
MAX_IMAGE_DIM = 720
WEBP_QUALITY = 85

RANK_GRADIENTS = [
    "from-amber-950/70 to-slate-900",
    "from-emerald-950/70 to-slate-900",
    "from-cyan-950/70 to-slate-900",
    "from-rose-950/70 to-slate-900",
    "from-indigo-950/70 to-slate-900",
    "from-yellow-950/70 to-slate-900",
    "from-purple-950/70 to-slate-900",
    "from-teal-950/70 to-slate-900",
    "from-orange-950/70 to-slate-900",
    "from-blue-950/70 to-slate-900",
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


def fetch_top_priced_active_items(client, limit: int = 20) -> List[Dict[str, Any]]:
    """Query live eBay store sorted by CurrentPriceDescending."""
    xml_req = f"""<?xml version="1.0" encoding="utf-8"?>
<GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <ActiveList>
    <Include>true</Include>
    <Pagination>
      <EntriesPerPage>{limit}</EntriesPerPage>
      <PageNumber>1</PageNumber>
    </Pagination>
    <Sort>CurrentPriceDescending</Sort>
  </ActiveList>
</GetMyeBaySellingRequest>"""
    resp = client._request_with_retry(
        "POST",
        client.trading_endpoint,
        data=xml_req.encode("utf-8"),
        headers=client._get_trading_headers("GetMyeBaySelling"),
        timeout=30,
    )
    root = ET.fromstring(resp.content)
    ns = {"e": "urn:ebay:apis:eBLBaseComponents"}
    ack = root.findtext("e:Ack", "", ns)
    if ack not in ("Success", "Warning"):
        errs = [e.findtext("e:LongMessage", "", ns) for e in root.findall(".//e:Errors", ns)]
        raise RuntimeError(f"GetMyeBaySelling failed ({ack}): {'; '.join(errs)}")

    items = []
    for node in root.findall(".//e:ActiveList/e:ItemArray/e:Item", ns):
        iid = (node.findtext("e:ItemID", "", ns) or "").strip()
        title = (node.findtext("e:Title", "", ns) or "").strip()
        price_txt = node.findtext("e:SellingStatus/e:CurrentPrice", "", ns)
        qty = int(node.findtext("e:Quantity", "0", ns) or 0)
        sold = int(node.findtext("e:SellingStatus/e:QuantitySold", "0", ns) or 0)
        qty_avail_txt = node.findtext("e:QuantityAvailable", "", ns)
        qty_avail = int(qty_avail_txt) if qty_avail_txt != "" else max(0, qty - sold)
        if not iid or not price_txt or qty_avail <= 0:
            continue
        items.append({"item_id": iid, "title": title, "price": float(price_txt), "qty_available": qty_avail})

    items.sort(key=lambda x: x["price"], reverse=True)
    return items


def fetch_ebay_item_details(client, item_id: str) -> Dict[str, Any]:
    """Fetch live listing title, price, status, stock availability, and PictureURLs via Trading GetItem."""
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

    title = (root.findtext(".//e:Item/e:Title", "", ns) or "").strip()
    status = (root.findtext(".//e:Item/e:SellingStatus/e:ListingStatus", "", ns) or "").strip()
    qty = int(root.findtext(".//e:Item/e:Quantity", "0", ns) or 0)
    sold = int(root.findtext(".//e:Item/e:SellingStatus/e:QuantitySold", "0", ns) or 0)
    qty_available = max(0, qty - sold)
    hide_from_search = (root.findtext(".//e:Item/e:HideFromSearch", "", ns) or "").strip().lower() == "true"
    price_text = root.findtext(".//e:Item/e:SellingStatus/e:CurrentPrice", "", ns)
    price = float(price_text) if price_text else 0.0
    condition = (root.findtext(".//e:Item/e:ConditionDisplayName", "", ns) or "").strip()
    pics = [
        p.text.strip()
        for p in root.findall(".//e:Item/e:PictureDetails/e:PictureURL", ns)
        if p.text and p.text.strip()
    ]
    return {
        "item_id": item_id,
        "title": title,
        "status": status,
        "qty_available": qty_available,
        "hide_from_search": hide_from_search,
        "price": price,
        "condition": condition,
        "pictures": pics,
    }


def upgrade_ebay_img_url(url: str) -> str:
    """Prefer higher-res 1600px EPS image when eBay returns $_1.JPG thumbnail size."""
    return re.sub(r"/\$_1\.(JPG|PNG|WEBP)", r"/$_57.\1", url, flags=re.IGNORECASE)


def download_and_optimize_webp(url: str, dest_path: str, force: bool = False) -> bool:
    """Download an image URL and save as a crisp .webp thumbnail."""
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


def clean_display_title(raw_title: str) -> str:
    """Strip trailing Pocket Cash 6-digit inventory SKU suffix for cleaner storefront display."""
    return re.sub(r"\s+\d{6}$", "", raw_title).strip()


def derive_card_metadata(title: str, price: float, condition: str, has_back: bool) -> Dict[str, Any]:
    """Build badge, subtitle, icon, and collector specs from live eBay listing metadata."""
    tl = title.lower()

    if "1/1" in tl or "one of one" in tl:
        badge = "1/1 Masterpiece"
        icon = "👑"
    elif "auto" in tl and "relic" in tl:
        badge = "Auto Relic Hit"
        icon = "🏆"
    elif "auto" in tl:
        badge = "Certified Auto"
        icon = "✍️"
    elif "bgs" in tl or "psa" in tl or "sgc" in tl or "arena club" in tl or "c3" in tl:
        badge = "Graded Slab"
        icon = "💎"
    elif re.search(r"/\d+", tl):
        badge = "Serial Numbered SSP"
        icon = "✨"
    elif "sp" in tl.split() or "short print" in tl or "rare" in tl:
        badge = "Short Print SSP"
        icon = "🔥"
    else:
        badge = "Vault Grail"
        icon = "⭐"

    serial_match = re.search(r"(\d+/\d+|/\d+)", title)
    grade_match = re.search(
        r"\b(BGS\s*[\d.]+(?:\s*Gem\s*Mint)?|PSA\s*[\d.]+|SGC\s*[\d.]+|Arena\s*Club\s*[\d.]+|C3(?:\s*Grading)?\s*[\d.]+)",
        title,
        re.IGNORECASE,
    )

    subtitle_parts = []
    if grade_match:
        subtitle_parts.append(grade_match.group(1).strip())
    elif condition:
        subtitle_parts.append(condition)
    if serial_match:
        subtitle_parts.append(f"Serial {serial_match.group(1)}")
    subtitle_parts.append("Pocket Cash eBay Vault")
    subtitle = " • ".join(subtitle_parts)

    if price >= 100:
        ship_spec = "Ships in padded mailer inside a box (USPS Ground Advantage)"
    elif price >= 20:
        ship_spec = "Ships in double-padded mailer (USPS Ground Advantage)"
    else:
        ship_spec = "Ships via $1 Tracked Standard Envelope"

    specs = [
        "Actual card scanned front & back" if has_back else "Actual card photo from listing",
        ship_spec,
        "100% authentic • Top-Rated eBay Seller",
    ]
    return {"badge": badge, "subtitle": subtitle, "icon": icon, "specs": specs}


def epn_item_url(item_id: str) -> str:
    return (
        f"https://www.ebay.com/itm/{item_id}"
        f"?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339204284"
        f"&customid=shop_top10_{item_id}&toolid=10001&mkevt=1"
    )


def sync_shop_showcase(force_images: bool = False, deploy: bool = True) -> bool:
    if not os.path.exists(SHOP_HTML_PATH):
        raise FileNotFoundError(f"shop.html not found: {SHOP_HTML_PATH}")

    client = get_ebay_client()
    candidates = fetch_top_priced_active_items(client, limit=40)
    print(f"[*] Fetched {len(candidates)} in-stock top-priced active candidates from eBay.")

    referenced_files = set()
    products: List[Dict[str, Any]] = []

    for cand in candidates:
        if len(products) >= TOP_N:
            break
        item_id = cand["item_id"]
        details = fetch_ebay_item_details(client, item_id)
        if (
            details["status"] != "Active"
            or details["qty_available"] <= 0
            or details["hide_from_search"]
            or not details["pictures"]
        ):
            print(f"  [!] Skipping unavailable/sold item {item_id} (status={details['status']}, avail={details['qty_available']}, hidden={details['hide_from_search']})")
            continue

        rank = len(products) + 1
        title = clean_display_title(details["title"] or cand["title"])
        price_val = details["price"] or cand["price"]
        price_str = f"${price_val:,.2f}"
        pics = details["pictures"]

        front_rel = None
        back_rel = None
        front_name = f"{item_id}_front.webp"
        if download_and_optimize_webp(pics[0], os.path.join(SHOP_IMG_DIR, front_name), force=force_images):
            front_rel = f"assets/images/shop/{front_name}"
            referenced_files.add(front_name)

        if len(pics) > 1:
            back_name = f"{item_id}_back.webp"
            if download_and_optimize_webp(pics[1], os.path.join(SHOP_IMG_DIR, back_name), force=force_images):
                back_rel = f"assets/images/shop/{back_name}"
                referenced_files.add(back_name)

        if not front_rel:
            continue

        meta = derive_card_metadata(title, price_val, details["condition"], bool(back_rel))
        print(f"  [#{rank:02d}] {item_id} | {price_str} | back={'OK' if back_rel else 'NONE'} | {title[:55]}")

        products.append(
            {
                "rank": rank,
                "ebayItemId": item_id,
                "badge": meta["badge"],
                "statusBadge": f"#{rank} Top Card",
                "title": title,
                "subtitle": meta["subtitle"],
                "price": price_str,
                "specs": meta["specs"],
                "icon": meta["icon"],
                "image": front_rel,
                "backImage": back_rel,
                "imageAlt": f"{title} - actual eBay card scan",
                "imageBg": RANK_GRADIENTS[(rank - 1) % len(RANK_GRADIENTS)],
                "ctaText": f"⚡ Buy on eBay ({price_str}) ↗",
                "ctaUrl": epn_item_url(item_id),
            }
        )

    if len(products) < TOP_N:
        raise RuntimeError(f"Expected {TOP_N} top listings with images, got {len(products)}")

    # Prune any cached images no longer in the Top 10
    if os.path.isdir(SHOP_IMG_DIR):
        for fname in os.listdir(SHOP_IMG_DIR):
            if fname not in referenced_files:
                try:
                    os.remove(os.path.join(SHOP_IMG_DIR, fname))
                    print(f"  [-] Removed outdated image: {fname}")
                except OSError as exc:
                    print(f"  [!] Could not remove {fname}: {exc}")

    with open(SHOP_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    marker_pattern = re.compile(
        r"(// SHOP_PRODUCTS_START\r?\n).*?(// SHOP_PRODUCTS_END)",
        re.DOTALL,
    )
    if not marker_pattern.search(html):
        raise RuntimeError("Missing // SHOP_PRODUCTS_START / // SHOP_PRODUCTS_END markers in shop.html")

    products_json = json.dumps(products, indent=6, ensure_ascii=False)
    new_html = marker_pattern.sub(
        lambda m: f"{m.group(1)}    const PRODUCTS = {products_json};\n    {m.group(2)}",
        html,
        count=1,
    )

    changed = new_html != html
    if changed:
        with open(SHOP_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("[*] Updated shop.html with Top 10 most expensive eBay cards.")
    else:
        print("[*] shop.html already up to date with Top 10 eBay cards.")

    if deploy:
        subprocess.run(["git", "add", "shop.html", "assets/images/shop"], cwd=BASE_DIR, check=False)
        status = subprocess.run(
            ["git", "status", "--porcelain", "shop.html", "assets/images/shop"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        if status.stdout.strip():
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            subprocess.run(["git", "commit", "-m", f"Sync shop.html Top 10 eBay Vault cards [{stamp}]"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
            print("[*] Pushed updated shop.html and Top 10 scans to origin/main.")

    return changed


if __name__ == "__main__":
    force = "--force" in sys.argv
    do_deploy = "--no-deploy" not in sys.argv
    sync_shop_showcase(force_images=force, deploy=do_deploy)
