#!/usr/bin/env python3
"""
Honey Duo Wealth Secure Web Interface
Professional version with authentication for hdw.honey-duo.com
"""

from flask import Flask, render_template, request, jsonify, make_response
from functools import wraps
import yaml
import subprocess
import os
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'hdw-honey-duo-2025-secure'

# Authentication - CHANGE THESE CREDENTIALS!
VALID_USERS = {
    'hdw': 'HoneyDuo2025!',
    'admin': 'AdminPass123!'
}

def check_auth(username, password):
    """Check if username/password is valid"""
    return username in VALID_USERS and VALID_USERS[username] == password

def authenticate():
    """Send 401 response with authentication request"""
    return make_response(
        '🔐 HDW Access Required\nLogin required for Honey Duo Wealth Management',
        401,
        {'WWW-Authenticate': 'Basic realm="HDW Management Interface"'}
    )

def requires_auth(f):
    """Decorator for authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Project configuration
PROJECT_ROOT = Path.home() / "hdw_setup" / "honey_duo_wealth"

def load_tasks():
    """Load tasks from tasks.yaml"""
    tasks_file = PROJECT_ROOT / "tasks.yaml"
    if not tasks_file.exists():
        return []
    
    try:
        with open(tasks_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('tasks', [])
    except:
        return []

def run_cli_command(command):
    """Run CLI command and return result"""
    try:
        cmd = f"python3 {PROJECT_ROOT}/cli/hdw-task.py {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_ROOT)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

@app.route('/')
@requires_auth
def dashboard():
    """Main dashboard"""
    tasks = load_tasks()
    
    # Calculate statistics
    status_counts = {}
    for task in tasks:
        status = task.get('status', 'pending')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Get recent tasks
    recent_tasks = sorted([t for t in tasks if t.get('updated')], 
                         key=lambda x: x.get('updated', ''), reverse=True)[:10]
    
    # Professional HTML interface
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🍯 Honey Duo Wealth - Project Management</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d30 100%);
                color: #ffffff; 
                line-height: 1.6;
                min-height: 100vh;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                background: linear-gradient(135deg, #2b2b2b 0%, #1a1a1a 100%);
                padding: 30px 0; 
                border-bottom: 3px solid #ffd700;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            }}
            .header h1 {{ 
                color: #ffd700; 
                text-align: center; 
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }}
            .domain-badge {{ 
                text-align: center; 
                margin-top: 10px;
                color: #888;
                font-size: 14px;
            }}
            .nav {{ 
                display: flex; 
                justify-content: center; 
                gap: 20px; 
                margin-top: 20px; 
            }}
            .nav a {{ 
                color: #ffffff; 
                text-decoration: none; 
                padding: 12px 24px;
                background: linear-gradient(135deg, #333 0%, #555 100%);
                border-radius: 8px; 
                transition: all 0.3s ease;
                border: 1px solid transparent;
            }}
            .nav a:hover, .nav a.active {{ 
                background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
                color: #000; 
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(255,215,0,0.3);
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin: 30px 0; 
            }}
            .stat-box {{ 
                padding: 25px; 
                border-radius: 15px; 
                text-align: center; 
                color: white; 
                font-weight: bold;
                position: relative;
                overflow: hidden;
                transform: perspective(1000px) rotateX(0);
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .stat-box:hover {{
                transform: perspective(1000px) rotateX(5deg) translateY(-5px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
            .stat-box::before {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%);
                z-index: 1;
            }}
            .stat-content {{ position: relative; z-index: 2; }}
            .stat-number {{ font-size: 3em; margin-bottom: 10px; }}
            .stat-label {{ font-size: 1.1em; opacity: 0.9; }}
            .stat-pending {{ background: linear-gradient(135deg, #ff8c00 0%, #ff6b35 100%); }}
            .stat-in-progress {{ background: linear-gradient(135deg, #0066cc 0%, #004499 100%); }}
            .stat-completed {{ background: linear-gradient(135deg, #00cc00 0%, #009900 100%); }}
            .stat-blocked {{ background: linear-gradient(135deg, #cc0000 0%, #990000 100%); }}
            .content-section {{ 
                background: rgba(43, 43, 43, 0.8);
                border-radius: 15px; 
                padding: 25px; 
                margin: 20px 0;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            }}
            .section-title {{ 
                color: #ffd700; 
                margin-bottom: 20px; 
                font-size: 1.5em;
                border-bottom: 2px solid #ffd700;
                padding-bottom: 10px;
            }}
            .task-item {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                padding: 15px; 
                margin: 10px 0; 
                background: rgba(51, 51, 51, 0.8);
                border-radius: 10px;
                border-left: 4px solid #ffd700;
                transition: all 0.3s ease;
            }}
            .task-item:hover {{
                background: rgba(51, 51, 51, 1);
                transform: translateX(5px);
            }}
            .task-info {{ flex: 1; }}
            .task-title {{ font-weight: bold; margin-bottom: 5px; }}
            .task-meta {{ color: #ccc; font-size: 0.9em; }}
            .task-actions {{ display: flex; gap: 10px; }}
            .btn {{ 
                padding: 8px 16px; 
                border: none; 
                border-radius: 6px;
                cursor: pointer; 
                font-weight: bold; 
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }}
            .btn:hover {{ 
                transform: translateY(-2px); 
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }}
            .btn-start {{ background: linear-gradient(135deg, #00cc00 0%, #009900 100%); color: white; }}
            .btn-complete {{ background: linear-gradient(135deg, #0066cc 0%, #004499 100%); color: white; }}
            .btn-block {{ background: linear-gradient(135deg, #cc0000 0%, #990000 100%); color: white; }}
            .btn-report {{ background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); color: black; }}
            .time-display {{ 
                text-align: center; 
                color: #aaa; 
                font-size: 14px; 
                margin-top: 15px; 
            }}
            .report-section {{
                background: #f8f8f8; 
                color: #000; 
                padding: 20px; 
                border-radius: 10px;
                font-family: 'Courier New', monospace; 
                white-space: pre-wrap;
                min-height: 200px; 
                margin: 20px 0;
                border: 2px solid #ddd;
            }}
            .form-group {{ margin: 15px 0; }}
            .form-group label {{ 
                display: block; 
                margin-bottom: 8px; 
                color: #ffd700; 
                font-weight: bold;
            }}
            .form-group select, .form-group textarea {{
                width: 100%; 
                padding: 12px; 
                border: 1px solid #555; 
                border-radius: 8px;
                background: #333; 
                color: #fff;
                font-size: 14px;
            }}
            .success {{ color: #00ff00; font-weight: bold; }}
            .error {{ color: #ff6b6b; font-weight: bold; }}
            @media (max-width: 768px) {{
                .task-item {{ flex-direction: column; align-items: flex-start; }}
                .task-actions {{ margin-top: 10px; }}
                .nav {{ flex-wrap: wrap; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1>🍯 Honey Duo Wealth</h1>
                <div class="domain-badge">🌐 Professional Project Management • hdw.honey-duo.com</div>
                <div class="nav">
                    <a href="/" class="active">📊 Dashboard</a>
                    <a href="/tasks">📋 Tasks</a>
                    <a href="/reports">📈 Reports</a>
                    <a href="/help">❓ Help</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="time-display">{datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}</div>
            
            <div class="content-section">
                <h2 class="section-title">📊 Project Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-box stat-pending">
                        <div class="stat-content">
                            <div class="stat-number">{status_counts.get('pending', 0)}</div>
                            <div class="stat-label">⏳ Pending Tasks</div>
                        </div>
                    </div>
                    <div class="stat-box stat-in-progress">
                        <div class="stat-content">
                            <div class="stat-number">{status_counts.get('in-progress', 0)}</div>
                            <div class="stat-label">🔄 In Progress</div>
                        </div>
                    </div>
                    <div class="stat-box stat-completed">
                        <div class="stat-content">
                            <div class="stat-number">{status_counts.get('completed', 0)}</div>
                            <div class="stat-label">✅ Completed</div>
                        </div>
                    </div>
                    <div class="stat-box stat-blocked">
                        <div class="stat-content">
                            <div class="stat-number">{status_counts.get('blocked', 0)}</div>
                            <div class="stat-label">🚫 Blocked</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">🔄 Recent Activity</h2>
    """
    
    if recent_tasks:
        for task in recent_tasks:
            status_icon = {'pending': '⏳', 'in-progress': '🔄', 'completed': '✅', 'blocked': '🚫'}.get(task.get('status'), '❓')
            updated = task.get('updated', '')
            if updated:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    time_str = dt.strftime('%m/%d %I:%M%p')
                except:
                    time_str = updated[:10]
            else:
                time_str = 'Never'
            
            html += f"""
                <div class="task-item">
                    <div class="task-info">
                        <div class="task-title">{status_icon} {task['id']}</div>
                        <div class="task-meta">{task.get('description', '')[:80]}{'...' if len(task.get('description', '')) > 80 else ''}</div>
                        <div class="task-meta">Updated: {time_str} • Status: {task.get('status', 'pending')}</div>
                    </div>
                    <div class="task-actions">
            """
            
            if task.get('status') == 'pending':
                html += f'<button class="btn btn-start" onclick="startTask(\'{task["id"]}\')">🚀 Start</button>'
            elif task.get('status') == 'in-progress':
                html += f'<button class="btn btn-complete" onclick="completeTask(\'{task["id"]}\')">✅ Complete</button>'
            
            html += f'<a href="/tasks" class="btn btn-report">📋 Manage</a>'
            html += "</div></div>"
    else:
        html += '<p style="text-align: center; color: #888; padding: 40px;">No recent activity</p>'
    
    html += """
            </div>
        </div>
        
        <script>
        function startTask(taskId) {
            fetch('/api/start/' + taskId, {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                alert(data.success ? 
                    `Task '${taskId}' started successfully!\\nContext file created for Claude.` : 
                    `Error: ${data.error}`);
                if (data.success) location.reload();
            });
        }
        
        function completeTask(taskId) {
            const message = prompt('Commit message (optional):');
            fetch('/api/complete/' + taskId, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message || ''})
            })
            .then(response => response.json())
            .then(data => {
                alert(data.success ? 
                    `Task '${taskId}' completed and committed!` : 
                    `Error: ${data.error}`);
                if (data.success) location.reload();
            });
        }
        
        // Auto-refresh every 60 seconds
        setTimeout(() => location.reload(), 60000);
        </script>
    </body>
    </html>
    """
    
    return html

@app.route('/tasks')
@requires_auth
def tasks():
    """Tasks management page"""
    tasks = load_tasks()
    
    # Create tasks page HTML
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📋 Tasks - HDW Management</title>
        <link rel="stylesheet" href="/static/styles.css">
    </head>
    <body>
        <!-- Include navigation -->
        <div class="container">
            <h1>📋 Task Management</h1>
            <!-- Task list with management controls -->
        </div>
    </body>
    </html>
    """
    return html

@app.route('/reports')
@requires_auth
def reports():
    """Reports generation page"""
    tasks = load_tasks()
    reportable_tasks = [t for t in tasks if t.get('status') in ['completed', 'blocked', 'in-progress']]
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>📈 Reports - HDW Management</title>
        <style>
            body {{ font-family: Arial; background: #1a1a1a; color: white; margin: 20px; }}
            .form-group {{ margin: 15px 0; }}
            .form-group label {{ display: block; margin-bottom: 5px; color: #ffd700; }}
            .form-group select, .form-group textarea {{
                width: 100%; padding: 10px; border: 1px solid #555; border-radius: 5px;
                background: #333; color: #fff;
            }}
            .report-area {{ 
                background: #f8f8f8; color: #000; padding: 20px; border-radius: 10px;
                font-family: 'Courier New', monospace; white-space: pre-wrap;
                min-height: 200px; margin: 20px 0;
            }}
            button {{ padding: 10px 15px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }}
            .btn-report {{ background: #ffd700; color: black; }}
        </style>
    </head>
    <body>
        <h1>📈 ChatGPT Status Reports</h1>
        
        <div class="form-group">
            <label for="task-select">Select Task:</label>
            <select id="task-select">
    """
    
    for task in reportable_tasks:
        html += f'<option value="{task["id"]}">{task["id"]} - {task.get("description", "")[:50]}</option>'
    
    html += """
            </select>
        </div>
        
        <div class="form-group">
            <label for="summary-input">Custom Summary (optional):</label>
            <textarea id="summary-input" rows="3" placeholder="Leave empty for auto-generated summary"></textarea>
        </div>
        
        <button class="btn-report" onclick="generateReport()">📈 Generate Report</button>
        <button onclick="copyReport()" style="background: #666; color: white;">📋 Copy to Clipboard</button>
        
        <div id="report-output" class="report-area">
            Click "Generate Report" to create a ChatGPT status update...
        </div>
        
        <div id="status-message"></div>
        
        <script>
        function generateReport() {
            const taskId = document.getElementById('task-select').value;
            const summary = document.getElementById('summary-input').value;
            
            fetch('/api/generate_report', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: taskId, summary: summary})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('report-output').textContent = data.report;
                    document.getElementById('status-message').innerHTML = 
                        '<span style="color: #00cc00;">✅ Report saved as: ' + data.filename + '</span>';
                } else {
                    document.getElementById('status-message').innerHTML = 
                        '<span style="color: #cc0000;">❌ Error: ' + data.error + '</span>';
                }
            });
        }
        
        function copyReport() {
            const reportText = document.getElementById('report-output').textContent;
            navigator.clipboard.writeText(reportText).then(() => {
                document.getElementById('status-message').innerHTML = 
                    '<span style="color: #00cc00;">📋 Report copied to clipboard!</span>';
            });
        }
        </script>
    </body>
    </html>
    """
    
    return html

# API endpoints
@app.route('/api/start/<task_id>', methods=['POST'])
@requires_auth
def start_task(task_id):
    result = run_cli_command(f"start {task_id}")
    return jsonify(result)

@app.route('/api/complete/<task_id>', methods=['POST'])
@requires_auth
def complete_task(task_id):
    data = request.json or {}
    message = data.get('message', '')
    command = f'commit {task_id} --message "{message}"' if message else f"commit {task_id}"
    result = run_cli_command(command)
    return jsonify(result)

@app.route('/api/generate_report', methods=['POST'])
@requires_auth
def generate_report():
    data = request.json
    task_id = data.get('task_id')
    custom_summary = data.get('summary', '')
    
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({"success": False, "error": f"Task '{task_id}' not found"})
    
    summary = custom_summary if custom_summary else f"Implemented {task.get('description', 'task requirements')}"
    
    # Get git artifacts
    try:
        result = subprocess.run(
            ["git", "show", "--name-only", "--pretty=format:", "HEAD"],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        recent_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        artifacts = ", ".join(recent_files) if recent_files else task.get("output", "No artifacts")
    except:
        artifacts = task.get("output", "No artifacts")
    
    status = task.get('status', 'pending').title()
    report = f"""Task: {task_id}
Status: {status}
Summary: "{summary}"
Artifacts: {artifacts}"""
    
    # Save report
    timestamp = datetime.now().strftime('%m%d_%H%M')
    reports_dir = PROJECT_ROOT / "chatgpt_reports"
    reports_dir.mkdir(exist_ok=True)
    
    filename = f"ChatGPT_Update_{task_id}_{timestamp}.txt"
    report_file = reports_dir / filename
    
    with open(report_file, 'w') as f:
        f.write(f"# ChatGPT Status Update\\n# Generated: {datetime.now().strftime('%A %B %d, %Y at %I:%M %p')}\\n\\n{report}")
    
    return jsonify({"success": True, "report": report, "filename": filename})

@app.route('/help')
@requires_auth
def help_page():
    return "<h1>Help coming soon...</h1>"

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "domain": "hdw.honey-duo.com"})

if __name__ == "__main__":
    print("🌐 HDW Secure Web Interface Starting...")
    print("🔐 Access: https://hdw.honey-duo.com")
    print("🔑 Login: hdw / HoneyDuo2025!")
    app.run(host='0.0.0.0', port=5000, debug=False)
