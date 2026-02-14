import os
import re
import yaml
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# ---------- Config ----------
SUPERVISOR_YAML_DIR = "data/supervisors"
LEGACY_YAML_INPUT = "data/supervisors.yaml"
PUBLIC_FOLDER = "public"
IMAGES_FOLDER = os.path.join(PUBLIC_FOLDER, "images")
SOURCE_IMAGES = "static/images"
SITE_BASE_PATH = "/supervisor-portfolio"
DEFAULT_LOGO_FILENAME = "AboAkademiUniversity.png"
DEFAULT_LOGO = f"{SITE_BASE_PATH}/images/{DEFAULT_LOGO_FILENAME}"
DEFAULT_LOGO_PDF = os.path.abspath(os.path.join(IMAGES_FOLDER, DEFAULT_LOGO_FILENAME))


def linkify_bracket_urls(text):
    if text is None:
        return ""

    text = str(text)
    return re.sub(
        r"\[(https?://[^\]\s]+)\]",
        lambda match: f'<a href="{match.group(1)}" target="_blank" rel="noopener">{match.group(1)}</a>',
        text,
    )


def normalize_url(url):
    if not url:
        return ""

    url = str(url).strip()
    if not url:
        return ""

    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        return url

    return f"https://{url}"


def normalize_web_pages(supervisor):
    web_pages = supervisor.get("web_pages")
    if not web_pages:
        return []

    if not isinstance(web_pages, list):
        web_pages = [web_pages]

    normalized = []
    for item in web_pages:
        if isinstance(item, dict):
            label = str(item.get("label") or item.get("name") or "Web Page").strip()
            url = normalize_url(item.get("url") or item.get("link"))
        else:
            label = "Web Page"
            url = normalize_url(item)

        if url:
            normalized.append({"label": label, "url": url})

    return normalized

# ---------- Load templates ----------
env = Environment(loader=FileSystemLoader("src/templates"))
env.filters["linkify_bracket_urls"] = linkify_bracket_urls
page_template = env.get_template("supervisor.html")
index_template = env.get_template("index.html")
pdf_template = env.get_template("pdf.html")


# ---------- Load YAML ----------
def load_supervisors():
    supervisors = []

    if os.path.isdir(SUPERVISOR_YAML_DIR):
        yaml_files = sorted(
            [
                os.path.join(SUPERVISOR_YAML_DIR, file_name)
                for file_name in os.listdir(SUPERVISOR_YAML_DIR)
                if file_name.endswith((".yml", ".yaml"))
            ]
        )

        for yaml_file in yaml_files:
            with open(yaml_file, "r", encoding="utf-8") as f:
                entry = yaml.safe_load(f)
                if isinstance(entry, dict):
                    supervisors.append(entry)
                elif isinstance(entry, list):
                    supervisors.extend(entry)

        if supervisors:
            return supervisors

    if os.path.isfile(LEGACY_YAML_INPUT):
        with open(LEGACY_YAML_INPUT, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    raise FileNotFoundError(
        f"No supervisor YAML files found in '{SUPERVISOR_YAML_DIR}' or '{LEGACY_YAML_INPUT}'."
    )


supervisors = load_supervisors()

# ---------- Match images by slug ----------
for supervisor in supervisors:
    supervisor["lab_website"] = normalize_url(supervisor.get("lab_website", ""))
    supervisor["cris_profile"] = normalize_url(supervisor.get("cris_profile", ""))
    supervisor["web_pages"] = normalize_web_pages(supervisor)

    slug = supervisor["slug"]

    # Try to find an image with any common extension
    found = False
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        candidate = slug + ext
        full_path = os.path.join(IMAGES_FOLDER, candidate)
        if os.path.isfile(full_path):
            supervisor["photo_url"] = f"{SITE_BASE_PATH}/images/{candidate}"
            supervisor["photo_pdf_path"] = os.path.abspath(full_path)
            found = True
            break

    if not found:
        supervisor["photo_url"] = DEFAULT_LOGO
        supervisor["photo_pdf_path"] = DEFAULT_LOGO_PDF
        print(f"⚠️ Missing image for {supervisor['name']} → using logo.")

print(f"✅ Loaded {len(supervisors)} supervisors.")

# Ensure deterministic ordering: first by unit, then by name
supervisors.sort(key=lambda s: (s.get("unit", ""), s["name"]))

# ---------- Generate supervisor pages ----------
os.makedirs(os.path.join(PUBLIC_FOLDER, "supervisors"), exist_ok=True)

for supervisor in supervisors:
    html = page_template.render(supervisor=supervisor)
    out_path = os.path.join(PUBLIC_FOLDER, "supervisors", f"{supervisor['slug']}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Page for {supervisor['name']}")

# ---------- Generate index ----------
with open(os.path.join(PUBLIC_FOLDER, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_template.render(supervisors=supervisors))
print("✅ Created index.html")

# ---------- Generate Supervisor_Portfolio.html ----------
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
