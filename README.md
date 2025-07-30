# 🚀 Elevance Confluence Report Dashboard

A modern, interactive web dashboard for visualizing and analyzing Confluence release reports with Elevance branding.

## ✨ Features

### 📊 **Interactive Visualizations**
- **Category Distribution**: Doughnut chart showing release types (Bug Fix, Enhancement, New Feature)
- **Timeline Analysis**: Bar chart displaying releases over time by quarters
- **Module Activity**: Top modules ranked by release frequency
- **Real-time Updates**: Charts update dynamically based on filter selections

### 🔍 **Advanced Filtering & Search**
- **Category Filter**: Filter by release type (Bug Fix, Enhancement, New Feature)
- **Quarter Filter**: Filter by specific time periods
- **Module Filter**: Filter by specific modules
- **Text Search**: Search across all release titles and descriptions
- **Reset Filters**: One-click filter reset functionality

### 📋 **Data Table**
- **Full-width Display**: Responsive table with proper column spacing
- **Pagination**: Handle large datasets with 20 records per page
- **Hover Effects**: Visual feedback for better user experience
- **Category Badges**: Color-coded badges for easy identification

### 🎨 **Modern UI/UX**
- **Elevance Branding**: Professional blue/white/black color scheme
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Card-based Layout**: Clean, organized interface with proper spacing
- **Loading States**: Smooth loading animations and error handling

## 🏗️ Architecture

### **Backend (Flask API)**
- **RESTful API**: Clean endpoints for data access
- **Data Processing**: Efficient parsing of Confluence HTML data
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Robust error handling and logging

### **Frontend (HTML/CSS/JavaScript)**
- **Bootstrap 5**: Modern, responsive framework
- **Chart.js**: Interactive, animated charts
- **Font Awesome**: Professional icons throughout
- **Custom CSS**: Elevance-branded styling

### **Data Flow**
```
Confluence HTML → Parser → Structured Data → API → Frontend → Interactive Dashboard
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- pip3

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/FNLFLSH/Confluence-Dashboard-.git
   cd Confluence-Dashboard-
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Prepare your data**
   - Place your Confluence HTML data in `data/report_confluence.json`
   - Or use the included demo data for testing

4. **Start the dashboard**
   ```bash
   python3 start_dashboard.py
   ```

5. **Access the dashboard**
   - Open your browser to: http://localhost:8080
   - API server runs on: http://localhost:5001

## 📁 Project Structure

```
Confluence-Dashboard-/
├── data/
│   ├── report_confluence.json    # Main data file
│   └── demo_data.json           # Demo data for testing
├── src/
│   ├── parser_json.py           # HTML parsing logic
│   ├── excel_writer.py          # Excel export functionality
│   └── utils.py                 # Data transformation utilities
├── static/
│   ├── index.html               # Main dashboard page
│   └── dashboard.js             # Frontend JavaScript
├── api_server.py                # Flask REST API
├── web_server.py                # Static file server
├── start_dashboard.py           # Startup script
├── dashboard.py                 # Alternative Dash app
├── main.py                      # Original Excel generator
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## 🔧 API Endpoints

### **Health Check**
- `GET /api/health` - Server status

### **Data Endpoints**
- `GET /api/summary` - Dashboard summary statistics
- `GET /api/releases` - Filtered release data with pagination
- `GET /api/filters` - Available filter options

### **Chart Data**
- `GET /api/charts/category` - Category distribution data
- `GET /api/charts/timeline` - Timeline chart data
- `GET /api/charts/modules` - Module activity data
- `GET /api/frequent-changes` - Most frequently changed modules

### **Search & Filtering**
- `GET /api/search` - Text search functionality

## 🎨 Customization

### **Branding**
The dashboard uses Elevance brand colors:
- Primary Blue: `#0033A0`
- Secondary Blue: `#366092`
- Accent Blue: `#002366`
- Light Blue: `#E6F3FF`

### **Styling**
- Modify `static/index.html` for layout changes
- Update CSS variables in the `:root` selector for color changes
- Customize chart colors in `static/dashboard.js`

### **Data Processing**
- Extend `src/parser_json.py` for additional data parsing
- Modify `src/utils.py` for custom data transformations
- Update `api_server.py` for new API endpoints

## 🔍 Troubleshooting

### **Common Issues**

1. **Port conflicts**
   ```bash
   # Check what's using the ports
   lsof -i :5001
   lsof -i :8080
   
   # Kill processes if needed
   kill -9 <PID>
   ```

2. **Data loading issues**
   - Ensure `data/report_confluence.json` exists
   - Check file permissions
   - Verify JSON format is correct

3. **Dependency issues**
   ```bash
   # Reinstall dependencies
   pip3 uninstall -r requirements.txt
   pip3 install -r requirements.txt
   ```

### **Development Mode**
- API server runs in debug mode with auto-reload
- Web server includes hot-reloading for static files
- Check terminal output for detailed error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Bootstrap 5** for responsive design framework
- **Chart.js** for interactive visualizations
- **Font Awesome** for professional icons
- **Flask** for the REST API backend

---

**Built with ❤️ for Elevance** 