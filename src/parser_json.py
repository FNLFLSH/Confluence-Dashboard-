import json
import re
from datetime import datetime

def load_and_parse_json(filepath):
    """Load JSON file and return list of dicts."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def clean_html(raw_html):
    """Remove HTML tags, entities, and extra whitespace from a string."""
    if not isinstance(raw_html, str):
        return ""
    clean = re.sub(r'<.*?>', '', raw_html)
    clean = re.sub(r'&[a-zA-Z0-9#]+;', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def parse_confluence_html_simple(html_content):
    """
    Parse Confluence HTML to extract release items from tables under h3 headers.
    """
    releases = []
    # Split the content by h3 tags to process each section individually
    content_blocks = re.split(r'(<h3[^>]*>.*?</h3>)', html_content)

    for i in range(1, len(content_blocks), 2):
        h3_tag = content_blocks[i]
        following_content = content_blocks[i + 1]

        # Extract overall date and title from the h3 header
        date_match = re.search(r'<time datetime="([^"]+)"', h3_tag)
        h3_title_match = re.search(r'\|\s*([^<]+)</h3>', h3_tag)
        
        h3_title = clean_html(h3_title_match.group(1)) if h3_title_match else ""
        h3_date = date_match.group(1) if date_match else ""

        # Intelligently infer the category from the h3 title
        category = "Other"
        if 'enhancement' in h3_title.lower() or 'updated' in h3_title.lower(): category = 'Enhancement'
        if 'new' in h3_title.lower() or 'created' in h3_title.lower(): category = 'New Feature'
        if 'bug' in h3_title.lower() or 'fix' in h3_title.lower(): category = 'Bug Fix'

        # Find and parse the table within this section
        table_match = re.search(r'<table[^>]*>(.*?)</table>', following_content, re.DOTALL)
        if not table_match:
            # If no table, use the h3 title as a single release item
            if h3_title:
                releases.append({
                    "Title": h3_title,
                    "Body": "No details provided in a table format.",
                    "Category": category,
                    "Date": h3_date
                })
            continue
        
        table_html = table_match.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
        
        has_items = False
        for row_html in rows:
            if '<th' in row_html.lower():  # Skip header rows
                continue

            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            
            # User confirmed: 1=Title, 2=Details, 3=Jira/ID, 4=Date
            if len(cells) >= 4:
                report_title = clean_html(cells[0])
                details = clean_html(cells[1])
                # Column 3 is an ID, we can ignore it for this report
                item_date = clean_html(cells[3])
                
                # Use the date from the table if valid, otherwise fall back to the h3 date
                try:
                    datetime.strptime(item_date.split('T')[0], '%Y-%m-%d')
                    final_date = item_date
                except (ValueError, TypeError):
                    final_date = h3_date

                if report_title or details:
                    releases.append({
                        "Title": report_title,
                        "Body": details,
                        "Category": category,  # Use the category inferred from the h3 title
                        "Date": final_date
                    })
                    has_items = True

        # If the table was empty but there was an h3 title, log the h3 as a release
        if not has_items and h3_title:
             releases.append({
                "Title": h3_title,
                "Body": "No items found in the table for this release.",
                "Category": category,
                "Date": h3_date,
            })
            
    return releases

def categorize_release(release_type):
    """Categorize release based on type."""
    release_type_lower = release_type.lower()
    
    if any(word in release_type_lower for word in ['bug', 'fix', 'fixed']):
        return "Bug Fix"
    elif any(word in release_type_lower for word in ['new', 'created']):
        return "New Feature"
    elif any(word in release_type_lower for word in ['updated', 'enhanced', 'enhancement']):
        return "Enhancement"
    else:
        return "Other"

def load_and_parse_confluence_data(filepath):
    """
    Load and parse Confluence data file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        data = json.loads(content)
        if 'body' in data and 'storage' in data['body']:
            html_content = data['body']['storage']['value']
            return parse_confluence_html_simple(html_content)
        elif isinstance(data, list):
            return data
    except (json.JSONDecodeError, KeyError):
        return parse_confluence_html_simple(content)
    
    return parse_confluence_html_simple(content) 