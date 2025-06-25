import json
import re
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .utils import standardize_fields, add_quarter_column
from collections import defaultdict

# Pre-compile regex for quarter sorting
QUARTER_SORT_PATTERN = re.compile(r'(\d{4}) Q(\d)')

def get_quarter_sort_key(q_string):
    """Generate a sort key for quarter strings (e.g., '2024 Q1 (Jan–Mar)')."""
    match = QUARTER_SORT_PATTERN.search(q_string)
    if match:
        year = int(match.group(1))
        quarter_num = int(match.group(2))
        # Sort by year first (descending - most recent first), then by quarter number
        return (-year, quarter_num)
    # Place "Unknown" or malformed quarters at the end
    return (9999, 5)

def analyze_module_changes(data):
    """
    Analyze modules that have undergone multiple changes within quarters and years.
    Returns data for modules with 2+ changes per quarter and 3+ changes per year.
    """
    # Group by module name and quarter/year
    module_quarter_changes = defaultdict(lambda: defaultdict(list))
    module_year_changes = defaultdict(lambda: defaultdict(list))
    
    for item in data:
        module_name = item.get('ModuleName', '').strip()
        if not module_name:  # Skip items without module names
            continue
            
        quarter = item.get('Quarter', '')
        category = item.get('Category', 'Other')
        date = item.get('Date', '')
        
        # Extract year from quarter or date
        year = None
        if quarter:
            year_match = re.search(r'(\d{4})', quarter)
            if year_match:
                year = year_match.group(1)
        elif date:
            try:
                if isinstance(date, str):
                    if 'T' in date:
                        date = date.split('T')[0]
                    year = datetime.strptime(date, '%Y-%m-%d').year
                elif isinstance(date, datetime):
                    year = date.year
            except (ValueError, TypeError):
                pass
        
        if quarter:
            module_quarter_changes[module_name][quarter].append({
                'title': item.get('Title', ''),
                'category': category,
                'date': date
            })
        
        if year:
            module_year_changes[module_name][str(year)].append({
                'title': item.get('Title', ''),
                'category': category,
                'date': date
            })
    
    # Find modules with multiple changes
    frequent_quarter_changes = []
    frequent_year_changes = []
    
    for module_name, quarters in module_quarter_changes.items():
        for quarter, changes in quarters.items():
            if len(changes) >= 2:  # 2 or more changes in a quarter
                frequent_quarter_changes.append({
                    'module_name': module_name,
                    'period': quarter,
                    'change_count': len(changes),
                    'changes': changes
                })
    
    for module_name, years in module_year_changes.items():
        for year, changes in years.items():
            if len(changes) >= 3:  # 3 or more changes in a year
                frequent_year_changes.append({
                    'module_name': module_name,
                    'period': year,
                    'change_count': len(changes),
                    'changes': changes
                })
    
    # Sort by change count (descending), then by module name
    frequent_quarter_changes.sort(key=lambda x: (-x['change_count'], x['module_name']))
    frequent_year_changes.sort(key=lambda x: (-x['change_count'], x['module_name']))
    
    return frequent_quarter_changes, frequent_year_changes

def export_grouped_by_quarter(data, filename):
    """
    Export release reports to a styled Excel sheet grouped by quarter.
    Optimized for speed with reduced operations and better data structures.
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    # Standardize the data
    data = standardize_fields(data)
    data = add_quarter_column(data)

    wb = Workbook()
    ws = wb.active
    ws.title = "Release Notes"

    # --- Pre-define styles for better performance ---
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="0033A0", end_color="0033A0", fill_type="solid")
    quarter_header_font = Font(bold=True, size=14, color="0033A0", underline="single")
    main_title_font = Font(bold=True, size=18, color="0033A0")
    total_font = Font(bold=True)
    align_wrap_top = Alignment(wrap_text=True, vertical="top", horizontal="left")
    align_center = Alignment(horizontal="center", vertical="center")
    thin_border = Border(left=Side(style='thin'), 
                         right=Side(style='thin'), 
                         top=Side(style='thin'), 
                         bottom=Side(style='thin'))

    # --- Main Title ---
    ws.merge_cells('A1:E1')
    main_title_cell = ws['A1']
    main_title_cell.value = "Release Reports by Quarter"
    main_title_cell.font = main_title_font
    main_title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 30
    
    row = 3
    
    # Get unique quarters and sort them efficiently
    quarter_data = {}
    for item in data:
        quarter = item.get('Quarter')
        if quarter:
            if quarter not in quarter_data:
                quarter_data[quarter] = []
            quarter_data[quarter].append(item)
    
    quarters = sorted(quarter_data.keys(), key=get_quarter_sort_key)
    
    summary = {}

    for q in quarters:
        # Quarter header
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
        q_header_cell = ws.cell(row=row, column=1, value=q)
        q_header_cell.font = quarter_header_font
        row += 1

        # Table headers
        headers = ["Report", "Details", "Module Name", "Category", "Date"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_center
            cell.border = thin_border
        row += 1

        # Process quarter data - filter out new module releases
        quarter_items = [item for item in quarter_data[q] if not (
            item.get("NewRelease", False) or 
            "new release" in (item.get("Body", "") or "").lower() or
            "new release" in (item.get("Title", "") or "").lower()
        )]
        counts = {}
        
        for report in quarter_items:
            # Write data efficiently
            ws.cell(row=row, column=1, value=report.get("Title"))
            ws.cell(row=row, column=2, value=report.get("Body"))
            ws.cell(row=row, column=3, value=report.get("ModuleName", ""))
            ws.cell(row=row, column=4, value=report.get("Category"))
            
            # Optimized date handling
            date_val = report.get("Date")
            if isinstance(date_val, str):
                try:
                    if date_val.endswith('Z'):
                        date_val = date_val[:-1]
                    if 'T' in date_val:
                        date_val = date_val.split('T')[0]
                    date_val = datetime.fromisoformat(date_val)
                except (ValueError, TypeError):
                    try:
                        date_val = datetime.strptime(date_val, '%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
            
            # Format date for display
            if isinstance(date_val, datetime):
                date_cell = ws.cell(row=row, column=5, value=date_val.strftime('%Y-%m-%d'))
            else:
                date_cell = ws.cell(row=row, column=5, value=str(date_val) if date_val else "")
            
            # Apply styling efficiently
            for col in range(1, 6):
                cell = ws.cell(row=row, column=col)
                cell.alignment = align_wrap_top
                cell.border = thin_border
            row += 1

            # Count categories
            cat = report.get('Category', 'Other')
            counts[cat] = counts.get(cat, 0) + 1
        
        summary[q] = counts
        row += 1

    # --- Summary Section ---
    row += 1
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
    summary_title_cell = ws.cell(row=row, column=1, value="📊 Summary")
    summary_title_cell.font = quarter_header_font
    row += 1
    
    summary_headers = ["Quarter", "Bug Fix", "Enhancement", "New Feature", "Other"]
    all_cats = ["Bug Fix", "Enhancement", "New Feature", "Other"]

    # Summary headers
    for col_idx, header in enumerate(summary_headers, 1):
        cell = ws.cell(row=row, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center
        cell.border = thin_border
    row += 1

    grand_total = {cat: 0 for cat in all_cats}
    
    # Summary data
    for quarter in quarters:
        counts = summary.get(quarter, {})
        q_cell = ws.cell(row=row, column=1, value=quarter)
        q_cell.border = thin_border
        
        for idx, cat in enumerate(all_cats, 2):
            count = counts.get(cat, 0)
            cell = ws.cell(row=row, column=idx, value=count)
            cell.alignment = align_center
            cell.border = thin_border
            grand_total[cat] += count
        row += 1

    # Yearly totals
    ws.cell(row=row, column=1, value="Yearly Total").font = total_font
    ws.cell(row=row, column=1).border = thin_border
    
    for idx, cat in enumerate(all_cats, 2):
        cell = ws.cell(row=row, column=idx, value=grand_total.get(cat, 0))
        cell.font = total_font
        cell.alignment = align_center
        cell.border = thin_border

    # --- Auto-size Columns ---
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 50
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 20
    
    # Optimize row heights
    for i in range(1, row + 1):
        ws.row_dimensions[i].height = max(15, ws.row_dimensions[i].height or 15)

    # Save the workbook
    wb.save(filename)
    print(f"Excel report generated: {filename}")
    print(f"Total releases processed: {len(data)}")
    print(f"Quarters found: {len(quarters)}")
    print(f"Categories: {list(set(item['Category'] for item in data))}")

def export_frequent_changes_report(data, filename):
    """
    Export a separate report showing modules with frequent changes.
    Creates a dedicated Excel file for frequent module changes analysis.
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    # Standardize the data
    data = standardize_fields(data)
    data = add_quarter_column(data)
    
    # Analyze frequent changes
    print("Analyzing modules with frequent changes...")
    frequent_quarter_changes, frequent_year_changes = analyze_module_changes(data)
    
    # Create new workbook for frequent changes
    wb = Workbook()
    ws = wb.active
    ws.title = "Frequent Module Changes"
    
    # --- Pre-define styles for better performance ---
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="0033A0", end_color="0033A0", fill_type="solid")
    quarter_header_font = Font(bold=True, size=14, color="0033A0", underline="single")
    main_title_font = Font(bold=True, size=18, color="0033A0")
    total_font = Font(bold=True)
    align_wrap_top = Alignment(wrap_text=True, vertical="top", horizontal="left")
    align_center = Alignment(horizontal="center", vertical="center")
    thin_border = Border(left=Side(style='thin'), 
                         right=Side(style='thin'), 
                         top=Side(style='thin'), 
                         bottom=Side(style='thin'))
    
    # --- Main Title ---
    ws.merge_cells('A1:E1')
    main_title_cell = ws['A1']
    main_title_cell.value = "Modules with Frequent Changes - Analysis Report"
    main_title_cell.font = main_title_font
    main_title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 30
    
    row = 3
    
    # --- Description Section ---
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
    desc_title = ws.cell(row=row, column=1, value="📋 Analysis Logic & Purpose")
    desc_title.font = Font(bold=True, size=12, color="0033A0")
    row += 1
    
    # Add description text
    description_text = [
        "This report identifies modules that have undergone frequent changes, helping to:",
        "• Identify modules requiring special attention or refactoring",
        "• Track development velocity and maintenance patterns", 
        "• Highlight potential technical debt or stability issues",
        "",
        "Quarterly Analysis: Modules with 2+ changes in a single quarter",
        "Yearly Analysis: Modules with 3+ changes in a single year",
        "",
        "Note: Each row represents a module that exceeded the threshold in that specific time period."
    ]
    
    for desc_line in description_text:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
        desc_cell = ws.cell(row=row, column=1, value=desc_line)
        desc_cell.font = Font(size=10)
        desc_cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        row += 1
    
    row += 2  # Add spacing
    
    # --- Quarterly Changes Section ---
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
    q_frequent_title = ws.cell(row=row, column=1, value="📈 Quarterly Analysis: Modules with 2+ Changes per Quarter")
    q_frequent_title.font = quarter_header_font
    row += 1
    
    if frequent_quarter_changes:
        # Group quarterly changes by quarter for better organization
        quarter_groups = {}
        for item in frequent_quarter_changes:
            quarter = item['period']
            if quarter not in quarter_groups:
                quarter_groups[quarter] = []
            quarter_groups[quarter].append(item)
        
        # Sort quarters
        sorted_quarters = sorted(quarter_groups.keys(), key=get_quarter_sort_key)
        
        for quarter in sorted_quarters:
            # Quarter sub-header
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
            quarter_subtitle = ws.cell(row=row, column=1, value=f"Quarter: {quarter}")
            quarter_subtitle.font = Font(bold=True, size=11, color="2E5C8A")
            quarter_subtitle.fill = PatternFill(start_color="E6F3FF", end_color="E6F3FF", fill_type="solid")
            row += 1
            
            # Headers for this quarter
            q_headers = ["Module Name", "Change Count", "Changes Summary", "Change Details"]
            for col_idx, header in enumerate(q_headers, 1):
                cell = ws.cell(row=row, column=col_idx, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = align_center
                cell.border = thin_border
            row += 1
            
            # Data for this quarter
            for item in quarter_groups[quarter]:
                ws.cell(row=row, column=1, value=item['module_name'])
                ws.cell(row=row, column=2, value=item['change_count'])
                
                # Create summary text
                categories = {}
                for change in item['changes']:
                    cat = change['category']
                    categories[cat] = categories.get(cat, 0) + 1
                
                summary_parts = []
                for cat, count in categories.items():
                    summary_parts.append(f"{cat}: {count}")
                summary_text = ", ".join(summary_parts)
                
                ws.cell(row=row, column=3, value=summary_text)
                
                # Format detailed changes
                changes_text = []
                for i, change in enumerate(item['changes'], 1):
                    change_str = f"{i}. {change['category']}: {change['title']}"
                    changes_text.append(change_str)
                
                changes_cell = ws.cell(row=row, column=4, value="\n".join(changes_text))
                changes_cell.alignment = align_wrap_top
                
                # Apply styling
                for col in range(1, 5):
                    cell = ws.cell(row=row, column=col)
                    cell.border = thin_border
                row += 1
            
            row += 1  # Add spacing between quarters
    else:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
        no_q_data = ws.cell(row=row, column=1, value="✅ No modules found with 2+ changes per quarter")
        no_q_data.font = Font(italic=True, color="008000")
        row += 1
    
    row += 2  # Add spacing before yearly section
    
    # --- Yearly Changes Section ---
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
    y_frequent_title = ws.cell(row=row, column=1, value="📊 Yearly Analysis: Modules with 3+ Changes per Year")
    y_frequent_title.font = quarter_header_font
    row += 1
    
    if frequent_year_changes:
        # Headers for yearly changes
        y_headers = ["Module Name", "Year", "Total Changes", "Quarterly Breakdown", "Change Details"]
        for col_idx, header in enumerate(y_headers, 1):
            cell = ws.cell(row=row, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_center
            cell.border = thin_border
        row += 1
        
        # Data for yearly changes
        for item in frequent_year_changes:
            ws.cell(row=row, column=1, value=item['module_name'])
            ws.cell(row=row, column=2, value=item['period'])
            ws.cell(row=row, column=3, value=item['change_count'])
            
            # Create quarterly breakdown
            quarter_counts = {}
            for change in item['changes']:
                # Extract quarter from date if possible
                date_str = str(change['date'])
                try:
                    if 'T' in date_str:
                        date_str = date_str.split('T')[0]
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    quarter = f"Q{(date_obj.month-1)//3 + 1}"
                    quarter_counts[quarter] = quarter_counts.get(quarter, 0) + 1
                except:
                    quarter_counts['Unknown'] = quarter_counts.get('Unknown', 0) + 1
            
            breakdown_text = ", ".join([f"{q}: {c}" for q, c in sorted(quarter_counts.items())])
            ws.cell(row=row, column=4, value=breakdown_text)
            
            # Format detailed changes
            changes_text = []
            for i, change in enumerate(item['changes'], 1):
                change_str = f"{i}. {change['category']}: {change['title']}"
                changes_text.append(change_str)
            
            changes_cell = ws.cell(row=row, column=5, value="\n".join(changes_text))
            changes_cell.alignment = align_wrap_top
            
            # Apply styling
            for col in range(1, 6):
                cell = ws.cell(row=row, column=col)
                cell.border = thin_border
            row += 1
    else:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
        no_y_data = ws.cell(row=row, column=1, value="✅ No modules found with 3+ changes per year")
        no_y_data.font = Font(italic=True, color="008000")
        row += 1
    
    # --- Auto-size columns ---
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 50
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 20
    
    # Optimize row heights
    for i in range(1, row + 1):
        ws.row_dimensions[i].height = max(15, ws.row_dimensions[i].height or 15)
    
    # Save the workbook
    wb.save(filename)
    print(f"Frequent changes report generated: {filename}")
    print(f"Frequent changes analysis: {len(frequent_quarter_changes)} quarterly, {len(frequent_year_changes)} yearly")

def create_new_releases_report(data, output_file):
    """
    Create a separate report specifically for new module releases.
    Only includes Date, Module Name, and Details columns.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "New Module Releases"
    
    # Remove default sheet
    if len(wb.sheetnames) > 1:
        wb.remove(wb['Sheet'])
    
    # Filter data to only include new releases
    new_releases = [item for item in data if (
        item.get("NewRelease", False) or 
        "new release" in (item.get("Body", "") or "").lower() or
        "new release" in (item.get("Title", "") or "").lower()
    )]
    
    if not new_releases:
        # If no new releases, create empty report with headers
        headers = ["Date", "Module Name", "Details"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = Font(bold=True, size=12)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF", size=12)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                               top=Side(style="thin"), bottom=Side(style="thin"))
        
        # Set column widths
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 60
        
        wb.save(output_file)
        return
    
    # Sort by date
    new_releases.sort(key=lambda x: x.get("Date", ""))
    
    # Create headers
    headers = ["Date", "Module Name", "Details"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True, size=12)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF", size=12)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                           top=Side(style="thin"), bottom=Side(style="thin"))
    
    # Add data
    row = 2
    for release in new_releases:
        # Date
        date_val = release.get("Date")
        if isinstance(date_val, str):
            try:
                if date_val.endswith('Z'):
                    date_val = date_val[:-1]
                if 'T' in date_val:
                    date_val = date_val.split('T')[0]
                date_val = datetime.fromisoformat(date_val)
            except (ValueError, TypeError):
                try:
                    date_val = datetime.strptime(date_val, '%Y-%m-%d')
                except (ValueError, TypeError):
                    pass
        
        if isinstance(date_val, datetime):
            ws.cell(row=row, column=1, value=date_val.strftime('%Y-%m-%d'))
        else:
            ws.cell(row=row, column=1, value=str(date_val) if date_val else "")
        
        # Module Name
        ws.cell(row=row, column=2, value=release.get("ModuleName", ""))
        
        # Details
        ws.cell(row=row, column=3, value=release.get("Body", ""))
        
        # Apply styling
        for col in range(1, 4):
            cell = ws.cell(row=row, column=col)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                               top=Side(style="thin"), bottom=Side(style="thin"))
        
        row += 1
    
    # Add summary section
    summary_row = row + 2
    
    # Title for summary
    summary_title = ws.cell(row=summary_row, column=1, value="SUMMARY")
    summary_title.font = Font(bold=True, size=14)
    summary_title.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    summary_title.font = Font(bold=True, color="FFFFFF", size=14)
    summary_title.alignment = Alignment(horizontal="center", vertical="center")
    summary_title.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                                 top=Side(style="thin"), bottom=Side(style="thin"))
    ws.merge_cells(f'A{summary_row}:C{summary_row}')
    
    # Total count
    summary_row += 1
    total_label = ws.cell(row=summary_row, column=1, value="Total New Releases:")
    total_label.font = Font(bold=True, size=12)
    total_count = ws.cell(row=summary_row, column=2, value=len(new_releases))
    total_count.font = Font(bold=True, size=12)
    
    # Quarterly summary
    summary_row += 2
    quarter_title = ws.cell(row=summary_row, column=1, value="Quarterly Breakdown")
    quarter_title.font = Font(bold=True, size=12)
    quarter_title.fill = PatternFill(start_color="8EAADB", end_color="8EAADB", fill_type="solid")
    quarter_title.alignment = Alignment(horizontal="center", vertical="center")
    quarter_title.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                                 top=Side(style="thin"), bottom=Side(style="thin"))
    ws.merge_cells(f'A{summary_row}:C{summary_row}')
    
    # Calculate quarterly counts
    quarter_counts = {}
    year_counts = {}
    
    for release in new_releases:
        date_val = release.get("Date")
        if isinstance(date_val, str):
            try:
                if date_val.endswith('Z'):
                    date_val = date_val[:-1]
                if 'T' in date_val:
                    date_val = date_val.split('T')[0]
                date_val = datetime.fromisoformat(date_val)
            except (ValueError, TypeError):
                try:
                    date_val = datetime.strptime(date_val, '%Y-%m-%d')
                except (ValueError, TypeError):
                    continue
        
        if isinstance(date_val, datetime):
            year = date_val.year
            quarter = f"Q{(date_val.month - 1) // 3 + 1}"
            quarter_key = f"{year} {quarter}"
            
            quarter_counts[quarter_key] = quarter_counts.get(quarter_key, 0) + 1
            year_counts[year] = year_counts.get(year, 0) + 1
    
    # Display quarterly counts
    summary_row += 1
    quarter_header = ws.cell(row=summary_row, column=1, value="Quarter")
    quarter_header.font = Font(bold=True, size=11)
    quarter_header.fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")
    quarter_header.alignment = Alignment(horizontal="center", vertical="center")
    quarter_header.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                                  top=Side(style="thin"), bottom=Side(style="thin"))
    
    count_header = ws.cell(row=summary_row, column=2, value="Count")
    count_header.font = Font(bold=True, size=11)
    count_header.fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")
    count_header.alignment = Alignment(horizontal="center", vertical="center")
    count_header.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                                top=Side(style="thin"), bottom=Side(style="thin"))
    
    # Sort quarters chronologically
    sorted_quarters = sorted(quarter_counts.keys(), key=lambda x: (int(x.split()[0]), x.split()[1]))
    
    for quarter in sorted_quarters:
        summary_row += 1
        ws.cell(row=summary_row, column=1, value=quarter)
        ws.cell(row=summary_row, column=2, value=quarter_counts[quarter])
        
        # Apply styling
        for col in range(1, 3):
            cell = ws.cell(row=summary_row, column=col)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                               top=Side(style="thin"), bottom=Side(style="thin"))
    
    # Yearly summary
    summary_row += 2
    year_title = ws.cell(row=summary_row, column=1, value="Yearly Breakdown")
    year_title.font = Font(bold=True, size=12)
    year_title.fill = PatternFill(start_color="8EAADB", end_color="8EAADB", fill_type="solid")
    year_title.alignment = Alignment(horizontal="center", vertical="center")
    year_title.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                              top=Side(style="thin"), bottom=Side(style="thin"))
    ws.merge_cells(f'A{summary_row}:C{summary_row}')
    
    summary_row += 1
    year_header = ws.cell(row=summary_row, column=1, value="Year")
    year_header.font = Font(bold=True, size=11)
    year_header.fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")
    year_header.alignment = Alignment(horizontal="center", vertical="center")
    year_header.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                               top=Side(style="thin"), bottom=Side(style="thin"))
    
    year_count_header = ws.cell(row=summary_row, column=2, value="Count")
    year_count_header.font = Font(bold=True, size=11)
    year_count_header.fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")
    year_count_header.alignment = Alignment(horizontal="center", vertical="center")
    year_count_header.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                                     top=Side(style="thin"), bottom=Side(style="thin"))
    
    # Sort years chronologically
    sorted_years = sorted(year_counts.keys())
    
    for year in sorted_years:
        summary_row += 1
        ws.cell(row=summary_row, column=1, value=year)
        ws.cell(row=summary_row, column=2, value=year_counts[year])
        
        # Apply styling
        for col in range(1, 3):
            cell = ws.cell(row=summary_row, column=col)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(left=Side(style="thin"), right=Side(style="thin"), 
                               top=Side(style="thin"), bottom=Side(style="thin"))
    
    # Set column widths
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 60
    
    # Auto-adjust row heights
    for row in ws.iter_rows():
        max_height = 0
        for cell in row:
            if cell.value:
                lines = str(cell.value).count('\n') + 1
                height = min(max(lines * 15, 20), 100)
                max_height = max(max_height, height)
        if max_height > 0:
            ws.row_dimensions[cell.row].height = max_height
    
    wb.save(output_file)
    print(f"New releases report generated: {output_file}")
    print(f"Total new releases found: {len(new_releases)}")
    print(f"Quarters with new releases: {len(quarter_counts)}")
    print(f"Years with new releases: {len(year_counts)}") 