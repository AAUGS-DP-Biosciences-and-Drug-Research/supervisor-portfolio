import os
import csv
import re
import shutil
import urllib.parse
from jinja2 import Environment, FileSystemLoader

# ---------- Config ----------
INPUT_CSV = "data/responses.csv"
PUBLIC_FOLDER = "public"
IMAGES_FOLDER = os.path.join(PUBLIC_FOLDER, "images")
SOURCE_IMAGES = "static/images"
SITE_BASE_PATH = "/supervisor-portfolio"
DEFAULT_LOGO = f"{SITE_BASE_PATH}/images/AboAkademiUniversity.png"

# ---------- Helpers ----------
def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

# ---------- Prepare image folder ----------
os.makedirs(IMAGES_FOLDER, exist_ok=True)

if os.path.isdir(SOURCE_IMAGES):
    for filename in os.listdir(SOURCE_IMAGES):
        src = os.path.join(SOURCE_IMAGES, filename)
        dst = os.path.join(IMAGES_FOLDER, filename)
        if os.path.isfile(src):
            shutil.copyfile(src, dst)
            print(f"✅ Copied image: {filename}")
else:
    print("⚠️ static/images folder not found.")

# ---------- Load templates ----------
env = Environment(loader=FileSystemLoader("src/templates"))
page_template = env.get_template("supervisor.html")
index_template = env.get_template("index.html")
pdf_template = env.get_template("pdf.html")

# ---------- Load and process CSV ----------
supervisors = []

with open(INPUT_CSV, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row.get("Name", "").strip()
        if not name:
            continue

        slug = slugify(name)

        # Get filename from CSV and encode it for safe URL use
        photo_url_raw = row.get("Upload a profile photo", "").strip()
        photo_filename = os.path.basename(photo_url_raw)
        photo_local_path = os.path.join(IMAGES_FOLDER, photo_filename)
        photo_url_encoded = urllib.parse.quote(photo_filename)

        # Check if image file exists
        if os.path.isfile(photo_local_path):
            final_photo_url = f"{SITE_BASE_PATH}/images/{photo_url_encoded}"
        else:
            final_photo_url = DEFAULT_LOGO
            print(f"⚠️ No photo found for {name}, using logo.")

        supervisor = {
            "name": name,
            "group": row.get("Research group name", "").strip(),
            "unit": row.get("Subject", "").strip(),
            "university": "Åbo Akademi University",
            "lab_website": row.get("Research group website", "").strip(),
            "cris_profile": row.get("Link to AboCRIS profile", "").strip() or row.get("Link to AboCRIS profile", "").strip(),
            "expertise": row.get("Areas of Expertise", "").strip(),
            "projects": row.get("Research projects", "").strip(),
            "techniques": row.get("Special methodologies & techniques", "").strip(),
            "funding": row.get("Major funding source(s) and international network(s)", "").strip(),
            "publications": row.get("Five selected publications", "").strip(),
            "keywords": row.get("Key words", "").strip(),
            "photo_url": final_photo_url,
            "slug": slug,
        }

        supervisors.append(supervisor)

print(f"\n✅ Loaded {len(supervisors)} supervisors.")

# ---------- Write supervisor pages ----------
os.makedirs(os.path.join(PUBLIC_FOLDER, "supervisors"), exist_ok=True)

for supervisor in supervisors:
    html = page_template.render(supervisor=supervisor)
    out_path = os.path.join(PUBLIC_FOLDER, "supervisors", f"{supervisor['slug']}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Page for {supervisor['name']}")

# ---------- Write index.html ----------
with open(os.path.join(PUBLIC_FOLDER, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_template.render(supervisors=supervisors))
print("✅ Created index.html")

# ---------- Write PDF template base ----------
with open(os.path.join(PUBLIC_FOLDER, "Supervisor_Portfolio.html"), "w", encoding="utf-8") as f:
    f.write(pdf_template.render(supervisors=supervisors))
print("✅ Created Supervisor_Portfolio.html")
