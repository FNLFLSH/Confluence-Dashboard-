import json
import re
from datetime import datetime

# Pre-compile regex patterns for better performance
HTML_TAG_PATTERN = re.compile(r'<.*?>')
HTML_ENTITY_PATTERN = re.compile(r'&[a-zA-Z0-9#]+;')
WHITESPACE_PATTERN = re.compile(r'\s+')
H3_SPLIT_PATTERN = re.compile(r'(<h3[^>]*>.*?</h3>)')
DATE_PATTERN = re.compile(r'<time datetime="([^"]+)"')
H3_TITLE_PATTERN = re.compile(r'\|\s*([^<]+)</h3>')
TABLE_PATTERN = re.compile(r'<table[^>]*>(.*?)</table>', re.DOTALL)
ROW_PATTERN = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
CELL_PATTERN = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL)
TERRAFORM_PATTERN = re.compile(r'terraform-[a-zA-Z0-9_-]+')  # Pre-compile terraform pattern

# Pre-compile metadata patterns for faster filtering
METADATA_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in [
        'type of release change',
        'service impacted', 
        'jira ticket id',
        'jira ticket',
        'ticket id'
    ]
]

def load_and_parse_json(filepath):
    """Load JSON file and return list of dicts."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def clean_html(raw_html):
    """Remove HTML tags, entities, and extra whitespace from a string."""
    if not isinstance(raw_html, str):
        return ""
    # Use pre-compiled patterns for better performance
    clean = HTML_TAG_PATTERN.sub('', raw_html)
    clean = HTML_ENTITY_PATTERN.sub(' ', clean)
    clean = WHITESPACE_PATTERN.sub(' ', clean).strip()
    return clean

def is_metadata_row_fast(cells):
    """
    Fast metadata row detection using pre-compiled patterns.
    Simplified to only filter out specific unwanted rows.
    """
    if not cells or len(cells) < 2:
        return False
    
    # Check first two cells for metadata patterns (most common location for headers)
    first_cell = clean_html(cells[0]).lower().strip()
    second_cell = clean_html(cells[1]).lower().strip() if len(cells) > 1 else ""
    
    # Use pre-compiled patterns for faster matching
    for pattern in METADATA_PATTERNS:
        if pattern.search(first_cell) or pattern.search(second_cell):
            return True
    
    return False

def parse_confluence_html_simple(html_content):
    """
    Parse Confluence HTML to extract release items from tables under h3 headers.
    Optimized for speed with pre-compiled patterns and reduced operations.
    Logs progress every 500 rows for large datasets.
    """
    releases = []
    
    # Split content by h3 tags using pre-compiled pattern
    content_blocks = H3_SPLIT_PATTERN.split(html_content)
    print(f"Processing {len(content_blocks)//2} content blocks...")

    for i in range(1, len(content_blocks), 2):
        if i % 20 == 1:  # Progress logging every 20 blocks instead of 10
            print(f"Processing block {i//2 + 1} of {len(content_blocks)//2}...")
        
        h3_tag = content_blocks[i]
        following_content = content_blocks[i + 1]

        # Extract date and title using pre-compiled patterns
        date_match = DATE_PATTERN.search(h3_tag)
        h3_title_match = H3_TITLE_PATTERN.search(h3_tag)
        
        h3_title = clean_html(h3_title_match.group(1)) if h3_title_match else ""
        h3_date = date_match.group(1) if date_match else ""

        # Fast category inference
        h3_lower = h3_title.lower()
        if 'enhancement' in h3_lower or 'updated' in h3_lower:
            category = 'Enhancement'
        elif 'new' in h3_lower or 'created' in h3_lower:
            category = 'New Feature'
        elif 'bug' in h3_lower or 'fix' in h3_lower:
            category = 'Bug Fix'
        else:
            category = "Other"

        # Find table using pre-compiled pattern
        table_match = TABLE_PATTERN.search(following_content)
        if not table_match:
            if h3_title:
                releases.append({
                    "Title": h3_title,
                    "Body": "No details provided in a table format.",
                    "ModuleName": "",
                    "Category": category,
                    "Date": h3_date
                })
            continue
        
        table_html = table_match.group(1)
        rows = ROW_PATTERN.findall(table_html)
        
        has_items = False
        for idx, row_html in enumerate(rows):
            if idx % 200 == 0:  # Progress logging every 200 rows instead of 100
                print(f"    Processing row {idx+1} of {len(rows)} in table {i//2 + 1}")
            if '<th' in row_html.lower():  # Skip header rows with th tags
                continue

            cells = CELL_PATTERN.findall(row_html)
            
            # Skip header rows that have header text in first cell
            if cells and len(cells) > 0:
                first_cell_text = clean_html(cells[0]).lower().strip()
                if first_cell_text in ['type of release change', 'type of release', 'release change']:
                    continue
            
            # Fast metadata row filtering
            if is_metadata_row_fast(cells):
                continue
            
            # Process valid rows - expect 7 columns: Type, Service, Jira Ticket ID, TFE Module Name, Release Notes, Dependencies, Version
            if len(cells) >= 7:
                report_title = clean_html(cells[0])  # Type of Release Change
                service_impacted = clean_html(cells[1])  # Service Impacted
                jira_ticket = clean_html(cells[2])  # Jira Ticket ID
                module_name_cell = clean_html(cells[3])  # TFE Module Name column
                details = clean_html(cells[4])  # Release Notes
                dependencies = clean_html(cells[5])  # Dependencies
                item_date = clean_html(cells[6])  # TFE Module Version
                
                # Extract terraform module name from the TFE Module Name column
                module_name = extract_terraform_module_name(module_name_cell)
                
                # Check if this is a new module release
                is_new_release = False
                if 'new module release' in report_title.lower() or 'new module release' in details.lower():
                    is_new_release = True
                    category = 'New Release'  # Override category for new releases
                
                # Fast date validation
                try:
                    if 'T' in item_date:
                        item_date = item_date.split('T')[0]
                    datetime.strptime(item_date, '%Y-%m-%d')
                    final_date = item_date
                except (ValueError, TypeError):
                    final_date = h3_date

                if report_title or details:
                    releases.append({
                        "Title": report_title,
                        "Body": details,
                        "ModuleName": module_name,  # Use the actual TFE module name from the data
                        "Category": category,
                        "NewRelease": is_new_release,  # New field to track new module releases
                        "Date": final_date
                    })
                    has_items = True

                # Progress logging every 1000 records instead of 500
                if len(releases) % 1000 == 0:
                    print(f"Parsed {len(releases)} release records so far...")

        # Fallback for empty tables
        if not has_items and h3_title:
             releases.append({
                "Title": h3_title,
                "Body": "No items found in the table for this release.",
                "ModuleName": "",
                "Category": category,
                "NewRelease": False,  # Add NewRelease field to fallback
                "Date": h3_date,
            })
            
    print(f"Total releases parsed: {len(releases)}")
    return releases

def extract_terraform_module_name(text):
    """
    Extract terraform module name from text content.
    Looks for patterns like terraform-aws-* or terraform-* and returns the first match.
    """
    match = TERRAFORM_PATTERN.search(text)
    if match:
        return match.group(0)
    return ""

def extract_module_name(title, details):
    """
    This function is no longer used since we extract module names directly from the JSON data.
    Keeping for backward compatibility but it should not be called.
    """
    return ""

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