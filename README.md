# 🧬 Supervisor Portfolio for the Doctoral Programme in Biosciences and Drug Research

Welcome to the Supervisor Portfolio repository!

This project collects supervisor profiles and automatically generates:
- 🌐 A public website showcasing each supervisor
- 📄 A downloadable master PDF portfolio
- 🖼️ An index page that displays supervisor photos in a responsive, topic‑grouped grid

The website and PDF are continuously updated and hosted via **GitHub Pages**.

👉 **Live Website:** 🔗 [Supervisor Portfolio](https://aaugs-dp-biosciences-and-drug-research.github.io/supervisor-portfolio/)

---

## 🚀 How It Works

| Step | Description |
|:----|:------------|
| 1 | Supervisors submit their details via Microsoft Forms |
| 2 | Responses are exported manually and converted to a structured YAML file: [`/data/supervisors/`](data/supervisors/) |
| 3 | Profile photos are saved manually in [`/public/images/`](public/images/) using the supervisor slug as filename (e.g. `guillaume-jacquemet.jpg`) |
| 4 | GitHub Actions automatically: |
|    | ➔ Builds individual HTML pages using Jinja templates |
|    | ➔ Compiles a full PDF portfolio |
|    | ➔ Publishes everything to GitHub Pages |

---

## 🧾 Notes

- **YAML Editing:** You can manually edit the individual YAML files in `data/supervisors/` for fine-grained control. Use the optional `photo_position: center` field to crop a thumbnail from the center instead of the default top.
- **Image Matching:** Images must match the `slug` of each supervisor (e.g. `guillaume-jacquemet.jpg`) and be placed in `public/images/`.

---

## 📊 Convert Excel Form Data to YAML

To generate supervisor YAML files from your Microsoft Form Excel export, use the following Colab notebook:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AAUGS-DP-Biosciences-and-Drug-Research/supervisor-portfolio/blob/main/Convert_Excel_Supervisor_Data_to_YAML.ipynb)

> This will generate clean, editable YAML files compatible with the portfolio builder.

---

## 📦 Dependencies

- Python 3.11+
- `jinja2`, `pyyaml`, `weasyprint`

These are automatically installed during the GitHub Actions run.

---

## 📬 Contributions

Pull requests and suggestions are welcome to improve automation, design, and data quality.
