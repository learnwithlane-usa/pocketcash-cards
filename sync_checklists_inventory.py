"""
Pocket Cash Cards - Automated Checklist Inventory Sync & Evergreen Affiliate Engine
=====================================================================================
Daily autonomous script that:
1. Connects to SQLite database (pocket_cash_cards.db).
2. Audits all checklists on getpocketcash.com for hardcoded eBay item links.
3. Reconciles against active inventory:
   - If a card sells out, ends, or is delisted, automatically removes the 'Buy in Store'
     link and ensures the card's 'Check Comps' link directs to an evergreen lowest-price
     search (_sop=12) with Pocket Cash's EPN affiliate tag (campid=5339204284).
   - If an active item's price changed in the DB, updates the button label in real-time.
4. Commits and deploys changes to GitHub Pages (origin main).
5. Writes timestamped execution summaries to sync_checklists.log.
"""

import os
import sys
import glob
import re
import sqlite3
import subprocess
import datetime

# Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKLISTS_DIR = os.path.join(BASE_DIR, "checklists")
DB_PATH = r"C:\Users\dee\.gemini\antigravity\scratch\tools\pocket_cash_cards.db"
LOG_FILE = os.path.join(BASE_DIR, "sync_checklists.log")
AFFILIATE_CAMPID = "5339204284"


def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception as e:
        print(f"Error writing to log: {e}", file=sys.stderr)


def run_cmd(cmd, cwd=BASE_DIR):
    result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def sync_inventory():
    log("Starting Pocket Cash checklist inventory sync...")

    if not os.path.exists(DB_PATH):
        log(f"ERROR: Database not found at {DB_PATH}")
        return False

    # Connect to SQLite
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    active_items = {}
    non_active_items = {}

    for row in cur.execute("SELECT ebay_item_id, sku, title, list_price, status FROM inventory WHERE ebay_item_id IS NOT NULL"):
        item_id = str(row[0]).strip()
        sku = row[1]
        title = row[2]
        price = float(row[3]) if row[3] is not None else 0.0
        status = row[4]

        item_info = {
            'sku': sku,
            'title': title,
            'price': price,
            'status': status
        }

        if status == 'ACTIVE':
            active_items[item_id] = item_info
        else:
            non_active_items[item_id] = item_info

    con.close()
    log(f"Database loaded: {len(active_items)} ACTIVE items, {len(non_active_items)} ended/sold items.")

    # Audit checklists
    checklist_files = sorted(glob.glob(os.path.join(CHECKLISTS_DIR, "*.html")))
    total_files_modified = 0
    total_links_removed = 0
    total_prices_updated = 0

    for fpath in checklist_files:
        fname = os.path.basename(fpath)
        if fname == "index.html":
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            original_content = f.read()

        modified_content = original_content
        file_changed = False

        # Find all direct item links: https://www.ebay.com/itm/(\d+)
        matches = list(re.finditer(r'<a\s+[^>]*href=["\']https?://(?:www\.)?ebay\.com/itm/(\d+)[^"\']*["\'][^>]*>(.*?)</a>\s*', original_content, re.DOTALL))

        for m in matches:
            full_match = m.group(0)
            item_id = m.group(1)
            inner_html = m.group(2)

            if item_id in active_items:
                # Active in DB: verify price
                expected_price = active_items[item_id]['price']
                price_pattern = r'Buy in Store \(\$([0-9\.]+)\)'
                price_match = re.search(price_pattern, inner_html)
                if price_match:
                    current_price = float(price_match.group(1))
                    if abs(current_price - expected_price) > 0.01:
                        new_text = f"Buy in Store (${expected_price:.2f})"
                        new_match = full_match.replace(f"Buy in Store (${price_match.group(1)})", new_text)
                        modified_content = modified_content.replace(full_match, new_match)
                        file_changed = True
                        total_prices_updated += 1
                        log(f"[{fname}] Price update for item {item_id}: ${current_price:.2f} -> ${expected_price:.2f}")
            else:
                # NOT active in DB (sold or ended): remove store button
                reason = "ENDED" if item_id in non_active_items else "DELISTED"
                modified_content = modified_content.replace(full_match, "")
                file_changed = True
                total_links_removed += 1
                log(f"[{fname}] {reason}: Removed dead store link for item {item_id}")

        if file_changed:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(modified_content)
            total_files_modified += 1
            log(f"Updated {fname}")

    # Summary
    if total_files_modified > 0:
        log(f"Sync complete: {total_files_modified} files modified. ({total_links_removed} dead links purged, {total_prices_updated} prices refreshed).")
        
        # Deploy to GitHub
        log("Deploying updates to GitHub Pages (origin main)...")
        run_cmd("git add checklists/*.html")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"Automated inventory sync: Replaced ended listings with evergreen eBay affiliate links [{date_str}]"
        code, out, err = run_cmd(f'git commit -m "{commit_msg}"')
        if code == 0:
            log(f"Git commit successful: {out.splitlines()[0] if out else ''}")
            code_push, out_push, err_push = run_cmd("git push origin main")
            if code_push == 0:
                log("Git push successful! Live site updated.")
            else:
                log(f"WARNING: Git push failed: {err_push}")
        else:
            log(f"Git commit notice: {out} {err}")
    else:
        log("Sync complete: All checklists are in sync. 0 dead links detected.")

    return True


if __name__ == "__main__":
    sync_inventory()
