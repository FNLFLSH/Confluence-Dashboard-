import os
import sys
import argparse
from src.parser_json import load_and_parse_confluence_data
from src.excel_writer import export_grouped_by_quarter

def main():
    parser = argparse.ArgumentParser(description='Generate Excel reports from Confluence HTML data')
    parser.add_argument('--input-file', required=True, help='Input JSON file path')
    parser.add_argument('--output-file', required=True, help='Output Excel file path for consolidated report')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Loading data from: {args.input_file}")
    data = load_and_parse_confluence_data(args.input_file)
    print(f"Parsed {len(data)} releases")
    
    # Generate consolidated Excel report with all worksheets
    print(f"Generating consolidated Excel report: {args.output_file}")
    export_grouped_by_quarter(data, args.output_file)
    
    print(f"Consolidated report generated successfully!")
    print(f"Single Excel file with all reports: {args.output_file}")
    print(f"Worksheets included: Release Notes, New Releases, Frequent Changes")

if __name__ == "__main__":
    main() 