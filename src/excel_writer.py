import json
import re
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .utils import standardize_fields, add_quarter_column

def get_quarter_sort_key(q_string):
    """Generate a sort key for quarter strings (e.g., '2024 Q1 (Jan–Mar)')."""
    match = re.search(r'(\d{4}) Q(\d)', q_string)
    if match:
        year = int(match.group(1))
        quarter_num = int(match.group(2))
        # Sort by year first (descending - most recent first), then by quarter number
        return (-year, quarter_num)
    # Place "Unknown" or malformed quarters at the end
    return (9999, 5)

def export_grouped_by_quarter(data, filename):
    """
    Export release reports to a styled Excel sheet grouped by quarter.
    Args:
        data (list or str): List of dicts or JSON string
        filename (str): Output Excel file path
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    # Standardize the data
    data = standardize_fields(data)
    data = add_quarter_column(data)

    wb = Workbook()
    ws = wb.active
    ws.title = "Release Notes"

    # --- Styling ---
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
    ws.merge_cells('A1:D1')
    main_title_cell = ws['A1']
    main_title_cell.value = "Release Reports by Quarter"
    main_title_cell.font = main_title_font
    main_title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 30
    
    row = 3
    
    # Get a unique, sorted list of quarters based on the custom key
    all_q_with_dupes = [item['Quarter'] for item in data if item.get('Quarter')]
    quarters = sorted(list(set(all_q_with_dupes)), key=get_quarter_sort_key)
    
    summary = {}

    for q in quarters:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        q_header_cell = ws.cell(row=row, column=1, value=q)
        q_header_cell.font = quarter_header_font
        row += 1

        headers = ["Report", "Details", "Category", "Date"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_center
            cell.border = thin_border
        row += 1

        quarter_data = [item for item in data if item.get('Quarter') == q]
        
        for report in quarter_data:
            ws.cell(row=row, column=1, value=report.get("Title"))
            ws.cell(row=row, column=2, value=report.get("Body"))
            ws.cell(row=row, column=3, value=report.get("Category"))
            
            date_val = report.get("Date")
            if isinstance(date_val, str):
                try:
                    # Handle ISO format dates (e.g., 2024-01-15T00:00:00.000Z)
                    if date_val.endswith('Z'):
                        date_val = date_val[:-1]
                    date_val = datetime.fromisoformat(date_val)
                except (ValueError, TypeError):
                    # Fallback for simple date formats
                    try:
                        date_val = datetime.strptime(date_val, '%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass # Keep as string if all parsing fails
            
            # Convert datetime to formatted string for proper display
            if isinstance(date_val, datetime):
                date_cell = ws.cell(row=row, column=4, value=date_val.strftime('%Y-%m-%d'))
            else:
                date_cell = ws.cell(row=row, column=4, value=str(date_val) if date_val else "")
            
            for col in range(1, 5):
                cell = ws.cell(row=row, column=col)
                cell.alignment = align_wrap_top
                cell.border = thin_border
            row += 1

        counts = {}
        for report in quarter_data:
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

    for col_idx, header in enumerate(summary_headers, 1):
        cell = ws.cell(row=row, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center
        cell.border = thin_border
    row += 1

    grand_total = {cat: 0 for cat in all_cats}
    
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

    ws.cell(row=row, column=1, value="Yearly Total").font = total_font
    ws.cell(row=row, column=1).border = thin_border
    
    for idx, cat in enumerate(all_cats, 2):
        cell = ws.cell(row=row, column=idx, value=grand_total.get(cat, 0))
        cell.font = total_font
        cell.alignment = align_center
        cell.border = thin_border

    # --- Auto-size Columns ---
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 60
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 20
    for i in range(1, row):
        ws.row_dimensions[i].height = max(15, ws.row_dimensions[i].height or 15)

    # Save the workbook
    wb.save(filename)
    print(f"Excel report generated: {filename}")
    print(f"Total releases processed: {len(data)}")
    print(f"Quarters found: {len(quarters)}")
    print(f"Categories: {list(set(item['Category'] for item in data))}") 