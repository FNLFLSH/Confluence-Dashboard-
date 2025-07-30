# Confluence Report Dashboard v0

A modern, interactive web dashboard for visualizing and exploring Confluence release report data. This dashboard provides beautiful charts, filtering capabilities, and real-time data exploration.

## 🚀 Features

### 📊 Interactive Visualizations
- **Category Distribution**: Doughnut chart showing release types (Bug Fix, Enhancement, New Feature, Other)
- **Timeline Analysis**: Bar chart displaying releases over time by quarter
- **Module Activity**: Horizontal bar chart showing top modules by release count
- **Summary Statistics**: Key metrics displayed in animated cards

### 🔍 Advanced Filtering
- **Category Filter**: Filter by release type
- **Quarter Filter**: Filter by specific time periods
- **Module Filter**: Filter by specific modules
- **Search Functionality**: Real-time search across titles and descriptions
- **Reset Filters**: One-click filter reset

### 📋 Data Table
- **Pagination**: Navigate through large datasets
- **Sortable Columns**: Sort by various criteria
- **Hover Effects**: Enhanced user experience
- **Responsive Design**: Works on all screen sizes

### 🎨 Modern UI/UX
- **Gradient Background**: Beautiful visual design
- **Card-based Layout**: Clean, organized interface
- **Responsive Design**: Mobile-friendly
- **Loading States**: Smooth user experience
- **Error Handling**: Graceful error display

## 🏗️ Architecture

```
Confluence Dashboard v0
├── api_server.py          # REST API backend
├── web_server.py          # Static file server
├── dashboard.py           # Dash-based alternative
├── static/
│   ├── index.html        # Main dashboard page
│   └── dashboard.js      # Frontend JavaScript
└── data/
    └── report_confluence.json  # Your data file
```

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Option 1: Modern Web Dashboard (Recommended)

1. **Start the API Server**:
   ```bash
   python api_server.py
   ```
   This starts the REST API on `http://localhost:5000`

2. **Start the Web Server**:
   ```bash
   python web_server.py
   ```
   This serves the dashboard on `http://localhost:8080`

3. **Open your browser**:
   Navigate to `http://localhost:8080`

### Option 2: Dash-based Dashboard

For a more integrated experience with Plotly charts:

```bash
python dashboard.py
```

This starts a Dash application on `http://localhost:8050`

## 📊 Dashboard Components

### Summary Statistics
- **Total Releases**: Count of all releases
- **Active Modules**: Number of unique modules
- **Time Periods**: Number of quarters with data
- **New Releases**: Count of new module releases

### Interactive Charts

#### Category Distribution
- Visual breakdown of release types
- Color-coded categories
- Interactive legend

#### Timeline Analysis
- Releases over time by quarter
- Bar chart visualization
- Automatic sorting by date

#### Module Activity
- Top modules by release count
- Horizontal bar chart
- Configurable limit (default: top 10)

### Data Table Features
- **Pagination**: 20 items per page
- **Search**: Real-time search functionality
- **Filtering**: Multiple filter options
- **Responsive**: Adapts to screen size

## 🔧 API Endpoints

The dashboard connects to these REST API endpoints:

- `GET /api/health` - System health check
- `GET /api/summary` - Summary statistics
- `GET /api/releases` - Release data with filtering
- `GET /api/charts/category` - Category chart data
- `GET /api/charts/timeline` - Timeline chart data
- `GET /api/charts/modules` - Modules chart data
- `GET /api/filters` - Available filter options
- `GET /api/search` - Search functionality
- `GET /api/frequent-changes` - Frequent changes analysis

## 🎨 Customization

### Colors and Styling
The dashboard uses CSS custom properties for easy theming:

```css
:root {
    --primary-color: #0033A0;
    --secondary-color: #366092;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
}
```

### Chart Colors
- **Bug Fix**: Red (`#dc3545`)
- **Enhancement**: Yellow (`#ffc107`)
- **New Feature**: Green (`#28a745`)
- **Other**: Gray (`#6c757d`)

## 🔍 Usage Examples

### Filtering Data
1. Select a category from the dropdown
2. Choose a specific quarter
3. Filter by module name
4. Use the search box for text-based filtering

### Exploring Charts
- **Hover** over chart elements for details
- **Click** legend items to show/hide data
- **Zoom** and pan on interactive charts

### Data Table Navigation
- Use pagination controls at the bottom
- Search for specific terms
- Sort by clicking column headers

## 🛠️ Development

### Adding New Charts
1. Create API endpoint in `api_server.py`
2. Add chart container in `static/index.html`
3. Implement chart logic in `static/dashboard.js`

### Modifying Styles
Edit the CSS in `static/index.html` or create separate CSS files.

### Extending API
Add new endpoints to `api_server.py` following the existing pattern.

## 📱 Mobile Support

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Touch devices

## 🔒 Security Notes

- The API server runs on localhost by default
- CORS is enabled for development
- No authentication is implemented (add as needed)
- Static files are served directly

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure `api_server.py` is running
   - Check port 5000 is available
   - Verify data file exists

2. **Charts Not Loading**
   - Check browser console for errors
   - Verify API endpoints are responding
   - Ensure Chart.js is loaded

3. **Data Not Displaying**
   - Check data file format
   - Verify parsing logic
   - Check API health endpoint

### Debug Mode
Enable debug mode in the servers for detailed error messages:

```python
app.run(debug=True)
```

## 📈 Performance

- **Lazy Loading**: Charts load on demand
- **Pagination**: Large datasets handled efficiently
- **Caching**: API responses cached in browser
- **Optimized Queries**: Efficient data filtering

## 🔄 Future Enhancements

- [ ] Export functionality (PDF, Excel)
- [ ] Advanced analytics
- [ ] User authentication
- [ ] Real-time updates
- [ ] Custom chart types
- [ ] Data comparison features
- [ ] Alert system for trends
- [ ] Integration with other data sources

## 📄 License

This project is open source and available under the MIT License. 