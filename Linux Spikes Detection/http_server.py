import http.server
import socketserver
import os
import re
import json
from datetime import datetime

# --- CONFIGURATION ---
PORT = 8080
LOG_FILE_PATH = "/home/ec2-user/spike_detector.log"
DIAGNOSTICS_DIR = "/home/ec2-user/diagnostics"
LOAD_THRESHOLD = 2.0
# The number of log entries to display on the dashboard
MAX_LOG_ENTRIES = 20

# --- DATA PROCESSING LOGIC ---

def parse_log_data(log_path):
    """Reads the log file, extracts load averages and spike events."""
    parsed_data = []
    spike_count = 0
    load_averages = []
    
    # Regex to capture the core log data: Timestamp, 5-min Load Avg, and event
    # Group 1: Timestamp | Group 2: Load Avg | Group 3: Event message
    log_pattern = re.compile(
        r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] Current 5-minute Load Average: (\d+\.\d+) \(Threshold: \d+\.\d+\)\n"
        r".*?\n"
        r".*?(\[.*?\] (?:Threshold exceeded|Load is within acceptable limits))"
    , re.MULTILINE | re.DOTALL)

    try:
        with open(log_path, 'r') as f:
            # Read all content and reverse it to process recent events first
            content = f.read()
            
            # Find all matches in the content
            matches = log_pattern.findall(content)
            
            # Process in reverse order to get the most recent logs first
            for timestamp_str, load_avg_str, event_str in reversed(matches):
                load_avg = float(load_avg_str)
                is_spike = load_avg > LOAD_THRESHOLD
                
                if is_spike:
                    spike_count += 1
                
                # Clean up the event string
                status = event_str.split('] ')[1].split('.')[0]
                
                parsed_data.append({
                    'timestamp': timestamp_str,
                    'load_avg': f"{load_avg:.2f}",
                    'status': status,
                    'class': 'bg-red-200 text-red-800' if is_spike else 'bg-green-200 text-green-800'
                })
                
                # Keep a list of all load averages for summary display
                load_averages.append(load_avg)
                
    except FileNotFoundError:
        return {'status': 'Error: Log file not found.', 'entries': [], 'summary': {'last_load': 'N/A', 'spike_count': 0, 'avg_load': 'N/A'}}
    except Exception as e:
        return {'status': f'Error reading log: {e}', 'entries': [], 'summary': {'last_load': 'N/A', 'spike_count': 0, 'avg_load': 'N/A'}}

    # Calculate Summary Statistics
    if load_averages:
        avg_load = sum(load_averages) / len(load_averages)
        last_load = parsed_data[0]['load_avg']
    else:
        avg_load = 0
        last_load = 'N/A'

    # Count diagnostic archives
    archive_files = [f for f in os.listdir(DIAGNOSTICS_DIR) if f.endswith('.tar.gz')]
    
    summary = {
        'last_load': last_load,
        'spike_count': len(archive_files),
        'avg_load': f"{avg_load:.2f}",
        'threshold': LOAD_THRESHOLD,
        'last_run': parsed_data[0]['timestamp'] if parsed_data else 'N/A'
    }

    return {'status': 'OK', 'entries': parsed_data[:MAX_LOG_ENTRIES], 'summary': summary}

# --- HTML TEMPLATE GENERATION ---

def generate_html(data):
    """Generates the full HTML content using Tailwind CSS."""
    
    summary = data['summary']
    entries_html = ""
    
    # Generate HTML rows for the log entries
    for entry in data['entries']:
        # Determine the status pill color based on the class
        status_pill_class = 'bg-red-100 text-red-700' if 'red' in entry['class'] else 'bg-green-100 text-green-700'
        
        entries_html += f"""
        <tr class="bg-white border-b hover:bg-gray-50">
            <td class="px-6 py-4 font-mono text-sm text-gray-900">{entry['timestamp']}</td>
            <td class="px-6 py-4 text-center font-bold">{entry['load_avg']}</td>
            <td class="px-6 py-4 text-center">
                <span class="inline-flex items-center px-3 py-0.5 rounded-full text-xs font-medium {status_pill_class}">
                    {entry['status']}
                </span>
            </td>
        </tr>
        """
    
    # Determine overall status indicator based on last run
    last_load_float = float(summary['last_load']) if summary['last_load'] != 'N/A' else 0
    main_status_class = "bg-red-600" if last_load_float >= summary['threshold'] else "bg-green-600"
    main_status_text = "SPIKE DETECTED" if last_load_float >= summary['threshold'] else "LOAD OK"

    # Main HTML structure
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Load Spike Detector Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f7f9fc; }}
        .card {{ background-color: white; border-radius: 1rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
    </style>
</head>
<body class="p-4 sm:p-8">
    <div class="max-w-6xl mx-auto">
        <header class="mb-8 p-6 card">
            <h1 class="text-4xl font-extrabold text-gray-900 flex items-center">
                <svg class="w-8 h-8 mr-3 {main_status_class} p-1 rounded-full text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm-1-8V7a1 1 0 112 0v3h2a1 1 0 110 2h-2v2a1 1 0 11-2 0v-2H7a1 1 0 110-2h2z" clip-rule="evenodd" />
                </svg>
                Load Spike Detector Dashboard
            </h1>
            <p class="mt-2 text-lg text-gray-600">Real-time status of the automated diagnostic system.</p>
        </header>

        <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <!-- Metric Card: Current Load -->
            <div class="card p-5 border-l-4 border-l-orange-500">
                <p class="text-sm font-medium text-gray-500">Last Recorded 5-min Load</p>
                <p class="mt-1 text-3xl font-bold {main_status_class.replace('bg-', 'text-')}">{summary['last_load']}</p>
            </div>
            <!-- Metric Card: Threshold -->
            <div class="card p-5 border-l-4 border-l-blue-500">
                <p class="text-sm font-medium text-gray-500">Threshold for Capture</p>
                <p class="mt-1 text-3xl font-bold text-blue-600">{summary['threshold']}</p>
            </div>
            <!-- Metric Card: Archive Count -->
            <div class="card p-5 border-l-4 border-l-purple-500">
                <p class="text-sm font-medium text-gray-500">Total Diagnostic Archives</p>
                <p class="mt-1 text-3xl font-bold text-purple-600">{summary['spike_count']}</p>
            </div>
            <!-- Metric Card: Last Run Time -->
            <div class="card p-5 border-l-4 border-l-gray-500">
                <p class="text-sm font-medium text-gray-500">Last Check Time</p>
                <p class="mt-1 text-xl font-bold text-gray-600">{summary['last_run'].split(' ')[1] if summary['last_run'] != 'N/A' else 'N/A'}</p>
            </div>
        </section>

        <!-- Log History Section -->
        <section class="card p-6">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4">
                Recent Activity Log ({MAX_LOG_ENTRIES} Entries)
            </h2>
            <div class="overflow-x-auto relative rounded-lg">
                <table class="w-full text-sm text-left text-gray-500">
                    <thead class="text-xs text-gray-700 uppercase bg-gray-50">
                        <tr>
                            <th scope="col" class="py-3 px-6">Timestamp</th>
                            <th scope="col" class="py-3 px-6 text-center">Load Average</th>
                            <th scope="col" class="py-3 px-6 text-center">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {entries_html}
                    </tbody>
                </table>
            </div>
            <p class="mt-4 text-xs text-gray-500">
                Showing the most recent {MAX_LOG_ENTRIES} cron job executions from {LOG_FILE_PATH}.
            </p>
        </section>

        <!-- Instructions Section -->
        <section class="mt-8 p-6 card bg-yellow-50 border-t-4 border-yellow-300">
            <h3 class="text-lg font-bold text-yellow-800">Deployment and Access Instructions:</h3>
            <ul class="mt-2 list-disc list-inside text-sm text-yellow-700">
                <li>Make sure your EC2 Security Group allows inbound traffic on **Port {PORT}**.</li>
                <li>Run this script using: <code class="bg-yellow-100 p-0.5 rounded">python3 dashboard_server.py</code></li>
                <li>Access the dashboard in your browser using: <code class="bg-yellow-100 p-0.5 rounded">http://&lt;Your-EC2-Public-IP&gt;:{PORT}</code></li>
            </ul>
        </section>
    </div>
</body>
</html>
    """
    return html_content

# --- WEB SERVER ---

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve the dynamic HTML dashboard."""
    def do_GET(self):
        """Handles GET requests by generating and serving the dashboard."""
        
        # 1. Process the log file
        log_data = parse_log_data(LOG_FILE_PATH)
        
        # 2. Generate HTML
        html_output = generate_html(log_data)
        
        # 3. Send response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(html_output.encode('utf-8'))))
        self.end_headers()
        
        # 4. Write the HTML content to the socket
        self.wfile.write(html_output.encode('utf-8'))


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    
    # Check if the log file exists before starting
    if not os.path.exists(LOG_FILE_PATH):
        print(f"CRITICAL ERROR: Log file not found at {LOG_FILE_PATH}")
        print("Please ensure your cron job is logging to this path or update the LOG_FILE_PATH variable.")
    
    # Check if the diagnostics directory exists
    if not os.path.exists(DIAGNOSTICS_DIR):
        print(f"WARNING: Diagnostics directory not found at {DIAGNOSTICS_DIR}")
        print("Creating the directory now.")
        try:
            os.makedirs(DIAGNOSTICS_DIR)
        except OSError as e:
            print(f"ERROR: Could not create directory: {e}")
            
    
    print("------------------------------------------------------------------")
    print(f"Starting Load Spike Dashboard Server on port {PORT}...")
    print(f"Access the dashboard at: http://<Your-EC2-Public-IP>:{PORT}")
    print(f"Monitoring log file: {LOG_FILE_PATH}")
    print("Press Ctrl+C to stop the server.")
    print("------------------------------------------------------------------")
    
    # Start the server
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            httpd.serve_forever()
    except PermissionError:
        print(f"\nERROR: Permission denied. You might need to use 'sudo' to run on port {PORT} if it's reserved.")
    except Exception as e:
        print(f"\nSERVER STOPPED: An unexpected error occurred: {e}")