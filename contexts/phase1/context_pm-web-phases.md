# Context for Task: pm-web-phases

**Phase:** 1 - Project Management System
**Description:** Update web UI to show phase-based progress

**Expected Output:** hdw_complete.py with phase views

## Context Documentation:

=== hdw_complete.py ===
#!/usr/bin/env python3
"""
Honey Duo Wealth Complete Management Interface
Full functionality for task management, reports, and project control
"""

from flask import Flask, request, jsonify, make_response, redirect, url_for
from functools import wraps
import yaml
import subprocess
import os
from pathlib import Path
import datetime
import json

app = Flask(__name__)
app.secret_key = 'hdw-honey-duo-2025-secure'

# Authentication
VALID_USERS = {
    'hdw': 'HoneyDuo2025!',
    'admin': 'AdminPass123!'
}

def check_auth(username, password):
    return username in VALID_USERS and VALID_USERS[username] == password

def authenticate():
    return make_response(
        '🔐 HDW Access Required\nLogin required for Honey Duo Wealth Management',
        401,
        {'WWW-Authenticate': 'Basic realm="HDW Management Interface"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

PROJECT_ROOT = Path.home() / "hdw_setup" / "honey_duo_wealth"

def load_tasks():
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

def get_base_html(title, active_page="dashboard"):
    """Get base HTML template"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - HDW Management</title>
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
                margin-bottom: 10px;
            }}
            .domain-badge {{ 
                text-align: center; 
                color: #888;
                font-size: 14px;
                margin-bottom: 20px;
            }}
            .nav {{ 
                display: flex; 
                justify-content: center; 
                gap: 20px; 
                flex-wrap: wrap;
            }}
            .nav a {{ 
                color: #ffffff; 
                text-decoration: none; 
                padding: 12px 24px;
                background: linear-gradient(135deg, #333 0%, #555 100%);
                border-radius: 8px; 
                transition: all 0.3s ease;
                border: 1px solid transparent;
                font-weight: 500;
            }}
            .nav a:hover, .nav a.active {{ 
                background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
                color: #000; 
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(255,215,0,0.3);
            }}
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
            .btn {{ 
                padding: 10px 20px; 
                border: none; 
                border-radius: 8px;
                cursor: pointer; 
                font-weight: bold; 
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
                font-size: 14px;
            }}
            .btn:hover {{ 
                transform: translateY(-2px); 
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }}
            .btn-primary {{ background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); color: #000; }}
            .btn-success {{ background: linear-gradient(135deg, #00cc00 0%, #009900 100%); color: white; }}
            .btn-info {{ background: linear-gradient(135deg, #0066cc 0%, #004499 100%); color: white; }}
            .btn-danger {{ background: linear-gradient(135deg, #cc0000 0%, #990000 100%); color: white; }}
            .btn-warning {{ background: linear-gradient(135deg, #ff8c00 0%, #ff6b35 100%); color: white; }}
            .task-item {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                padding: 20px; 
                margin: 15px 0; 
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
            .task-title {{ font-weight: bold; margin-bottom: 8px; font-size: 18px; }}
            .task-meta {{ color: #ccc; font-size: 14px; margin-bottom: 4px; }}
            .task-actions {{ display: flex; gap: 10px; flex-wrap: wrap; }}
            .form-group {{ margin: 20px 0; }}
            .form-group label {{ 
                display: block; 
                margin-bottom: 8px; 
                color: #ffd700; 
                font-weight: bold;
            }}
            .form-group select, .form-group textarea, .form-group input {{
                width: 100%; 
                padding: 12px; 
                border: 1px solid #555; 
                border-radius: 8px;
                background: #333; 
                color: #fff;
                font-size: 16px;
                font-family: inherit;
            }}
            .form-group select:focus, .form-group textarea:focus, .form-group input:focus {{
                outline: none;
                border-color: #ffd700;
                box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.2);
            }}
            .report-area {{ 
                background: #f8f8f8; 
                color: #000; 
                padding: 20px; 
                border-radius: 10px;
                font-family: 'Courier New', monospace; 
                white-space: pre-wrap;
                min-height: 200px; 
                margin: 20px 0;
                border: 2px solid #ddd;
                font-size: 14px;
                line-height: 1.4;
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin: 20px 0; 
            }}
            .stat-box {{ 
                padding: 20px; 
                border-radius: 15px; 
                text-align: center; 
                color: white; 
                font-weight: bold;
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .stat-box:hover {{ transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
            .stat-number {{ font-size: 2.5em; margin-bottom: 10px; }}
            .stat-label {{ font-size: 1em; opacity: 0.9; }}
            .stat-pending {{ background: linear-gradient(135deg, #ff8c00 0%, #ff6b35 100%); }}
            .stat-in-progress {{ background: linear-gradient(135deg, #0066cc 0%, #004499 100%); }}
            .stat-completed {{ background: linear-gradient(135deg, #00cc00 0%, #009900 100%); }}
            .stat-blocked {{ background: linear-gradient(135deg, #cc0000 0%, #990000 100%); }}
            .success {{ color: #00ff00; font-weight: bold; }}
            .error {{ color: #ff6b6b; font-weight: bold; }}
            .time-display {{ 
                text-align: center; 
                color: #aaa; 
                font-size: 14px; 
                margin: 15px 0; 
            }}
            .status-message {{
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                font-weight: bold;
            }}
            .status-success {{ background: rgba(0, 204, 0, 0.2); color: #00ff00; border: 1px solid #00cc00; }}
            .status-error {{ background: rgba(204, 0, 0, 0.2); color: #ff6b6b; border: 1px solid #cc0000; }}
            .empty-state {{
                text-align: center;
                color: #888;
                padding: 60px 20px;
                font-size: 18px;
            }}
            @media (max-width: 768px) {{
                .task-item {{ flex-direction: column; align-items: flex-start; }}
                .task-actions {{ margin-top: 15px; width: 100%; }}
                .nav {{ gap: 10px; }}
                .nav a {{ padding: 8px 16px; font-size: 14px; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1>🍯 Honey Duo Wealth</h1>
                <div class="domain-badge">🌐 Professional Project Management • hdw.honey-duo.com</div>
                <div class="nav">
                    <a href="/" class="{'active' if active_page == 'dashboard' else ''}">📊 Dashboard</a>
                    <a href="/tasks" class="{'active' if active_page == 'tasks' else ''}">📋 Tasks</a>
                    <a href="/reports" class="{'active' if active_page == 'reports' else ''}">📈 Reports</a>
                    <a href="/help" class="{'active' if active_page == 'help' else ''}">❓ Help</a>
                </div>
            </div>
        </div>
        
        <div class="container">
    """

@app.route('/')
@requires_auth
def dashboard():
    tasks = load_tasks()
    
    # Calculate statistics
    status_counts = {}
    for task in tasks:
        status = task.get('status', 'pending')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Get recent tasks
    recent_tasks = sorted([t for t in tasks if t.get('updated')], 
                         key=lambda x: x.get('updated', ''), reverse=True)[:10]
    
    current_time = datetime.datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')
    
    html = get_base_html("Dashboard", "dashboard")
    
    html += f"""
            <div class="time-display">{current_time}</div>
            
            <div class="content-section">
                <h2 class="section-title">📊 Project Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-box stat-pending">
                        <div class="stat-number">{status_counts.get('pending', 0)}</div>
                        <div class="stat-label">⏳ Pending Tasks</div>
                    </div>
                    <div class="stat-box stat-in-progress">
                        <div class="stat-number">{status_counts.get('in-progress', 0)}</div>
                        <div class="stat-label">🔄 In Progress</div>
                    </div>
                    <div class="stat-box stat-completed">
                        <div class="stat-number">{status_counts.get('completed', 0)}</div>
                        <div class="stat-label">✅ Completed</div>
                    </div>
                    <div class="stat-box stat-blocked">
                        <div class="stat-number">{status_counts.get('blocked', 0)}</div>
                        <div class="stat-label">🚫 Blocked</div>
                    </div>
                </div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">🚀 Quick Actions</h2>
                <div style="display: flex; gap: 15px; flex-wrap: wrap; justify-content: center;">
                    <a href="/tasks" class="btn btn-primary">📋 Manage Tasks</a>
                    <a href="/reports" class="btn btn-success">📈 Generate Reports</a>
                    <button onclick="location.reload()" class="btn btn-info">🔄 Refresh Dashboard</button>
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
                    dt = datetime.datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    time_str = dt.strftime('%m/%d %I:%M%p')
                except:
                    time_str = updated[:10]
            else:
                time_str = 'Never'
            
            html += f"""
                <div class="task-item">
                    <div class="task-info">
                        <div class="task-title">{status_icon} {task['id']}</div>
                        <div class="task-meta">{task.get('description', '')}</div>
                        <div class="task-meta">Updated: {time_str} • Status: {task.get('status', 'pending')}</div>
                    </div>
                    <div class="task-actions">
                        <a href="/tasks" class="btn btn-primary">📋 Manage</a>
                    </div>
                </div>
            """
    else:
        html += '<div class="empty-state">No recent activity</div>'
    
    html += """
            </div>
        </div>
        
        <script>
        // Auto-refresh every 2 minutes
        setTimeout(() => location.reload(), 120000);
        </script>
    </body>
    </html>
    """
    
    return html

@app.route('/tasks')
@requires_auth
def tasks():
    tasks = load_tasks()
    
    html = get_base_html("Task Management", "tasks")
    
    html += f"""
            <div class="content-section">
                <h2 class="section-title">📋 Task Management</h2>
                <div style="margin-bottom: 20px; text-align: center;">
                    <button onclick="location.reload()" class="btn btn-info">🔄 Refresh Tasks</button>
                </div>
            </div>
    """
    
    # Group tasks by status
    task_groups = {
        'pending': [t for t in tasks if t.get('status') == 'pending'],
        'in-progress': [t for t in tasks if t.get('status') == 'in-progress'],
        'completed': [t for t in tasks if t.get('status') == 'completed'],
        'blocked': [t for t in tasks if t.get('status') == 'blocked']
    }
    
    group_info = {
        'pending': ('⏳ Pending Tasks', 'These tasks are ready to start'),
        'in-progress': ('🔄 In Progress', 'Currently active tasks'),
        'completed': ('✅ Completed Tasks', 'Successfully finished tasks'),
        'blocked': ('🚫 Blocked Tasks', 'Tasks waiting for resolution')
    }
    
    for status, task_list in task_groups.items():
        if task_list:  # Only show sections with tasks
            title, description = group_info[status]
            html += f"""
            <div class="content-section">
                <h2 class="section-title">{title}</h2>
                <p style="color: #ccc; margin-bottom: 20px;">{description}</p>
            """
            
            for task in task_list:
                updated = task.get('updated', '')
                if updated:
                    try:
                        dt = datetime.datetime.fromisoformat(updated.replace('Z', '+00:00'))
                        time_str = dt.strftime('%m/%d %I:%M%p')
                    except:
                        time_str = updated[:10]
                else:
                    time_str = 'Never'
                
                html += f"""
                <div class="task-item">
                    <div class="task-info">
                        <div class="task-title">{task['id']}</div>
                        <div class="task-meta">{task.get('description', 'No description')}</div>
                        <div class="task-meta">Updated: {time_str}</div>
                        <div class="task-meta">Output: {task.get('output', 'Not specified')}</div>
                """
                
                if task.get('tests'):
                    html += f'<div class="task-meta">Tests: {task["tests"]}</div>'
                
                html += """
                    </div>
                    <div class="task-actions">
                """
                
                # Action buttons based on status
                if status == 'pending':
                    html += f'<button class="btn btn-success" onclick="startTask(\'{task["id"]}\')">🚀 Start Task</button>'
                elif status == 'in-progress':
                    html += f'<button class="btn btn-primary" onclick="completeTask(\'{task["id"]}\')">✅ Complete Task</button>'
                
                if status not in ['completed', 'blocked']:
                    html += f'<button class="btn btn-danger" onclick="blockTask(\'{task["id"]}\')">🚫 Block Task</button>'
                
                if status in ['completed', 'blocked', 'in-progress']:
                    html += f'<a href="/reports?task={task["id"]}" class="btn btn-warning">📈 Generate Report</a>'
                
                html += """
                    </div>
                </div>
                """
            
            html += "</div>"
    
    if not any(task_groups.values()):
        html += '<div class="content-section"><div class="empty-state">No tasks found. Check your tasks.yaml file.</div></div>'
    
    html += """
        </div>
        
        <script>
        function startTask(taskId) {
            if (!confirm(`Start task '${taskId}'?\\n\\nThis will create a context file for Claude.`)) return;
            
            fetch('/api/start_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: taskId})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Task '${taskId}' started successfully!\\n\\n📄 Context file created for Claude.`);
                    location.reload();
                } else {
                    alert(`❌ Error starting task: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`❌ Network error: ${error}`);
            });
        }
        
        function completeTask(taskId) {
            const message = prompt(`Complete task '${taskId}'\\n\\nOptional commit message:`);
            if (message === null) return; // User cancelled
            
            fetch('/api/complete_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: taskId, message: message || ''})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Task '${taskId}' completed and committed to git!`);
                    location.reload();
                } else {
                    alert(`❌ Error completing task: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`❌ Network error: ${error}`);
            });
        }
        
        function blockTask(taskId) {
            const reason = prompt(`Block task '${taskId}'\\n\\nReason for blocking:`);
            if (!reason) return;
            
            fetch('/api/block_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: taskId, reason: reason})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`🚫 Task '${taskId}' blocked successfully!`);
                    location.reload();
                } else {
                    alert(`❌ Error blocking task: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`❌ Network error: ${error}`);
            });
        }
        </script>
    </body>
    </html>
    """
    
    return html

@app.route('/reports')
@requires_auth
def reports():
    tasks = load_tasks()
    reportable_tasks = [t for t in tasks if t.get('status') in ['completed', 'blocked', 'in-progress']]
    
    # Get task from URL parameter if specified
    selected_task = request.args.get('task', '')
    
    html = get_base_html("ChatGPT Reports", "reports")
    
    html += f"""
            <div class="content-section">
                <h2 class="section-title">📈 ChatGPT Status Reports</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Generate professional status updates for ChatGPT</p>
                
                <div class="form-group">
                    <label for="task-select">Select Task:</label>
                    <select id="task-select" onchange="updateSummary()">
                        <option value="">Choose a task...</option>
    """
    
    for task in reportable_tasks:
        selected = 'selected' if task['id'] == selected_task else ''
        status_icon = {'pending': '⏳', 'in-progress': '🔄', 'completed': '✅', 'blocked': '🚫'}.get(task.get('status'), '❓')
        html += f'<option value="{task["id"]}" {selected}>{status_icon} {task["id"]} - {task.get("description", "")[:60]}</option>'
    
    html += """
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="summary-input">Custom Summary (optional):</label>
                    <textarea id="summary-input" rows="4" placeholder="Leave empty for auto-generated summary based on task description"></textarea>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <button class="btn btn-primary" onclick="generateReport()">📈 Generate Report</button>
                    <button class="btn btn-info" onclick="copyReport()">📋 Copy to Clipboard</button>
                    <button class="btn btn-success" onclick="openReportsFolder()">📁 Open Reports Folder</button>
                </div>
                
                <div id="status-message"></div>
                
                <div class="form-group">
                    <label>Generated Report (Copy & Paste to ChatGPT):</label>
                    <div id="report-output" class="report-area">
Click "Generate Report" to create a ChatGPT status update...

The report will include:
• Task ID and current status
• Summary of work completed
• Files/artifacts created
• Professional formatting for ChatGPT

Reports are automatically saved to: chatgpt_reports/ChatGPT_Update_taskname_MMDD_HHMM.txt
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        function updateSummary() {
            const taskSelect = document.getElementById('task-select');
            const summaryInput = document.getElementById('summary-input');
            
            if (taskSelect.value) {
                const selectedOption = taskSelect.options[taskSelect.selectedIndex];
                const taskDesc = selectedOption.text.split(' - ')[1] || '';
                if (taskDesc) {
                    summaryInput.placeholder = `Auto-generated: "Implemented ${taskDesc}"`;
                }
            }
        }
        
        function generateReport() {
            const taskId = document.getElementById('task-select').value;
            const summary = document.getElementById('summary-input').value;
            
            if (!taskId) {
                showMessage('Please select a task first', 'error');
                return;
            }
            
            showMessage('Generating report...', 'info');
            
            fetch('/api/generate_report', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: taskId, summary: summary})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('report-output').textContent = data.report;
                    showMessage(`✅ Report generated and saved as: ${data.filename}`, 'success');
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        }
        
        function copyReport() {
            const reportText = document.getElementById('report-output').textContent;
            if (!reportText || reportText.includes('Click "Generate Report"')) {
                showMessage('Generate a report first', 'error');
                return;
            }
            
            navigator.clipboard.writeText(reportText).then(() => {
                showMessage('📋 Report copied to clipboard! Paste it into ChatGPT.', 'success');
            }).catch(() => {
                showMessage('❌ Failed to copy to clipboard', 'error');
            });
        }
        
        function openReportsFolder() {
            showMessage('📁 Reports are saved to: chatgpt_reports/ folder in your project directory', 'info');
        }
        
        function showMessage(message, type) {
            const statusDiv = document.getElementById('status-message');
            statusDiv.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
            
            // Auto-clear success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    statusDiv.innerHTML = '';
                }, 5000);
            }
        }
        
        // Auto-update summary when page loads if task is selected
        window.onload = function() {
            updateSummary();
        };
        </script>
    </body>
    </html>
    """
    
    return html

@app.route('/help')
@requires_auth
def help_page():
    html = get_base_html("Help & User Guide", "help")
    
    html += """
            <div class="content-section">
                <h2 class="section-title">📖 HDW User Guide</h2>
                
                <h3 style="color: #ffd700; margin-top: 25px;">🔄 Your Workflow</h3>
                <ol style="margin-left: 20px; line-height: 2;">
                    <li><strong>Check Dashboard</strong> for project overview and statistics</li>
                    <li><strong>Go to Tasks</strong> to start pending work</li>
                    <li><strong>Click "🚀 Start Task"</strong> - creates context file for Claude</li>
                    <li><strong>Work with Claude</strong> using the generated context</li>
                    <li><strong>Click "✅ Complete Task"</strong> when done</li>
                    <li><strong>Generate ChatGPT Reports</strong> to update project status</li>
                </ol>
                
                <h3 style="color: #ffd700; margin-top: 25px;">📊 Dashboard</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li>View real-time task statistics</li>
                    <li>See recent activity and updates</li>
                    <li>Quick access to all management functions</li>
                    <li>Auto-refreshes every 2 minutes</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">📋 Task Management</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>🚀 Start Task:</strong> Creates context file for Claude</li>
                    <li><strong>✅ Complete Task:</strong> Marks as done and commits to git</li>
                    <li><strong>🚫 Block Task:</strong> Mark as blocked with reason</li>
                    <li><strong>📈 Generate Report:</strong> Create ChatGPT status update</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">📈 ChatGPT Reports</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li>Select any completed or in-progress task</li>
                    <li>Add custom summary or use auto-generated one</li>
                    <li>Report includes task status, summary, and artifacts</li>
                    <li>Automatically saved with clear naming: <code>ChatGPT_Update_taskname_MMDD_HHMM.txt</code></li>
                    <li>Copy and paste directly into ChatGPT</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">🔧 Technical Details</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Access:</strong> https://hdw.honey-duo.com (worldwide)</li>
                    <li><strong>Security:</strong> HTTPS + login protection</li>
                    <li><strong>Files:</strong> Reports saved to chatgpt_reports/ folder</li>
                    <li><strong>Context:</strong> Task context files created in .task_context_*.md</li>
                    <li><strong>Integration:</strong> Direct CLI integration for task management</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">💡 Tips for Success</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li>Always start tasks before working with Claude</li>
                    <li>Use descriptive commit messages when completing tasks</li>
                    <li>Generate reports regularly to keep ChatGPT updated</li>
                    <li>Check the dashboard daily for project overview</li>
                    <li>Block tasks immediately if you encounter issues</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">🚨 Troubleshooting</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Tasks not loading:</strong> Check tasks.yaml file exists</li>
                    <li><strong>Commands failing:</strong> Ensure CLI tools are working</li>
                    <li><strong>Reports not saving:</strong> Check chatgpt_reports/ folder permissions</li>
                    <li><strong>Interface slow:</strong> Use refresh buttons to reload data</li>
                </ul>
                
                <div style="background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; border-radius: 8px; padding: 20px; margin: 25px 0;">
                    <h4 style="color: #ffd700;">🎯 Remember: This is YOUR Professional Interface</h4>
                    <p>You now have a world-class project management system accessible from anywhere via your own domain. Use it to efficiently coordinate between ChatGPT (planning), Claude (coding), and yourself (integration).</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

# API Endpoints
@app.route('/api/start_task', methods=['POST'])
@requires_auth
def start_task():
    data = request.json
    task_id = data.get('task_id')
    if not task_id:
        return jsonify({"success": False, "error": "No task ID provided"})
    
    result = run_cli_command(f"start {task_id}")
    return jsonify(result)

@app.route('/api/complete_task', methods=['POST'])
@requires_auth
def complete_task():
    data = request.json
    task_id = data.get('task_id')
    message = data.get('message', '')
    
    if not task_id:
        return jsonify({"success": False, "error": "No task ID provided"})
    
    if message:
        command = f'commit {task_id} --message "{message}"'
    else:
        command = f"commit {task_id}"
    
    result = run_cli_command(command)
    return jsonify(result)

@app.route('/api/block_task', methods=['POST'])
@requires_auth
def block_task():
    data = request.json
    task_id = data.get('task_id')
    reason = data.get('reason', '')
    
    if not task_id or not reason:
        return jsonify({"success": False, "error": "Task ID and reason required"})
    
    result = run_cli_command(f'block {task_id} "{reason}"')
    return jsonify(result)

@app.route('/api/generate_report', methods=['POST'])
@requires_auth
def generate_report():
    data = request.json
    task_id = data.get('task_id')
    custom_summary = data.get('summary', '')
    
    if not task_id:
        return jsonify({"success": False, "error": "No task ID provided"})
    
    # Find the task
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({"success": False, "error": f"Task '{task_id}' not found"})
    
    # Generate summary
    if custom_summary:
        summary = custom_summary
    else:
        summary = f"Implemented {task.get('description', 'task requirements')}"
    
    # Get artifacts from git
    try:
        result = subprocess.run(
            ["git", "show", "--name-only", "--pretty=format:", "HEAD"],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        recent_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        artifacts = ", ".join(recent_files) if recent_files else task.get("output", "No artifacts specified")
    except:
        artifacts = task.get("output", "No artifacts specified")
    
    status = task.get('status', 'pending').title()
    
    # Create report
    report = f"""Task: {task_id}
Status: {status}
Summary: "{summary}"
Artifacts: {artifacts}"""
    
    # Save to file
    timestamp = datetime.datetime.now().strftime('%m%d_%H%M')
    reports_dir = PROJECT_ROOT / "chatgpt_reports"
    reports_dir.mkdir(exist_ok=True)
    
    filename = f"ChatGPT_Update_{task_id}_{timestamp}.txt"
    report_file = reports_dir / filename
    
    with open(report_file, 'w') as f:
        f.write(f"# ChatGPT Status Update\n")
        f.write(f"# Generated: {datetime.datetime.now().strftime('%A %B %d, %Y at %I:%M %p')}\n")
        f.write(f"# Task: {task_id}\n\n")
        f.write(report)
    
    return jsonify({
        "success": True, 
        "report": report, 
        "filename": filename,
        "filepath": str(report_file)
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "domain": "hdw.honey-duo.com"})

if __name__ == "__main__":
    print("🌐 HDW Complete Management Interface Starting...")
    print("🔐 Access: https://hdw.honey-duo.com")
    print("🔑 Login: hdw / HoneyDuo2025!")
    print("")
    print("💡 Features Available:")
    print("  📊 Dashboard - Project overview and statistics")
    print("  📋 Tasks - Complete task management")
    print("  📈 Reports - ChatGPT status report generation")
    print("  ❓ Help - Full user guide")
    print("")
    print("🚀 Ready for professional project management!")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
