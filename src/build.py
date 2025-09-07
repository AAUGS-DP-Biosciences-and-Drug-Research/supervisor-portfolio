import os
import yaml
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Optional dependencies for image smart centering
try:  # pragma: no cover - if unavailable we skip centering
    from PIL import Image, ImageFilter, ImageOps
    import numpy as np
except Exception:  # pragma: no cover - graceful degradation
    Image = ImageFilter = ImageOps = np = None

# ---------- Config ----------
YAML_INPUT = "data/supervisors.yaml"
PUBLIC_FOLDER = "public"
IMAGES_FOLDER = os.path.join(PUBLIC_FOLDER, "images")
SOURCE_IMAGES = "static/images"
SITE_BASE_PATH = "/supervisor-portfolio"
DEFAULT_LOGO_FILENAME = "AboAkademiUniversity.png"
DEFAULT_LOGO = f"{SITE_BASE_PATH}/images/{DEFAULT_LOGO_FILENAME}"
DEFAULT_LOGO_PDF = os.path.abspath(os.path.join(IMAGES_FOLDER, DEFAULT_LOGO_FILENAME))


def center_face(image_path: str) -> None:
    """Center the most "interesting" part of an image in a square crop.

    This uses a lightweight edge-based heuristic when Pillow and NumPy are
    available.  If the optional dependencies are missing or no edges are
    detected, the image is left unchanged.
    """
    if Image is None or np is None:
        return

    with Image.open(image_path) as img:
        size = min(img.size)
        gray = img.convert("L")
        edges = gray.filter(ImageFilter.FIND_EDGES)
        arr = np.array(edges)
        ys, xs = np.nonzero(arr)
        if len(xs) == 0:
            # No strong edges detected – keep as-is
            return
        cx = xs.mean() / arr.shape[1]
        cy = ys.mean() / arr.shape[0]
        cropped = ImageOps.fit(img, (size, size), centering=(cx, cy))
        cropped.save(image_path)

# ---------- Load templates ----------
env = Environment(loader=FileSystemLoader("src/templates"))
page_template = env.get_template("supervisor.html")
index_template = env.get_template("index.html")
pdf_template = env.get_template("pdf.html")

# ---------- Load YAML ----------
with open(YAML_INPUT, "r", encoding="utf-8") as f:
    supervisors = yaml.safe_load(f)

# ---------- Match images by slug ----------
for supervisor in supervisors:
    slug = supervisor["slug"]

    # Try to find an image with any common extension
    found = False
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        candidate = slug + ext
        full_path = os.path.join(IMAGES_FOLDER, candidate)
        if os.path.isfile(full_path):
            # Attempt to center the face in the image before using it
            center_face(full_path)
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
