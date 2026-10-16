import os
import re

site_dir = r"C:\Users\dee\.gemini\antigravity\scratch\pocketcash-site"

for html_file in ["index.html", "ardmore.html"]:
    fpath = os.path.join(site_dir, html_file)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    srcs = re.findall(r'(?:src|srcset)=["\']([^"\']+)["\']', content)
    print(f"Checking {html_file}: {len(srcs)} media references...")
    missing = []
    for s in srcs:
        if s.startswith(("http://", "https://", "data:", "mailto:", "tel:")):
            continue
        local_s = s.split("?")[0].split("#")[0]
        full_p = os.path.normpath(os.path.join(site_dir, local_s))
        if not os.path.exists(full_p):
            missing.append(s)

    if missing:
        print(f"  MISSING in {html_file}: {missing}")
    else:
        print(f"  ALL {len(srcs)} LOCAL MEDIA ASSETS RESOLVE PERFECTLY in {html_file}!")
