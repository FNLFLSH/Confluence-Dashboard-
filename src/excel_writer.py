import json
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .utils import standardize_fields, add_quarter_column

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

    row = 1
    quarters = sorted(list(set(item['Quarter'] for item in data)))
    summary = {}

    # Style setup
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="0033A0", end_color="0033A0", fill_type="solid")
    align = Alignment(wrap_text=True, vertical="top")

    for q in quarters:
        # Add quarter header
        ws.cell(row=row, column=1, value=q)
        ws.cell(row=row, column=1).font = Font(bold=True, size=12)
        row += 1

        # Write headers with styling
        headers = ["Report", "Details", "Category", "Date"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
        row += 1

        # Write report rows
        quarter_data = [item for item in data if item['Quarter'] == q]
        for report in quarter_data:
            ws.cell(row=row, column=1, value=report["Title"])
            ws.cell(row=row, column=2, value=report["Body"])
            ws.cell(row=row, column=3, value=report["Category"])
            ws.cell(row=row, column=4, value=report["Date"])
            for col in range(1, 5):
                ws.cell(row=row, column=col).alignment = align
            row += 1

        # Collect summary info
        counts = {}
        for report in quarter_data:
            cat = report['Category']
            counts[cat] = counts.get(cat, 0) + 1
        summary[q] = counts

        row += 2

    # Summary header
    ws.cell(row=row, column=1, value="📊 Summary").font = Font(bold=True, size=14)
    row += 1
    summary_headers = ["Quarter", "Bug Fix", "Enhancement", "New Feature", "Other"]
    for col_idx, header in enumerate(summary_headers, 1):
        cell = ws.cell(row=row, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
    row += 1

    # Per-quarter summary
    grand_total = {"Bug Fix": 0, "Enhancement": 0, "New Feature": 0, "Other": 0}
    for quarter, counts in summary.items():
        ws.cell(row=row, column=1, value=quarter)
        for idx, cat in enumerate(["Bug Fix", "Enhancement", "New Feature", "Other"], 2):
            count = counts.get(cat, 0)
            ws.cell(row=row, column=idx, value=count)
            grand_total[cat] += count
        row += 1

    # Yearly total row
    ws.cell(row=row, column=1, value="Yearly Total").font = Font(bold=True)
    for idx, cat in enumerate(["Bug Fix", "Enhancement", "New Feature", "Other"], 2):
        ws.cell(row=row, column=idx, value=grand_total[cat]).font = Font(bold=True)
    row += 1

    # Auto-size columns
    for col in range(1, 5):
        ws.column_dimensions[get_column_letter(col)].width = 20

    # Save the workbook
    wb.save(filename)
    print(f"Excel report generated successfully: {filename}")
    print(f"Total releases processed: {len(data)}")
    print(f"Quarters found: {len(quarters)}")
    print(f"Categories: {list(set(item['Category'] for item in data))}") 