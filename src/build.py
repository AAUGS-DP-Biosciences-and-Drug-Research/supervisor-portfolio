import os
import csv
import re
from jinja2 import Environment, FileSystemLoader

# ---------- Config ----------
INPUT_CSV = "data/responses.csv"
PUBLIC_FOLDER = "public"
IMAGES_FOLDER = os.path.join(PUBLIC_FOLDER, "images")
DEFAULT_LOGO = "https://www.abo.fi/wp-content/uploads/2019/09/AboAkademiUniversity.png"

# ---------- Helpers ----------
def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

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
        permission = row.get("I give the permission to post my picture online", "").strip().lower() == "yes"
        photo_url_raw = row.get("Upload a profile photo", "").strip()
        photo_filename = os.path.basename(photo_url_raw)
        photo_local_path = os.path.join(IMAGES_FOLDER, photo_filename)

        # If permission given and image file exists locally, use it
        if permission and os.path.isfile(photo_local_path):
            final_photo_url = f"./images/{photo_filename}"
        else:
            final_photo_url = f"./{DEFAULT_LOGO}"

        supervisor = {
            "name": name,
            "group": row.get("Research group name", "").strip(),
            "unit": row.get("Subject", "").strip(),
            "university": "Åbo Akademi University",
            "lab_website": row.get("Research group website", "").strip(),
            "cris_profile": row.get("Link to AboCRIS profile", "").strip(),
            "expertise": row.get("Areas of Expertise", "").strip(),
            "projects": row.get("Research projects", "").strip(),
            "techniques": row.get("Special methodologies & techniques", "").strip(),
            "funding": row.get("Major funding source(s) and international network(s)", "").strip(),
            "publications": row.get("Five selected publications", "").strip(),
            "keywords": row.get("Key words", "").strip(),
            "photo_url": final_photo_url,
            "photo_permission": permission,
            "slug": slug,
        }

        supervisors.append(supervisor)

print(f"✅ Loaded CSV with {len(supervisors)} rows.")

# ---------- Create output folders ----------
os.makedirs(os.path.join(PUBLIC_FOLDER, "supervisors"), exist_ok=True)

# ---------- Write individual supervisor pages ----------
for supervisor in supervisors:
    html = page_template.render(supervisor=supervisor)
    out_path = os.path.join(PUBLIC_FOLDER, "supervisors", f"{supervisor['slug']}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Created page for {supervisor['name']}")

# ---------- Write index.html ----------
with open(os.path.join(PUBLIC_FOLDER, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_template.render(supervisors=supervisors))
print("✅ Created index.html")

# ---------- Write PDF template base ----------
with open(os.path.join(PUBLIC_FOLDER, "Supervisor_Portfolio.html"), "w", encoding="utf-8") as f:
    f.write(pdf_template.render(supervisors=supervisors))
print("✅ Created Supervisor_Portfolio.html")
