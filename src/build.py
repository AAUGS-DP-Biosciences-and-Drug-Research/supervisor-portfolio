import os
import yaml
import shutil
import unicodedata
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# ---------- Config ----------
YAML_INPUT = "data/supervisors.yaml"
PUBLIC_FOLDER = "public"
IMAGES_FOLDER = os.path.join(PUBLIC_FOLDER, "images")
SOURCE_IMAGES = "static/images"
SITE_BASE_PATH = "/supervisor-portfolio"
DEFAULT_LOGO_FILENAME = "AboAkademiUniversity.png"
DEFAULT_LOGO = f"{SITE_BASE_PATH}/images/{DEFAULT_LOGO_FILENAME}"
DEFAULT_LOGO_PDF = os.path.abspath(os.path.join(IMAGES_FOLDER, DEFAULT_LOGO_FILENAME))

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

# ---------- Load YAML ----------
with open(YAML_INPUT, "r", encoding="utf-8") as f:
    supervisors = yaml.safe_load(f)

# ---------- Helpers ----------
def normalize_filename(name):
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    return name.lower().replace(" ", "").replace("%20", "").replace("_", "").strip()

# ---------- Build lookup for all source images ----------
source_images = {normalize_filename(f): f for f in os.listdir(SOURCE_IMAGES)}

# ---------- Match and rename images to slug ----------
for supervisor in supervisors:
    slug = supervisor["slug"]
    raw_photo_name = supervisor.get("photo", "")
    norm_key = normalize_filename(raw_photo_name)

    matched = source_images.get(norm_key)
    if matched:
        ext = os.path.splitext(matched)[-1]
        clean_filename = f"{slug}{ext}"
        src_path = os.path.join(SOURCE_IMAGES, matched)
        dst_path = os.path.join(IMAGES_FOLDER, clean_filename)
        shutil.copyfile(src_path, dst_path)

        supervisor["photo_url"] = f"{SITE_BASE_PATH}/images/{clean_filename}"
        supervisor["photo_pdf_path"] = os.path.abspath(dst_path)
    else:
        supervisor["photo_url"] = DEFAULT_LOGO
        supervisor["photo_pdf_path"] = DEFAULT_LOGO_PDF
        print(f"⚠️ Missing image for {supervisor['name']}, using logo.")

print(f"✅ Loaded {len(supervisors)} supervisors from YAML.")

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

# ---------- Write Supervisor_Portfolio.html ----------
pdf_html_path = os.path.join(PUBLIC_FOLDER, "Supervisor_Portfolio.html")
with open(pdf_html_path, "w", encoding="utf-8") as f:
    f.write(pdf_template.render(supervisors=supervisors))
print("✅ Created Supervisor_Portfolio.html")

# ---------- Generate PDF ----------
try:
    HTML(pdf_html_path).write_pdf(os.path.join(PUBLIC_FOLDER, "Supervisor_Portfolio.pdf"))
    print("✅ Created Supervisor_Portfolio.pdf")
except Exception as e:
    print(f"❌ Failed to create PDF: {e}")
