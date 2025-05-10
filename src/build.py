import os
import yaml
import shutil
from jinja2 import Environment, FileSystemLoader

# ---------- Config ----------
YAML_INPUT = "data/supervisors.yaml"
PUBLIC_FOLDER = "public"
IMAGES_FOLDER = os.path.join(PUBLIC_FOLDER, "images")
SOURCE_IMAGES = "static/images"
SITE_BASE_PATH = "/supervisor-portfolio"
DEFAULT_LOGO = f"{SITE_BASE_PATH}/images/AboAkademiUniversity.png"

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

# ---------- Load supervisors.yaml ----------
with open(YAML_INPUT, "r", encoding="utf-8") as f:
    supervisors = yaml.safe_load(f)

for supervisor in supervisors:
    image_name = supervisor.get("photo", "")
    image_path = os.path.join(IMAGES_FOLDER, image_name)
    if os.path.isfile(image_path):
        supervisor["photo_url"] = f"{SITE_BASE_PATH}/images/{image_name}"
    else:
        supervisor["photo_url"] = DEFAULT_LOGO
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

# ---------- Write Supervisor_Portfolio.html for PDF ----------
with open(os.path.join(PUBLIC_FOLDER, "Supervisor_Portfolio.html"), "w", encoding="utf-8") as f:
    f.write(pdf_template.render(supervisors=supervisors))
print("✅ Created Supervisor_Portfolio.html")
