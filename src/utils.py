from datetime import datetime

def standardize_fields(data):
    """Standardize field names in the data."""
    field_mapping = {
        'Title': ['Title', 'Report', 'Name'],
        'Body': ['Body', 'Details', 'Description'],
        'Category': ['Category', 'Type']
    }
    
    for item in data:
        for standard_name, alternatives in field_mapping.items():
            for alt_name in alternatives:
                if alt_name in item and standard_name not in item:
                    item[standard_name] = item[alt_name]
                    break
        
        # Set defaults if missing
        if 'Title' not in item:
            item['Title'] = 'Untitled'
        if 'Body' not in item:
            item['Body'] = 'No description provided'
        if 'Category' not in item:
            item['Category'] = 'Other'
        if 'Date' not in item:
            item['Date'] = datetime.now().strftime('%Y-%m-%d')
    
    return data

def add_quarter_column(data):
    """Add a year-inclusive quarter column (e.g., '2024 Q1 (Jan–Mar)') and sort data."""
    for item in data:
        try:
            date_str = item.get('Date', '')
            if not date_str:
                item['DateObject'] = datetime.max
                item['Quarter'] = 'Unknown'
                continue

            date_obj = datetime.fromisoformat(date_str.replace('Z', ''))
            
            month = date_obj.month
            year = date_obj.year
            
            if month <= 3:
                quarter = f"{year} Q1 (Jan–Mar)"
            elif month <= 6:
                quarter = f"{year} Q2 (Apr–Jun)"
            elif month <= 9:
                quarter = f"{year} Q3 (Jul–Sep)"
            else:
                quarter = f"{year} Q4 (Oct–Dec)"
            
            item['Quarter'] = quarter
            item['DateObject'] = date_obj
        except (ValueError, TypeError):
            item['Quarter'] = 'Unknown'
            item['DateObject'] = datetime.max
    
    data.sort(key=lambda x: x.get('DateObject', datetime.max))
    return data 