import json
import re
from datetime import datetime

def load_and_parse_json(filepath):
    """Load JSON file and return list of dicts."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def parse_confluence_html_simple(html_content):
    """
    Parse Confluence HTML content using regex patterns.
    Returns a list of dictionaries with release data.
    """
    releases = []
    
    # Pattern to find release dates and titles
    h3_pattern = r'<h3[^>]*class="auto-cursor-target"[^>]*>.*?<time datetime="([^"]+)"[^>]*>.*?\|\s*([^<]+)</h3>'
    
    # Find all h3 elements with release information
    h3_matches = re.findall(h3_pattern, html_content, re.DOTALL)
    
    for date_str, title in h3_matches:
        # Find the table content after this h3
        # Look for table rows with data
        table_pattern = r'<tr[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>'
        
        # Find the section between this h3 and the next h3
        section_start = html_content.find(f'<time datetime="{date_str}"')
        if section_start == -1:
            continue
            
        # Find the next h3 or end of content
        next_h3 = html_content.find('<h3', section_start + 1)
        if next_h3 == -1:
            section_end = len(html_content)
        else:
            section_end = next_h3
            
        section_content = html_content[section_start:section_end]
        
        # Find table rows in this section
        table_rows = re.findall(table_pattern, section_content, re.DOTALL)
        
        for row in table_rows:
            if len(row) >= 4:
                release_type = row[0].strip()
                service = row[1].strip()
                module_name = row[2].strip()
                release_notes = row[3].strip()
                
                # Clean up HTML entities
                release_notes = re.sub(r'&[^;]+;', ' ', release_notes)
                release_notes = re.sub(r'<[^>]+>', ' ', release_notes)
                release_notes = re.sub(r'\s+', ' ', release_notes).strip()
                
                # Categorize based on release type
                category = categorize_release(release_type)
                
                releases.append({
                    "Title": f"{release_type}: {service}",
                    "Body": f"Module: {module_name}\n\n{release_notes}",
                    "Category": category,
                    "Date": date_str
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
    Handles both simple JSON and Confluence HTML content.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to parse as JSON first
    try:
        data = json.loads(content)
        # If it's a simple list of dicts, return as is
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            return data
    except json.JSONDecodeError:
        pass
    
    # If not simple JSON, try to parse as Confluence HTML
    try:
        # Look for the actual content in the JSON structure
        json_data = json.loads(content)
        if 'body' in json_data and 'storage' in json_data['body']:
            html_content = json_data['body']['storage']['value']
            return parse_confluence_html_simple(html_content)
    except (json.JSONDecodeError, KeyError):
        pass
    
    # If all else fails, try to parse the content directly as HTML
    return parse_confluence_html_simple(content) 