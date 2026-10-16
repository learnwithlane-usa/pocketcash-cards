import os

img_dir = r"C:\Users\dee\.gemini\antigravity\scratch\pocketcash-site\assets\images\ardmore"
preview_path = r"C:\Users\dee\.gemini\antigravity\scratch\pocketcash-site\ardmore-gallery-preview.html"

jpgs = [f for f in sorted(os.listdir(img_dir)) if f.endswith(".jpg")]

html_lines = [
    "<!DOCTYPE html>",
    "<html lang='en'>",
    "<head>",
    "<meta charset='UTF-8'>",
    "<title>Pocket Cash Cards — Ardmore Booth 64 Photo Review</title>",
    "<style>",
    "  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #090e17; color: #f1f5f9; padding: 30px; }",
    "  h1 { color: #7bbe81; margin-bottom: 8px; font-size: 24px; font-weight: 900; }",
    "  p { color: #94a3b8; font-size: 14px; margin-bottom: 24px; }",
    "  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }",
    "  .card { background: #0f1826; border: 1px solid #1f304b; border-radius: 12px; overflow: hidden; padding: 12px; }",
    "  img { width: 100%; height: 230px; object-fit: cover; border-radius: 8px; }",
    "  .filename { font-family: monospace; font-size: 11px; color: #eed9a5; margin-top: 10px; word-break: break-all; }",
    "  .badge { display: inline-block; background: rgba(123, 190, 129, 0.15); color: #7bbe81; border: 1px solid rgba(123, 190, 129, 0.3); font-size: 11px; font-weight: bold; padding: 3px 8px; border-radius: 4px; margin-top: 6px; }",
    "</style>",
    "</head>",
    "<body>",
    "<h1>Pocket Cash Cards — Ardmore Booth #64 Gallery Preview</h1>",
    "<p>Processed from raw photos in <code>E:\\Ardmore Photos.zip</code>. Converted to web-optimized JPG and WebP with Google SEO &amp; GEO filenames.</p>",
    "<div class='grid'>"
]

for j in jpgs:
    size_kb = round(os.path.getsize(os.path.join(img_dir, j)) / 1024, 1)
    html_lines.append(f"  <div class='card'>")
    html_lines.append(f"    <img src='assets/images/ardmore/{j}' alt='{j}'>")
    html_lines.append(f"    <div class='filename'>{j}</div>")
    html_lines.append(f"    <div class='badge'>JPG: {size_kb} KB • WebP Ready</div>")
    html_lines.append(f"  </div>")

html_lines.append("</div>")
html_lines.append("</body>")
html_lines.append("</html>")

with open(preview_path, "w", encoding="utf-8") as f:
    f.write("\n".join(html_lines))

print(f"Created gallery preview at {preview_path}")
