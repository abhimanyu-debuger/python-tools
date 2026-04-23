import os
from urllib.parse import urljoin
from datetime import datetime, UTC

PROJECT_DIR = os.getcwd()
BASE_URL = "http://localhost/New_Simplex_Website/"

IGNORE_DIRS = {"vendor", ".git", "node_modules", "__pycache__"}

def is_valid_file(file):
    return file.endswith(".php")

def generate_url(file_path):
    relative_path = os.path.relpath(file_path, PROJECT_DIR)

    if relative_path.endswith("index.php"):
        relative_path = relative_path.replace("index.php", "")
    
    return urljoin(BASE_URL, relative_path.replace("\\", "/"))

def scan_directory():
    urls = []

    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if is_valid_file(file):
                full_path = os.path.join(root, file)
                urls.append(generate_url(full_path))

    return sorted(set(urls))


def create_sitemap_xml(urls):
    now = datetime.now(UTC).strftime("%Y-%m-%d")

    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in urls:
        xml_content.append("  <url>")
        xml_content.append(f"    <loc>{url}</loc>")
        xml_content.append(f"    <lastmod>{now}</lastmod>")
        xml_content.append("    <changefreq>weekly</changefreq>")
        xml_content.append("    <priority>0.8</priority>")
        xml_content.append("  </url>")

    xml_content.append("</urlset>")

    with open("sitemap.xml", "w") as f:
        f.write("\n".join(xml_content))


if __name__ == "__main__":
    print(f"📂 Scanning: {PROJECT_DIR}")

    urls = scan_directory()

    print(f"🔍 Found {len(urls)} PHP pages")

    create_sitemap_xml(urls)

    print("✅ sitemap.xml generated successfully!")
