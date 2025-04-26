
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Create output folders
os.makedirs('public/supervisors', exist_ok=True)

# Load data
df = pd.read_csv('data/responses.csv')

# Prepare HTML environment
env = Environment(loader=FileSystemLoader('src/templates'))
template = env.get_template('supervisor.html')

supervisors = []

for index, row in df.iterrows():
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

    # Skip empty profiles
    if not supervisor['name']:
        continue

    supervisors.append(supervisor)

    # Create individual supervisor page
    filename = f"public/supervisors/{supervisor['name'].lower().replace(' ', '-')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template.render(supervisor=supervisor))

# Create main index.html
index_template = env.get_template('index.html')
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(index_template.render(supervisors=supervisors))

# Generate PDF
HTML('public/index.html').write_pdf('public/Supervisor_Portfolio.pdf')
