import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Create necessary output folders
os.makedirs('public/supervisors', exist_ok=True)

# Log for GitHub Actions
print("✅ Folders created.")

# Load the CSV
try:
    df = pd.read_csv('data/responses.csv')
    print(f"✅ Loaded CSV with {len(df)} rows.")
except Exception as e:
    print(f"❌ Failed to load CSV: {e}")
    exit(1)

# Prepare Jinja2 environment
env = Environment(loader=FileSystemLoader('src/templates'))
supervisor_template = env.get_template('supervisor.html')
index_template = env.get_template('index.html')

supervisors = []

for index, row in df.iterrows():
    # Read data safely
    supervisor = {
        'name': row.get('Name', '').strip(),
        'group': row.get('Group Name', '').strip(),
        'pi': row.get('PI name', '').strip(),
        'unit': row.get('Subject', '').strip(),
        'university': "Åbo Akademi University",
        'expertise': row.get('Areas of Expertise', '').strip(),
        'projects': row.get('Research projects', '').strip(),
        'techniques': row.get('Special methodologies & techniques', '').strip(),
        'publications': row.get('Five selected publications', '').strip(),
        'lab_website': row.get('Lab Website', '').strip(),
        'email': row.get('Email', '').strip(),
        'photo_url': row.get('Upload a profile photo', '').strip()
    }

    # Skip empty supervisors (missing name)
    if not supervisor['name']:
        continue

    supervisors.append(supervisor)

    # Create supervisor page
    filename = f"public/supervisors/{supervisor['name'].lower().replace(' ', '-')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(supervisor_template.render(supervisor=supervisor))

    print(f"✅ Created page for {supervisor['name']}")

# Create main index.html
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(index_template.render(supervisors=supervisors))

print("✅ Created index.html with all supervisors listed.")

# Generate the master PDF
try:
    HTML('public/index.html').write_pdf('public/Supervisor_Portfolio.pdf')
    print("✅ Created Supervisor_Portfolio.pdf.")
except Exception as e:
    print(f"❌ Failed to create PDF: {e}")

print("🏁 Build complete!")
