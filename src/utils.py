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
    """Add quarter column based on date."""
    for item in data:
        try:
            date_str = item['Date']
            if isinstance(date_str, str):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                date_obj = date_str
            
            month = date_obj.month
            year = date_obj.year
            
            if month <= 3:
                quarter = f"Q1 {year}"
            elif month <= 6:
                quarter = f"Q2 {year}"
            elif month <= 9:
                quarter = f"Q3 {year}"
            else:
                quarter = f"Q4 {year}"
            
            item['Quarter'] = quarter
        except (ValueError, TypeError):
            item['Quarter'] = 'Unknown'
    
    return data 