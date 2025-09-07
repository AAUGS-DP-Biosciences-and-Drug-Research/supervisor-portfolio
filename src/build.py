import os
import yaml
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

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

    """Detect a face and center it in a square crop in-place.

    If face-detection libraries are unavailable or no face is found,
    the image is left untouched.
    """
    if cv2 is None or Image is None:
        return

    img = cv2.imread(image_path)
    if img is None:
        return
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return

    # Pick the largest detected face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    cx, cy = x + w // 2, y + h // 2
    side = int(max(w, h) * 1.5)

    img_pil = Image.open(image_path)
    width, height = img_pil.size

    left = max(cx - side // 2, 0)
    top = max(cy - side // 2, 0)
    right = min(left + side, width)
    bottom = min(top + side, height)

    # Adjust if we hit borders to keep square
    if right - left != side:
        left = max(width - side, 0)
        right = width
    if bottom - top != side:
        top = max(height - side, 0)
        bottom = height

    cropped = img_pil.crop((left, top, right, bottom))
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
