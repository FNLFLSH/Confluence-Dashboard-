# Release Report Excel Exporter

A Python function that converts JSON-formatted release reports into a beautifully styled Excel sheet, organized by quarter with summary statistics.

## Features

✅ **Quarter Grouping**: Automatically groups reports by quarter (Q1-Q4)  
✅ **Professional Styling**: Elevance blue headers with white text  
✅ **Wrapped Text**: All report bodies have wrapped text and top alignment  
✅ **Summary Section**: 📊 Summary table with quarterly and yearly totals  
✅ **Auto-sizing**: Column widths automatically adjust to content  

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from src.excel_writer import export_grouped_by_quarter

# Your JSON data
data = [
    {
        "Title": "Bug Fix: Login Issue",
        "Body": "Fixed authentication problem that was preventing users from logging in.",
        "Category": "Bug Fix",
        "Date": "2024-01-15"
    },
    {
        "Title": "New Feature: Dark Mode",
        "Body": "Added dark mode theme option for better user experience.",
        "Category": "New Feature",
        "Date": "2024-02-20"
    }
]

# Export to Excel
export_grouped_by_quarter(data, "output/release_notes_output.xlsx")
```

### JSON String Input

```python
import json

json_string = '''
[
    {
        "Title": "Enhancement: Performance",
        "Body": "Improved page load times by 40%",
        "Category": "Enhancement",
        "Date": "2024-04-10"
    }
]
'''

export_grouped_by_quarter(json_string, "output/release_notes_output.xlsx")
```

## Data Format

Each report should be a dictionary with these fields:

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `Title` | Yes | Report title | "Bug Fix: Login Issue" |
| `Body` | Yes | Report details | "Fixed authentication problem..." |
| `Category` | Yes | Report type | "Bug Fix", "Enhancement", "New Feature", "Other" |
| `Date` | Yes | Report date (YYYY-MM-DD) | "2024-01-15" |

### Alternative Field Names

The function supports alternative field names for flexibility:

- `Title` → `Report` or `Name`
- `Body` → `Details` or `Description`  
- `Category` → `Type`

## Output Format

The Excel file will contain:

1. **Main Title**: "Release Reports by Quarter"
2. **Quarter Sections**: Each quarter (Q1-Q4) with its reports
3. **Styled Headers**: White text on Elevance blue (#0033A0) background
4. **Report Tables**: All reports for each quarter with wrapped text
5. **📊 Summary Section**: 
   - Quarterly counts by category
   - Yearly totals row

## Quarter Mapping

- **Q1**: January–March
- **Q2**: April–June  
- **Q3**: July–September
- **Q4**: October–December

## Styling Features

- **Headers**: White text on Elevance blue (#0033A0) background
- **Text Wrapping**: All report bodies wrap text and align to top
- **Borders**: Clean borders around all cells
- **Auto-sizing**: Column widths adjust to content (max 50 characters)
- **Quarter Headers**: Bold blue text for quarter sections
- **Summary**: Bold formatting for totals

## Example Output

```
Release Reports by Quarter

Q1 (Jan–Mar)
┌─────────┬────────────┬──────────┬────────────┐
│ Report  │ Details    │ Category │ Date       │
├─────────┼────────────┼──────────┼────────────┤
│ Bug Fix │ Fixed...   │ Bug Fix  │ 2024-01-15 │
└─────────┴────────────┴──────────┴────────────┘

📊 Summary
┌─────────────┬─────────┬─────────────┬─────────────┬───────┐
│ Quarter     │ Bug Fix │ Enhancement │ New Feature │ Other │
├─────────────┼─────────┼─────────────┼─────────────┼───────┤
│ Q1 (Jan–Mar)│    1    │      0      │      1      │   0   │
│ Yearly Total│    2    │      1      │      2      │   0   │
└─────────────┴─────────┴─────────────┴─────────────┴───────┘
```

## Testing

Run the main script to see the exporter in action:

```bash
python main.py
```

This will create a sample Excel file `output/release_notes_output.xlsx` with example data.

## Dependencies

- `openpyxl>=3.1.0` - Excel file creation and styling
- `pandas>=1.5.0` - Data manipulation and quarter calculation 