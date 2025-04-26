import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Create necessary output folders
os.makedirs('public/supervisors', exist_ok=True)

print("✅ Folders created.")

# Load the CSV
try:
    df = pd.read_csv('data/responses.csv', encoding='latin1')
    print(f"✅ Loaded CSV with {len(df)} rows.")
except Exception as e:
    print(f"❌ Failed to load CSV: {e}")
    exit(1)

# Clean up weird column names
df.columns = [col.strip().replace(' ', ' ').replace('\n', '').replace('\r', '') for col in df.columns]

# Prepare Jinja2 environment
env = Environment(loader=FileSystemLoader('src/templates'))
supervisor_template = env.get_template('supervisor.html')
index_template = env.get_template('index.html')

supervisors = []

for index, row in df.iterrows():
    supervisor = {
        'name': (row.get('Name') or '').strip(),
        'group': (row.get('Lab Name') or '').strip(),
        'unit': (row.get('Subject') or '').strip(),
        'university': "Åbo Akademi University",
        'expertise': (row.get('Areas of Expertise') or '').strip(),
        'projects': (row.get('Research projects') or '').strip(),
        'techniques': (row.get('Special methodologies & techniques') or '').strip(),
        'publications': (row.get('Five selected publications') or '').strip(),
        'lab_website': (row.get('Lab Website') or '').strip(),
        'email': (row.get('Email') or '').strip(),
        'photo_url': (row.get('Upload a profile photo') or '').strip()
    }

    if not supervisor['name']:
        continue

    supervisors.append(supervisor)

    filename = f"public/supervisors/{supervisor['name'].lower().replace(' ', '-')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(supervisor_template.render(supervisor=supervisor))

    print(f"✅ Created page for {supervisor['name']}")

# Create main index.html
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(index_template.render(supervisors=supervisors))

print("✅ Created index.html with all supervisors listed.")

# Create a temporary PDF HTML file first
with open('public/pdf_version.html', 'w', encoding='utf-8') as f:
    f.write(env.get_template('pdf.html').render(supervisors=supervisors))

# Then generate the PDF
HTML('public/pdf_version.html').write_pdf('public/Supervisor_Portfolio.pdf')
print("✅ Created Supervisor_Portfolio.pdf.")

print("🏁 Build complete!")
