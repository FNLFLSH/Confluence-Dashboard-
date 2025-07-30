from flask import Flask, send_from_directory, render_template_string
import os

app = Flask(__name__)

# Serve static files
@app.route('/')
def index():
    """Serve the main dashboard page"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_dir, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, etc.)"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_dir, filename)

@app.route('/dashboard')
def dashboard():
    """Alternative route for the dashboard"""
    return index()

if __name__ == '__main__':
    print("🌐 Starting Web Server...")
    print("📊 Dashboard available at: http://localhost:8080")
    print("🔗 API Server should be running at: http://localhost:5000")
    print("")
    print("To start the complete system:")
    print("1. Start API server: python api_server.py")
    print("2. Start web server: python web_server.py")
    print("3. Open browser to: http://localhost:8080")
    
    app.run(debug=True, host='0.0.0.0', port=8080) 