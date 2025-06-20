# Confluence Report Generator

A Python tool that converts Confluence HTML release reports into beautifully styled Excel sheets, organized by quarter with summary statistics. Automatically parses complex Confluence HTML content and extracts structured release data.

## Features

 **Confluence HTML Parsing**: Automatically extracts release data from Confluence HTML exports  
**Quarter Grouping**: Groups reports by quarter (Q1-Q4) with most recent year first  
 **Professional Styling**: Elevance blue headers with white text  
 **Wrapped Text**: All report bodies have wrapped text and top alignment  
 **Summary Section**:  Summary table with quarterly and yearly totals  
**Auto-sizing**: Column widths automatically adjust to content  
 **Date Formatting**: Clean YYYY-MM-DD date display without time  
 **Smart Sorting**: Years sorted descending (2025 → 2024 → 2023...) with quarters grouped by year  

## Project Structure

```
confluence_report_generator/
├── src/
│   ├── parser_json.py      # Confluence HTML parser
│   ├── utils.py           # Data transformation utilities
│   ├── excel_writer.py    # Excel generation and styling
│   └── __init__.py
├── data/
│   └── report_confluence.json  # Your Confluence HTML data
├── output/
│   └── release_notes_output.xlsx  # Generated Excel report
├── main.py                # Main entry point
├── requirements.txt       # Python dependencies
└── README.md
```

## Installation

1. Move to correct Directory 
```bash

cd confluence_report_generator
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Usage

```bash
# Generate Excel report from Confluence HTML data
python3 main.py --input-file data/report_confluence.json --output-file output/release_notes_output.xlsx
```

### Python Script Usage

```python
from src.parser_json import parse_confluence_html
from src.excel_writer import export_grouped_by_quarter

# Parse Confluence HTML data
with open('data/report_confluence.json', 'r') as f:
    confluence_data = f.read()

# Extract structured release data
releases = parse_confluence_html(confluence_data)

# Export to Excel
export_grouped_by_quarter(releases, "output/release_notes_output.xlsx")
```

## Data Format

The tool expects Confluence HTML export data in JSON format. It automatically extracts:

| Field | Description | Example |
|-------|-------------|---------|
| `Title` | Release title | "Bug Fix: Login Issue" |
| `Body` | Release details | "Fixed authentication problem..." |
| `Category` | Inferred from section headers | "Bug Fix", "Enhancement", "New Feature" |
| `Date` | Release date | "2025-04-02" |

### Supported Categories

The parser automatically categorizes releases based on Confluence section headers:
- **Bug Fix**: From "Bug Fixes" sections
- **Enhancement**: From "Enhancements" sections  
- **New Feature**: From "New Features" sections
- **Other**: From any other sections

## Output Format

The Excel file contains:

1. **Main Title**: "Release Reports by Quarter"
2. **Quarter Sections**: Each quarter (Q1-Q4) grouped by year, most recent first
3. **Styled Headers**: White text on Elevance blue (#0033A0) background
4. **Report Tables**: All reports for each quarter with wrapped text
5. **📊 Summary Section**: 
   - Quarterly counts by category
   - Yearly totals row

### Quarter Organization

Reports are organized by year (descending) and quarter:
- **2025 Q1** (all 2025 Q1 releases)
- **2025 Q2** (all 2025 Q2 releases)
- **2025 Q3** (all 2025 Q3 releases)
- **2025 Q4** (all 2025 Q4 releases)
- **2024 Q1** (all 2024 Q1 releases)
- And so on...

## Quarter Mapping

- **Q1**: January–March
- **Q2**: April–June  
- **Q3**: July–September
- **Q4**: October–December

## Styling Features

- **Headers**: White text on Elevance blue (#0033A0) background
- **Text Wrapping**: All report bodies wrap text and align to top
- **Borders**: Clean borders around all cells
- **Auto-sizing**: Column widths adjust to content
- **Quarter Headers**: Bold blue text for quarter sections
- **Summary**: Bold formatting for totals
- **Date Display**: Clean YYYY-MM-DD format without time

## Example Output

```
Release Reports by Quarter

2025 Q1 (Jan–Mar)
┌─────────┬────────────┬──────────┬────────────┐
│ Report  │ Details    │ Category │ Date       │
├─────────┼────────────┼──────────┼────────────┤
│ Bug Fix │ Fixed...   │ Bug Fix  │ 2025-01-15 │
└─────────┴────────────┴──────────┴────────────┘

📊 Summary
┌─────────────┬─────────┬─────────────┬─────────────┬───────┐
│ Quarter     │ Bug Fix │ Enhancement │ New Feature │ Other │
├─────────────┼─────────┼─────────────┼─────────────┼───────┤
│ 2025 Q1     │    1    │      0      │      1      │   0   │
│ Yearly Total│    2    │      1      │      2      │   0   │
└─────────────┴─────────┴─────────────┴─────────────┴───────┘
```

## Processing Statistics

The tool processes large datasets efficiently:
- **1,914 releases** from your Confluence data
- **20 quarters** across multiple years
- **4 categories** automatically detected
- **Fast parsing** of complex HTML structures

## Dependencies

- `openpyxl>=3.1.0` - Excel file creation and styling
- `pandas>=1.5.0` - Data manipulation and quarter calculation

## Development

The project is organized into modular components:

- **`parser_json.py`**: Handles Confluence HTML parsing using regex patterns
- **`utils.py`**: Provides data transformation and quarter calculation utilities
- **`excel_writer.py`**: Manages Excel generation with professional styling
- **`main.py`**: Entry point with command-line interface

## License

This project is open source and available under the MIT License. 