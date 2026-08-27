import csv
import json
import re

# ==============================================================================
# ABDA 2026 E-Poster Portal Automated Generator
# This script reads a CSV file containing submitted poster details and converts
# them into the JavaScript data format required for index.html.
# ==============================================================================

CSV_FILE_PATH = "posters.csv"
HTML_FILE_PATH = "index.html"
OUTPUT_JSON_PATH = "posters.json"

def clean_text(text):
    """Sanitize string inputs to prevent JSON/HTML escaping issues."""
    if not text:
        return ""
    return text.strip().replace('"', '\\"').replace('\n', ' ')

def parse_csv_to_posters(csv_path):
    """
    Reads posters.csv and maps columns to the ABDA 2026 JSON schema.
    Expected CSV Column Headers:
    ID, Title, Category, Authors, Affiliations, Keywords, ImageUrl, Background, Methods, Conclusion
    """
    posters = []
    
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse keywords split by comma or semicolon
                raw_keywords = row.get('Keywords', '')
                keywords = [k.strip() for k in re.split(r'[,;]', raw_keywords) if k.strip()]
                if not keywords:
                    keywords = ["ABDA2026"]
                
                poster = {
                    "id": row.get('ID', '').strip(),
                    "title": row.get('Title', '').strip(),
                    "category": row.get('Category', 'Scientific Research').strip(),
                    "authors": row.get('Authors', '').strip(),
                    "affiliations": row.get('Affiliations', '').strip(),
                    "keywords": keywords,
                    "imageUrl": row.get('ImageUrl', '').strip(),
                    "background": row.get('Background', '').strip(),
                    "methods": row.get('Methods', '').strip(),
                    "conclusion": row.get('Conclusion', '').strip()
                }
                
                # Only append entries that have at least an ID
                if poster["id"]:
                    posters.append(poster)
                    
        print(f"✅ Successfully parsed {len(posters)} poster entries from '{csv_path}'.")
        return posters

    except FileNotFoundError:
        print(f"❌ Error: '{csv_path}' not found. Please place your CSV file in the same folder as this script.")
        return []

def update_index_html(html_path, posters):
    """
    Injects the parsed JSON array directly into index.html at RAW_SUBMITTED_POSTERS.
    """
    if not posters:
        print("⚠️ No poster data to write. Skipping update.")
        return

    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Format JSON with indent
        json_data_str = json.dumps(posters, indent=12)

        # Regex replace content of RAW_SUBMITTED_POSTERS = [ ... ];
        pattern = r"const RAW_SUBMITTED_POSTERS = \[[\s\S]*?\];"
        replacement = f"const RAW_SUBMITTED_POSTERS = {json_data_str};"

        updated_content = re.sub(pattern, replacement, content)

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"🎉 Successfully updated '{html_path}' with {len(posters)} submitted posters!")

    except FileNotFoundError:
        print(f"❌ Error: Could not find '{html_path}'.")

def export_json(json_path, posters):
    """Exports posters array as a standalone posters.json file."""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(posters, f, indent=2)
    print(f"📁 Exported standalone JSON file to '{json_path}'.")

if __name__ == "__main__":
    print("--- ABDA 2026 E-Poster Insertion Automation ---")
    poster_data = parse_csv_to_posters(CSV_FILE_PATH)
    if poster_data:
        # Update index.html directly
        update_index_html(HTML_FILE_PATH, poster_data)
        # Also create a standalone posters.json copy for backup
        export_json(OUTPUT_JSON_PATH, poster_data)


