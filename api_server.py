from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import json
import os
from src.parser_json import load_and_parse_confluence_data
from src.utils import standardize_fields, add_quarter_column
from src.excel_writer import analyze_module_changes

app = Flask(__name__)
CORS(app)

# Global variable to store parsed data
parsed_data = None

def load_data():
    """Load and parse the Confluence data"""
    global parsed_data
    try:
        # Try main data file first
        data_file = "data/report_confluence.json"
        if os.path.exists(data_file):
            print(f"Loading main data file: {data_file}")
            parsed_data = load_and_parse_confluence_data(data_file)
            parsed_data = standardize_fields(parsed_data)
            parsed_data = add_quarter_column(parsed_data)
            return True
        else:
            # Try demo data file
            demo_file = "data/demo_data.json"
            if os.path.exists(demo_file):
                print(f"Main data file not found, using demo data: {demo_file}")
                parsed_data = load_and_parse_confluence_data(demo_file)
                parsed_data = standardize_fields(parsed_data)
                parsed_data = add_quarter_column(parsed_data)
                return True
            else:
                print(f"Data files not found: {data_file} or {demo_file}")
                return False
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

# Load data on startup
data_loaded = load_data()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'data_loaded': data_loaded,
        'data_count': len(parsed_data) if parsed_data else 0
    })

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get summary statistics"""
    if not parsed_data:
        return jsonify({'error': 'No data available'}), 404
    
    df = pd.DataFrame(parsed_data)
    
    summary = {
        'total_releases': len(df),
        'total_modules': len(df['ModuleName'].dropna().unique()),
        'total_quarters': len(df['Quarter'].dropna().unique()),
        'new_releases': len(df[df.get('NewRelease', False) == True]),
        'categories': df['Category'].value_counts().to_dict(),
        'quarters': df['Quarter'].value_counts().to_dict(),
        'modules': df['ModuleName'].value_counts().head(20).to_dict()
    }
    
    return jsonify(summary)

@app.route('/api/releases', methods=['GET'])
def get_releases():
    """Get releases with optional filtering"""
    if not parsed_data:
        return jsonify({'error': 'No data available'}), 404
    
    # Get filter parameters
    category = request.args.get('category', 'all')
    quarter = request.args.get('quarter', 'all')
    module = request.args.get('module', 'all')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    df = pd.DataFrame(parsed_data)
    
    # Apply filters
    if category != "all":
        df = df[df['Category'] == category]
    if quarter != "all":
        df = df[df['Quarter'] == quarter]
    if module != "all":
        df = df[df['ModuleName'] == module]
    
    # Sort by date (most recent first)
    df = df.sort_values('Date', ascending=False)
    
    # Apply pagination
    df_paginated = df.iloc[offset:offset + limit]
    
    releases = []
    for _, row in df_paginated.iterrows():
        releases.append({
            'title': row.get('Title', ''),
            'body': row.get('Body', ''),
            'category': row.get('Category', ''),
            'module_name': row.get('ModuleName', ''),
            'date': row.get('Date', ''),
            'quarter': row.get('Quarter', ''),
            'new_release': row.get('NewRelease', False)
        })
    
    return jsonify({
        'releases': releases,
        'total': len(df),
        'limit': limit,
        'offset': offset
    })

@app.route('/api/charts/category', methods=['GET'])
def get_category_chart():
    """Get data for category distribution chart"""
    if not parsed_data:
        return jsonify({'error': 'No data available'}), 404
    
    category = request.args.get('category', 'all')
    quarter = request.args.get('quarter', 'all')
    module = request.args.get('module', 'all')
    
    df = pd.DataFrame(parsed_data)
    
    # Apply filters
    if category != "all":
        df = df[df['Category'] == category]
    if quarter != "all":
        df = df[df['Quarter'] == quarter]
    if module != "all":
        df = df[df['ModuleName'] == module]
    
    category_counts = df['Category'].value_counts()
    
    return jsonify({
        'labels': category_counts.index.tolist(),
        'values': category_counts.values.tolist()
    })

@app.route('/api/charts/timeline', methods=['GET'])
def get_timeline_chart():
    """Get data for timeline chart"""
    if not parsed_data:
        return jsonify({'error': 'No data available'}), 404
    
    category = request.args.get('category', 'all')
    quarter = request.args.get('quarter', 'all')
    module = request.args.get('module', 'all')
    
    df = pd.DataFrame(parsed_data)
    
    # Apply filters
    if category != "all":
        df = df[df['Category'] == category]
    if quarter != "all":
        df = df[df['Quarter'] == quarter]
    if module != "all":
        df = df[df['ModuleName'] == module]
    
    quarter_counts = df['Quarter'].value_counts().sort_index()
    
    return jsonify({
        'quarters': quarter_counts.index.tolist(),
        'counts': quarter_counts.values.tolist()
    })

@app.route('/api/charts/modules', methods=['GET'])
def get_modules_chart():
    """Get data for modules activity chart"""
    if not parsed_data:
        return jsonify({'error': 'No data available'}), 404
    
    category = request.args.get('category', 'all')
    quarter = request.args.get('quarter', 'all')
    module = request.args.get('module', 'all')
    limit = int(request.args.get('limit', 10))
    
    df = pd.DataFrame(parsed_data)
    
    # Apply filters
    if category != "all":
        df = df[df['Category'] == category]
    if quarter != "all":
        df = df[df['Quarter'] == quarter]
    if module != "all":
        df = df[df['ModuleName'] == module]
    
    module_counts = df['ModuleName'].value_counts().head(limit)
    
    return jsonify({
        'modules': module_counts.index.tolist(),
        'counts': module_counts.values.tolist()
    })

@app.route('/api/frequent-changes', methods=['GET'])
def get_frequent_changes():
    """Get frequent changes analysis"""
    if not parsed_data:
        return jsonify({'error': 'No data available'}), 404
    
    frequent_quarter_changes, frequent_year_changes = analyze_module_changes(parsed_data)
    
    return jsonify({
        'quarterly_changes': frequent_quarter_changes,
        'yearly_changes': frequent_year_changes
    })

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get available filter options"""
    if not parsed_data:
        return jsonify({'error': 'No data available'}), 404
    
    df = pd.DataFrame(parsed_data)
    
    filters = {
        'categories': sorted(df['Category'].unique().tolist()),
        'quarters': sorted(df['Quarter'].dropna().unique().tolist()),
        'modules': sorted(df['ModuleName'].dropna().unique().tolist())
    }
    
    return jsonify(filters)

@app.route('/api/search', methods=['GET'])
def search_releases():
    """Search releases by title or body"""
    if not parsed_data:
        return jsonify({'error': 'No data available'}), 404
    
    query = request.args.get('q', '').lower()
    limit = int(request.args.get('limit', 50))
    
    if not query:
        return jsonify({'releases': [], 'total': 0})
    
    df = pd.DataFrame(parsed_data)
    
    # Search in title and body
    mask = (
        df['Title'].str.lower().str.contains(query, na=False) |
        df['Body'].str.lower().str.contains(query, na=False)
    )
    
    df_filtered = df[mask].head(limit)
    
    releases = []
    for _, row in df_filtered.iterrows():
        releases.append({
            'title': row.get('Title', ''),
            'body': row.get('Body', ''),
            'category': row.get('Category', ''),
            'module_name': row.get('ModuleName', ''),
            'date': row.get('Date', ''),
            'quarter': row.get('Quarter', '')
        })
    
    return jsonify({
        'releases': releases,
        'total': len(df[mask]),
        'query': query
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 