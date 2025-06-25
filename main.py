import os
import sys
import argparse
from src.parser_json import load_and_parse_confluence_data
from src.excel_writer import export_grouped_by_quarter, export_frequent_changes_report, create_new_releases_report

def main():
    parser = argparse.ArgumentParser(description='Generate Excel reports from Confluence HTML data')
    parser.add_argument('--input-file', required=True, help='Input JSON file path')
    parser.add_argument('--output-file', required=True, help='Output Excel file path for main report')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Loading data from: {args.input_file}")
    data = load_and_parse_confluence_data(args.input_file)
    print(f"Parsed {len(data)} releases")
    
    # Generate main release notes report
    print(f"Generating main Excel report: {args.output_file}")
    export_grouped_by_quarter(data, args.output_file)
    
    # Generate frequent changes report
    frequent_output = args.output_file.replace('.xlsx', '_frequent_changes.xlsx')
    print(f"Generating frequent changes report: {frequent_output}")
    export_frequent_changes_report(data, frequent_output)
    
    # Generate new releases report
    new_releases_output = args.output_file.replace('.xlsx', '_new_releases.xlsx')
    print(f"Generating new releases report: {new_releases_output}")
    create_new_releases_report(data, new_releases_output)
    
    print(f"All three reports generated successfully!")
    print(f"1. Main report: {args.output_file}")
    print(f"2. Frequent changes report: {frequent_output}")
    print(f"3. New releases report: {new_releases_output}")

if __name__ == "__main__":
    main() 