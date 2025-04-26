import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def safe_read(row, column_name):
    value = row.get(column_name, "")
    if pd.isna(value):
        return ""
    return str(value).strip()



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
        'name': safe_read(row, 'Name'),
        'group': safe_read(row, 'Lab Name'),
        'unit': safe_read(row, 'Subject'),
        'university': "Åbo Akademi University",
        'expertise': safe_read(row, 'Areas of Expertise'),
        'projects': safe_read(row, 'Research projects'),
        'techniques': safe_read(row, 'Special methodologies & techniques'),
        'publications': safe_read(row, 'Five selected publications'),
        'lab_website': safe_read(row, 'Lab Website'),
        'email': safe_read(row, 'Email'),
        'photo_url': safe_read(row, 'Upload a profile photo')
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
