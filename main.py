import os
from src.parser_json import load_and_parse_confluence_data
from src.excel_writer import export_grouped_by_quarter

def main():
    input_path = os.path.join('data', 'report_confluence (1).json')
    output_path = os.path.join('output', 'release_notes_output.xlsx')
    data = load_and_parse_confluence_data(input_path)
    export_grouped_by_quarter(data, output_path)
    print(f"Excel report generated: {output_path}")
    print(f"Total releases processed: {len(data)}")

if __name__ == "__main__":
    main() 