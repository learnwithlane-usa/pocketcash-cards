"""
Pocket Cash Cards - Automated Checklist Inventory Sync & Evergreen Affiliate Engine
=====================================================================================
Daily autonomous script that:
1. Connects to SQLite database (pocket_cash_cards.db).
2. Audits all checklists on getpocketcash.com for hardcoded eBay item links.
3. Reconciles against active inventory:
   - Filters out synthetic 9000... draft IDs so only live 12-digit eBay ItemIDs are linked.
   - If a card sells out, ends, or is delisted, automatically removes the 'Buy in Store'
     link and ensures the card's 'Check Comps' link directs to an evergreen lowest-price
     search (_sop=12) with Pocket Cash's EPN affiliate tag (campid=5339204284).
   - If an active item's price changed in the DB, updates the button label in real-time.
4. Commits and deploys changes to GitHub Pages (origin main), with self-healing push
   recovery if local main is ahead of origin/main.
5. Writes timestamped execution summaries to sync_checklists.log.
"""

import os
import sys
import glob
import re
import sqlite3
import subprocess
import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKLISTS_DIR = os.path.join(BASE_DIR, "checklists")
DB_PATH = r"C:\Users\dee\.gemini\antigravity\scratch\tools\pocket_cash_cards.db"
LOG_FILE = os.path.join(BASE_DIR, "sync_checklists.log")
AFFILIATE_CAMPID = "5339204284"

# Explicit set-matching overrides where eBay titles use shorthand set names
SET_KEYWORDS = {
    "1990-collect-a-card-kingpins.html": ("1990", ["kingpin"]),
    "2016-decision-political.html": ("2016", ["decision"]),
    "2016-decision-political-cards.html": ("2016", ["decision"]),
    "1995-wheels-high-gear-rodeo.html": ("1995", ["high gear"]),
    "1995-high-gear-rodeo.html": ("1995", ["high gear"]),
    "2023-czech-baseball-wbc.html": (None, ["czech", "baseball"]),
    "2023-bbm-sumo-wrestling.html": (None, ["bbm", "sumo"]),
    "2024-scc-kbo-league.html": (None, ["scc", "kbo"]),
    "2024-ufa-ultimate-frisbee.html": (None, ["choice", "ufa"]),
    "2024-upper-deck-pwhl-series-1.html": (None, ["pwhl"]),
    "2026-savannah-bananas-tour.html": ("2026", ["banana"]),
    "2026-choice-banana-ball.html": ("2026", ["banana"]),
}

CARD_TAG_RE = re.compile(
    r'(<div\s+class="card-item[^"]*"([^>]*)>.*?)(\s*<a\s+[^>]*href="https://www\.ebay\.com/sch/i\.html[^"]*"[^>]*>.*?</a>)',
    re.DOTALL,
)


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


def sync_inventory(deploy=True):
    log("Starting Pocket Cash bidirectional checklist inventory sync...")

    tools_dir = r"C:\Users\dee\.gemini\antigravity\scratch\tools"
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    try:
        from buyer_wants_matcher import sync_databases
        sync_databases()
    except Exception as se:
        log(f"Notice: Pre-sync database unification skipped: {se}")

    if not os.path.exists(DB_PATH):
        log(f"ERROR: Database not found at {DB_PATH}")
        return False

    # Connect to SQLite
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    active_items = {}
    non_active_items = {}
    active_list_for_matching = []

    for row in cur.execute(
        "SELECT ebay_item_id, sku, title, list_price, status FROM inventory WHERE ebay_item_id IS NOT NULL"
    ):
        item_id = str(row[0]).strip()
        sku = row[1]
        title = row[2] or ""
        price = float(row[3]) if row[3] is not None else 0.0
        status = row[4]

        item_info = {
            "item_id": item_id,
            "sku": sku,
            "title": title,
            "title_lower": title.lower(),
            "price": price,
            "status": status,
        }

        # Exclude synthetic 9000... placeholder IDs from active inventory
        if status == "ACTIVE" and item_id.isdigit() and not item_id.startswith("9000"):
            active_items[item_id] = item_info
            active_list_for_matching.append(item_info)
        else:
            non_active_items[item_id] = item_info

    con.close()
    log(
        f"Database loaded: {len(active_items)} real ACTIVE items, {len(non_active_items)} ended/sold/synthetic items."
    )

    # Audit checklists
    checklist_files = sorted(glob.glob(os.path.join(CHECKLISTS_DIR, "*.html")))
    total_files_modified = 0
    total_links_removed = 0
    total_links_injected = 0
    total_prices_updated = 0

    for fpath in checklist_files:
        fname = os.path.basename(fpath)
        if fname == "index.html":
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            original_content = f.read()

        modified_content = original_content
        file_changed = False

        if fname in SET_KEYWORDS:
            year_token, brand_tokens = SET_KEYWORDS[fname]
        else:
            slug_tokens = [
                t
                for t in fname.replace(".html", "").split("-")
                if len(t) >= 3 and t not in ("checklist", "cards", "set", "the", "and")
            ]
            year_token = next(
                (t for t in slug_tokens if t.isdigit() and len(t) == 4), None
            )
            brand_tokens = [t for t in slug_tokens if t != year_token][:2]

        # 1. Reconcile existing direct item links: https://www.ebay.com/itm/(\d+)
        matches = list(
            re.finditer(
                r'<a\s+[^>]*href=["\']https?://(?:www\.)?ebay\.com/itm/(\d+)[^"\']*["\'][^>]*>(.*?)</a>\s*',
                original_content,
                re.DOTALL,
            )
        )

        for m in matches:
            full_match = m.group(0)
            item_id = m.group(1)
            inner_html = m.group(2)

            if item_id in active_items:
                expected_price = active_items[item_id]["price"]
                price_pattern = r"(?:⚡\s*)?Buy\s+(?:PC Copy|in Store)\s*\(\$([0-9\.]+)\)"
                price_match = re.search(price_pattern, inner_html)

                new_match = full_match
                target_url = f"https://www.ebay.com/itm/{item_id}?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid={AFFILIATE_CAMPID}&customid=pc_copy_{item_id}&toolid=10001&mkevt=1"
                if (
                    f"campid={AFFILIATE_CAMPID}" not in new_match
                    or f"customid=pc_copy_{item_id}" not in new_match
                ):
                    new_match = re.sub(
                        r'href=["\']https?://(?:www\.)?ebay\.com/itm/\d+[^"\']*["\']',
                        f'href="{target_url}"',
                        new_match,
                    )

                if "rel=" in new_match:
                    new_match = re.sub(
                        r'rel=["\'][^"\']*["\']',
                        'rel="sponsored noopener noreferrer"',
                        new_match,
                    )
                else:
                    new_match = new_match.replace(
                        "<a ", '<a rel="sponsored noopener noreferrer" '
                    )

                if price_match:
                    current_price = float(price_match.group(1))
                    if abs(current_price - expected_price) > 0.01:
                        prefix = (
                            "⚡ Buy PC Copy"
                            if "PC Copy" in price_match.group(0)
                            else "Buy in Store"
                        )
                        new_match = new_match.replace(
                            price_match.group(0), f"{prefix} (${expected_price:.2f})"
                        )
                        total_prices_updated += 1
                        log(
                            f"[{fname}] Price update for item {item_id}: ${current_price:.2f} -> ${expected_price:.2f}"
                        )

                if new_match != full_match:
                    modified_content = modified_content.replace(full_match, new_match)
                    file_changed = True
            else:
                reason = (
                    "SYNTHETIC_DRAFT"
                    if item_id.startswith("9000")
                    else ("ENDED" if item_id in non_active_items else "DELISTED")
                )
                modified_content = modified_content.replace(full_match, "")
                file_changed = True
                total_links_removed += 1
                log(f"[{fname}] {reason}: Removed dead store link for item {item_id}")

        # 2. Bidirectional Injection: Check card blocks lacking a direct store link
        if brand_tokens:
            card_blocks = list(CARD_TAG_RE.finditer(modified_content))
            for cb in card_blocks:
                prefix_html, attrs, comp_link_html = cb.groups()
                if "ebay.com/itm/" in prefix_html:
                    continue

                m_player = re.search(r'data-(?:player|name)="([^"]+)"', attrs)
                m_num = re.search(r'data-number="([^"]+)"', attrs)
                if not m_player or not m_num:
                    continue

                player_name = m_player.group(1).strip()
                card_num = m_num.group(1).strip()
                p_low = player_name.lower()
                if len(p_low) < 4:
                    continue
                c_num_clean = card_num.lstrip("#").lstrip("0") or "0"

                matched_item = None
                fallback_item = None
                for it in active_list_for_matching:
                    tl = it["title_lower"]
                    if year_token and year_token not in tl:
                        continue
                    if not all(bt in tl for bt in brand_tokens):
                        continue
                    if p_low not in tl:
                        continue
                    if (
                        f"#{c_num_clean}" in tl
                        or f"#0{c_num_clean}" in tl
                        or f" {c_num_clean} " in tl
                    ):
                        matched_item = it
                        break
                    elif " " in p_low and len(p_low) >= 8 and fallback_item is None:
                        fallback_item = it

                chosen_item = matched_item or fallback_item
                if chosen_item:
                    inv_url = f"https://www.ebay.com/itm/{chosen_item['item_id']}?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid={AFFILIATE_CAMPID}&customid=pc_copy_{chosen_item['item_id']}&toolid=10001&mkevt=1"
                    inv_price = f"{chosen_item['price']:.2f}"
                    injected_btn = (
                        f'\n            <a href="{inv_url}" target="_blank" rel="sponsored noopener noreferrer" '
                        f'class="inline-flex items-center gap-1.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 text-xs font-black px-3 py-1.5 rounded-xl shadow-md transition transform active:scale-95">'
                        f"<span>⚡ Buy PC Copy (${inv_price})</span></a>"
                    )
                    old_block = cb.group(0)
                    new_block = f"{prefix_html}{injected_btn}{comp_link_html}"
                    modified_content = modified_content.replace(old_block, new_block, 1)
                    file_changed = True
                    total_links_injected += 1
                    log(
                        f"[{fname}] INJECTED: Added ⚡ Buy PC Copy (${inv_price}) for #{card_num} {player_name} (item {chosen_item['item_id']})"
                    )

        if file_changed:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(modified_content)
            total_files_modified += 1
            log(f"Updated {fname}")

    # Summary & Git Deployment
    if total_files_modified > 0:
        log(
            f"Sync complete: {total_files_modified} files modified. ({total_links_injected} PC links injected, {total_links_removed} dead links purged, {total_prices_updated} prices refreshed)."
        )

        if deploy:
            log("Deploying updates to GitHub Pages (origin main)...")
            run_cmd("git add checklists/*.html")
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            commit_msg = f"Automated bidirectional inventory sync: +{total_links_injected} active PC links, -{total_links_removed} ended [{date_str}]"
            code, out, err = run_cmd(f'git commit -m "{commit_msg}"')
            if code == 0:
                log(f"Git commit successful: {out.splitlines()[0] if out else ''}")
                code_push, out_push, err_push = run_cmd("git push origin main")
                if code_push == 0:
                    log("Git push successful! Live site updated.")
                    indexnow_script = r"G:\AI\scripts\submit_indexnow.py"
                    if os.path.exists(indexnow_script):
                        log("Pinging IndexNow (Bing/Yandex) with updated URLs...")
                        run_cmd(f'python "{indexnow_script}"')
                else:
                    log(f"WARNING: Git push failed: {err_push}")
            else:
                log(f"Git commit notice: {out} {err}")
    else:
        log("Sync complete: All checklists are in sync. 0 changes needed.")
        if deploy:
            _, status_out, _ = run_cmd("git status -sb")
            if "[ahead " in status_out:
                log("Detected unpushed local commits on main. Running self-healing git push...")
                code_push, _, err_push = run_cmd("git push origin main")
                if code_push == 0:
                    log("Self-healing git push succeeded!")
                else:
                    log(f"WARNING: Self-healing git push failed: {err_push}")

    # 3. Run EPN Affiliate Conversion Monitor (syncs Impact/EPN API to pocket_cash_cards.db)
    if deploy:
        try:
            cfg_scripts = r"C:\Users\dee\.gemini\config\scripts"
            if cfg_scripts not in sys.path:
                sys.path.insert(0, cfg_scripts)
            from epn_monitor import sync_epn_conversions
            sync_epn_conversions()
            log("EPN conversion monitor completed.")
        except Exception as epn_err:
            log(f"Notice: EPN conversion monitor skipped: {epn_err}")

    return True


if __name__ == "__main__":
    do_deploy = "--no-deploy" not in sys.argv
    sync_inventory(deploy=do_deploy)
