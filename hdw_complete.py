#!/usr/bin/env python3
"""
Honey Duo Wealth Complete Management Interface
Enhanced with multi-phase support, progress tracking, Blueprint Generator UI, and Enhanced Context
"""

from flask import Flask, request, jsonify, make_response, redirect, url_for
from functools import wraps
import yaml
import subprocess
import os
import sys
from pathlib import Path
import datetime
import json

# Add src to path to import TaskManager
sys.path.insert(0, str(Path(__file__).parent))
from src.task_manager import TaskManager

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

# Initialize TaskManager
task_manager = TaskManager(PROJECT_ROOT)

def run_cli_command(command):
    """Run CLI command and return result"""
    try:
        cmd = f"python3 {PROJECT_ROOT}/cli/hdw-task.py {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_ROOT)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def get_base_html(title, active_page="dashboard"):
    """Get base HTML template with enhanced styling for phases"""
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
            .btn-secondary {{ background: linear-gradient(135deg, #666 0%, #888 100%); color: white; }}
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
                background: #1a1a1a; 
                color: #ffffff; 
                padding: 20px; 
                border-radius: 10px;
                font-family: 'Courier New', monospace; 
                white-space: pre-wrap;
                min-height: 300px; 
                margin: 20px 0;
                border: 2px solid #ffd700;
                font-size: 13px;
                line-height: 1.4;
                overflow-y: auto;
                max-height: 600px;
            }}
            .generator-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .generator-card {{
                background: rgba(30, 30, 30, 0.8);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid rgba(255, 215, 0, 0.3);
                transition: all 0.3s ease;
            }}
            .generator-card:hover {{
                border-color: #ffd700;
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(255, 215, 0, 0.2);
            }}
            .card-title {{
                color: #ffd700;
                font-size: 1.3em;
                font-weight: bold;
                margin-bottom: 15px;
                text-align: center;
            }}
            .card-description {{
                color: #ccc;
                margin-bottom: 20px;
                text-align: center;
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
            .info {{ color: #0099ff; font-weight: bold; }}
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
            .status-info {{ background: rgba(0, 102, 204, 0.2); color: #0099ff; border: 1px solid #0066cc; }}
            .empty-state {{
                text-align: center;
                color: #888;
                padding: 60px 20px;
                font-size: 18px;
            }}
            .phase-section {{
                margin: 30px 0;
                padding: 20px;
                background: rgba(30, 30, 30, 0.5);
                border-radius: 12px;
                border: 1px solid rgba(255, 215, 0, 0.2);
            }}
            .phase-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}
            .phase-title {{
                font-size: 1.3em;
                color: #ffd700;
                font-weight: bold;
            }}
            .phase-progress {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .progress-bar {{
                width: 200px;
                height: 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #ffd700 0%, #ffed4e 100%);
                transition: width 0.3s ease;
            }}
            .progress-text {{
                font-size: 14px;
                color: #ccc;
            }}
            /* Enhanced context modal styles */
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
            }}
            .modal-content {{
                background-color: #2b2b2b;
                margin: 5% auto;
                padding: 20px;
                border: 2px solid #ffd700;
                border-radius: 10px;
                width: 80%;
                max-width: 800px;
                max-height: 80vh;
                overflow-y: auto;
                color: #fff;
            }}
            .close {{
                color: #ffd700;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }}
            .close:hover {{
                color: #ffed4e;
            }}
            .checkbox-container {{
                margin: 15px 0;
                padding: 15px;
                background: rgba(255, 215, 0, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(255, 215, 0, 0.3);
            }}
            .checkbox-container label {{
                display: flex;
                align-items: center;
                cursor: pointer;
            }}
            .checkbox-container input[type="checkbox"] {{
                margin-right: 10px;
                width: 20px;
                height: 20px;
                cursor: pointer;
            }}
            .related-tasks {{
                margin: 20px 0;
                padding: 15px;
                background: rgba(30, 30, 30, 0.8);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .related-task {{
                padding: 10px;
                margin: 5px 0;
                background: rgba(51, 51, 51, 0.8);
                border-radius: 5px;
                border-left: 3px solid #ffd700;
            }}
            @media (max-width: 768px) {{
                .task-item {{ flex-direction: column; align-items: flex-start; }}
                .task-actions {{ margin-top: 15px; width: 100%; }}
                .nav {{ gap: 10px; }}
                .nav a {{ padding: 8px 16px; font-size: 14px; }}
                .progress-bar {{ width: 150px; }}
                .generator-grid {{ grid-template-columns: 1fr; }}
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
                    <a href="/phases" class="{'active' if active_page == 'phases' else ''}">📁 Phases</a>
                    <a href="/generator" class="{'active' if active_page == 'generator' else ''}">🏗️ Generator</a>
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
    tasks_data = task_manager.load_tasks()
    tasks = tasks_data.get("tasks", [])
    
    # Calculate statistics
    status_counts = {}
    for task in tasks:
        status = task.get('status', 'pending')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Get phase progress
    phase_progress = task_manager.get_phase_progress()
    
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
                <h2 class="section-title">📈 Phase Progress</h2>
    """
    
    # Show phase progress
    for phase_id in sorted(phase_progress.keys()):
        progress = phase_progress[phase_id]
        bar_width = int(progress["percentage"])
        
        html += f"""
                <div class="phase-section">
                    <div class="phase-header">
                        <div class="phase-title">📁 Phase {phase_id}: {progress['name']}</div>
                        <div class="phase-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {bar_width}%"></div>
                            </div>
                            <div class="progress-text">{progress['percentage']:.0f}% ({progress['completed']}/{progress['total']})</div>
                        </div>
                    </div>
                    <div style="color: #ccc; font-size: 14px;">
                        {progress['completed']} completed, {progress['in_progress']} in progress, {progress['pending']} pending
                        {f", {progress['blocked']} blocked" if progress['blocked'] > 0 else ""}
                    </div>
                </div>
        """
    
    html += """
            </div>
            
            <div class="content-section">
                <h2 class="section-title">🚀 Quick Actions</h2>
                <div style="display: flex; gap: 15px; flex-wrap: wrap; justify-content: center;">
                    <a href="/tasks" class="btn btn-primary">📋 Manage Tasks</a>
                    <a href="/phases" class="btn btn-info">📁 View Phases</a>
                    <a href="/generator" class="btn btn-success">🏗️ Blueprint Generator</a>
                    <a href="/reports" class="btn btn-warning">📈 Generate Reports</a>
                    <button onclick="location.reload()" class="btn btn-secondary">🔄 Refresh Dashboard</button>
                </div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">🔄 Recent Activity</h2>
    """
    
    if recent_tasks:
        for task in recent_tasks:
            status_icon = {'pending': '⏳', 'in-progress': '🔄', 'completed': '✅', 'blocked': '🚫'}.get(task.get('status'), '❓')
            phase_info = f"Phase {task.get('phase', 0)}" if task.get('phase', 0) > 0 else "Legacy"
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
                        <div class="task-meta">{phase_info} • Updated: {time_str} • Status: {task.get('status', 'pending')}</div>
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
    tasks_data = task_manager.load_tasks()
    tasks = tasks_data.get("tasks", [])
    
    html = get_base_html("Task Management", "tasks")
    
    html += f"""
            <div class="content-section">
                <h2 class="section-title">📋 Task Management</h2>
                <div style="margin-bottom: 20px; text-align: center;">
                    <button onclick="location.reload()" class="btn btn-info">🔄 Refresh Tasks</button>
                </div>
            </div>
    """
    
    # Group tasks by phase
    tasks_by_phase = {}
    for task in tasks:
        phase = task.get('phase', 0)
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = {
                'pending': [],
                'in-progress': [],
                'completed': [],
                'blocked': []
            }
        status = task.get('status', 'pending')
        tasks_by_phase[phase][status].append(task)
    
    # Display tasks grouped by phase
    for phase_id in sorted(tasks_by_phase.keys()):
        phase_info = tasks_data.get("phases", {}).get(str(phase_id), {})
        phase_name = phase_info.get("name", "Legacy Tasks" if phase_id == 0 else f"Phase {phase_id}")
        
        # Count tasks in this phase
        phase_task_count = sum(len(tasks_by_phase[phase_id][status]) for status in ['pending', 'in-progress', 'completed', 'blocked'])
        
        if phase_task_count > 0:
            html += f"""
            <div class="content-section">
                <h2 class="section-title">📁 {phase_name}</h2>
            """
            
            # Show tasks by status within the phase
            status_order = ['in-progress', 'pending', 'blocked', 'completed']
            status_info = {
                'pending': ('⏳', 'Pending'),
                'in-progress': ('🔄', 'In Progress'),
                'completed': ('✅', 'Completed'),
                'blocked': ('🚫', 'Blocked')
            }
            
            for status in status_order:
                task_list = tasks_by_phase[phase_id][status]
                if task_list:
                    emoji, label = status_info[status]
                    html += f'<h4 style="color: #ffd700; margin: 20px 0 10px 0;">{emoji} {label} ({len(task_list)})</h4>'
                    
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
                        
                        # Show block reason for blocked tasks
                        if status == "blocked" and task.get("notes"):
                            for note in reversed(task.get("notes", [])):
                                if "Blocked:" in note.get("note", ""):
                                    html += f'<div class="task-meta" style="color: #ff6b6b; font-weight: bold;">🚫 {note["note"]}</div>'
                                    break
                        
                        html += """
                            </div>
                            <div class="task-actions">
                        """
                        
                        # Action buttons based on status
                        if status == 'pending':
                            html += f'<button class="btn btn-success" onclick="showStartDialog(\'{task["id"]}\')">🚀 Start Task</button>'
                        elif status == 'in-progress':
                            html += f'<button class="btn btn-primary" onclick="completeTask(\'{task["id"]}\')">✅ Complete Task</button>'
                        
                        if status not in ['completed', 'blocked']:
                            html += f'<button class="btn btn-danger" onclick="blockTask(\'{task["id"]}\')">🚫 Block Task</button>'
                        
                        # Add enhanced context buttons
                        if status in ['pending', 'in-progress']:
                            html += f'<button class="btn btn-secondary" onclick="previewContext(\'{task["id"]}\')">👁️ Preview Context</button>'
                            html += f'<button class="btn btn-info" onclick="showRelatedTasks(\'{task["id"]}\')">🔗 Related Tasks</button>'
                        
                        if status in ['completed', 'blocked', 'in-progress']:
                            html += f'<a href="/reports?task={task["id"]}" class="btn btn-warning">📈 Generate Report</a>'
                        
                        html += """
                            </div>
                        </div>
                        """
            
            html += "</div>"
    
    if not tasks:
        html += '<div class="content-section"><div class="empty-state">No tasks found.</div></div>'
    
    # Enhanced context modal
    html += """
        <!-- Modal for enhanced context -->
        <div id="contextModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <div id="modalContent"></div>
            </div>
        </div>
        
        </div>
        
        <script>
        function showStartDialog(taskId) {
            const modalContent = `
                <h2 style="color: #ffd700; margin-bottom: 20px;">🚀 Start Task: ${taskId}</h2>
                <div class="checkbox-container">
                    <label>
                        <input type="checkbox" id="useEnhanced" checked>
                        <span style="font-size: 16px;">✨ Use Enhanced Context</span>
                    </label>
                    <p style="color: #ccc; margin-top: 10px; margin-left: 30px; font-size: 14px;">
                        Includes related tasks, architecture diagrams, and decision history
                    </p>
                </div>
                <div style="margin-top: 20px;">
                    <button class="btn btn-success" onclick="startTaskWithOptions('${taskId}')">🚀 Start Task</button>
                    <button class="btn btn-secondary" onclick="previewContextInModal('${taskId}')">👁️ Preview Context</button>
                    <button class="btn btn-secondary" onclick="closeModal()">❌ Cancel</button>
                </div>
                <div id="previewArea" style="margin-top: 20px;"></div>
            `;
            
            document.getElementById('modalContent').innerHTML = modalContent;
            document.getElementById('contextModal').style.display = 'block';
        }
        
        function startTaskWithOptions(taskId) {
            const useEnhanced = document.getElementById('useEnhanced').checked;
            
            if (!confirm(`Start task '${taskId}' with ${useEnhanced ? 'enhanced' : 'basic'} context?\\n\\nThis will create a context file for Claude.`)) return;
            
            fetch('/api/start_task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    task_id: taskId,
                    enhanced: useEnhanced
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Task '${taskId}' started successfully!\\n\\n📄 ${data.enhanced ? 'Enhanced' : 'Basic'} context file created.`);
                    location.reload();
                } else {
                    alert(`❌ Error starting task: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`❌ Network error: ${error}`);
            });
        }
        
        function startTask(taskId) {
            // Legacy function for backward compatibility
            showStartDialog(taskId);
        }
        
        function previewContext(taskId) {
            fetch(`/api/preview_context/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    const modalContent = `
                        <h2 style="color: #ffd700;">📄 Context Preview: ${taskId}</h2>
                        <div class="report-area" style="max-height: 500px;">
                            ${data.context.replace(/\\n/g, '\\n')}
                        </div>
                        <button class="btn btn-secondary" onclick="closeModal()">Close</button>
                    `;
                    document.getElementById('modalContent').innerHTML = modalContent;
                    document.getElementById('contextModal').style.display = 'block';
                })
                .catch(error => {
                    alert(`❌ Error loading context: ${error}`);
                });
        }
        
        function previewContextInModal(taskId) {
            const useEnhanced = document.getElementById('useEnhanced').checked;
            
            fetch(`/api/preview_context/${taskId}?enhanced=${useEnhanced}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('previewArea').innerHTML = `
                        <h3 style="color: #ffd700;">Preview:</h3>
                        <div class="report-area" style="max-height: 300px;">
                            ${data.context.replace(/\\n/g, '\\n')}
                        </div>
                    `;
                })
                .catch(error => {
                    document.getElementById('previewArea').innerHTML = `<p class="error">Error loading preview</p>`;
                });
        }
        
        function showRelatedTasks(taskId) {
            fetch(`/api/related_tasks/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    let relatedHtml = '<h3 style="color: #ffd700;">🔗 Related Tasks</h3>';
                    
                    if (data.related_tasks && data.related_tasks.length > 0) {
                        relatedHtml += '<div class="related-tasks">';
                        data.related_tasks.forEach(task => {
                            const statusIcon = task.status === 'completed' ? '✅' : '🔄';
                            relatedHtml += `
                                <div class="related-task">
                                    <strong>${statusIcon} ${task.id}</strong>: ${task.description}
                                    <div style="color: #888; font-size: 12px; margin-top: 5px;">
                                        Phase ${task.phase} • Status: ${task.status}
                                    </div>
                                </div>
                            `;
                        });
                        relatedHtml += '</div>';
                    } else {
                        relatedHtml += '<p style="color: #888;">No related tasks found.</p>';
                    }
                    
                    relatedHtml += '<button class="btn btn-secondary" onclick="closeModal()" style="margin-top: 20px;">Close</button>';
                    
                    document.getElementById('modalContent').innerHTML = relatedHtml;
                    document.getElementById('contextModal').style.display = 'block';
                })
                .catch(error => {
                    alert(`❌ Error loading related tasks: ${error}`);
                });
        }
        
        function closeModal() {
            document.getElementById('contextModal').style.display = 'none';
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('contextModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
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

@app.route('/phases')
@requires_auth
def phases():
    tasks_data = task_manager.load_tasks()
    phase_progress = task_manager.get_phase_progress()
    
    html = get_base_html("Phase Overview", "phases")
    
    html += """
            <div class="content-section">
                <h2 class="section-title">📁 Phase Management</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Track progress across all project phases</p>
            </div>
    """
    
    for phase_id in sorted(phase_progress.keys()):
        progress = phase_progress[phase_id]
        phase_info = tasks_data.get("phases", {}).get(str(phase_id), {})
        
        # Get all tasks for this phase
        phase_tasks = [t for t in tasks_data.get("tasks", []) if t.get("phase", 0) == phase_id]
        
        html += f"""
            <div class="content-section">
                <div class="phase-header">
                    <div>
                        <h3 class="phase-title">📁 Phase {phase_id}: {progress['name']}</h3>
                        {f'<p style="color: #ccc; margin: 10px 0;">{phase_info.get("description", "")}</p>' if phase_info.get("description") else ''}
                    </div>
                    <div class="phase-progress">
                        <div class="progress-bar" style="width: 300px;">
                            <div class="progress-fill" style="width: {progress['percentage']}%"></div>
                        </div>
                        <div class="progress-text" style="font-size: 18px; color: #ffd700;">{progress['percentage']:.0f}%</div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0;">
                    <div style="text-align: center; padding: 15px; background: rgba(0, 204, 0, 0.1); border-radius: 8px;">
                        <div style="font-size: 24px; font-weight: bold; color: #00ff00;">{progress['completed']}</div>
                        <div style="color: #ccc;">Completed</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(0, 102, 204, 0.1); border-radius: 8px;">
                        <div style="font-size: 24px; font-weight: bold; color: #0099ff;">{progress['in_progress']}</div>
                        <div style="color: #ccc;">In Progress</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255, 140, 0, 0.1); border-radius: 8px;">
                        <div style="font-size: 24px; font-weight: bold; color: #ff8c00;">{progress['pending']}</div>
                        <div style="color: #ccc;">Pending</div>
                    </div>
                    {f'<div style="text-align: center; padding: 15px; background: rgba(204, 0, 0, 0.1); border-radius: 8px;"><div style="font-size: 24px; font-weight: bold; color: #ff6b6b;">{progress["blocked"]}</div><div style="color: #ccc;">Blocked</div></div>' if progress['blocked'] > 0 else ''}
                </div>
                
                <div style="margin-top: 20px;">
                    <a href="/tasks" class="btn btn-primary">📋 View Phase Tasks</a>
                    <a href="/generator?phase={phase_id}" class="btn btn-success">🏗️ Generate Blueprint</a>
                    {f'<span style="color: #888; margin-left: 15px;">Source: {phase_info.get("file", "tasks.yaml")}</span>' if phase_id > 0 else ''}
                </div>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/generator')
@requires_auth
def generator():
    phase_progress = task_manager.get_phase_progress()
    selected_phase = request.args.get('phase', '1')
    
    html = get_base_html("Blueprint Generator", "generator")
    
    html += f"""
            <div class="content-section">
                <h2 class="section-title">🏗️ Blueprint Generator</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Generate comprehensive documentation for Claude session handoffs</p>
                
                <div class="form-group">
                    <label for="phase-select">Select Phase:</label>
                    <select id="phase-select">
    """
    
    # Add phase options
    for phase_id in sorted(phase_progress.keys()):
        progress = phase_progress[phase_id]
        selected = 'selected' if str(phase_id) == selected_phase else ''
        status_emoji = "✅" if progress['percentage'] == 100 else "🔄" if progress['completed'] > 0 else "⏳"
        html += f'<option value="{phase_id}" {selected}>{status_emoji} Phase {phase_id}: {progress["name"]} ({progress["percentage"]:.0f}%)</option>'
    
    html += """
                    </select>
                </div>
            </div>
            
            <div class="generator-grid">
                <div class="generator-card">
                    <div class="card-title">📋 Phase Blueprint</div>
                    <div class="card-description">Complete technical blueprint with tasks, architecture, and progress for the selected phase</div>
                    <button class="btn btn-primary" onclick="generateDocument('phase')" style="width: 100%;">🏗️ Generate Phase Blueprint</button>
                </div>
                
                <div class="generator-card">
                    <div class="card-title">🤝 Session Handoff</div>
                    <div class="card-description">Comprehensive handoff document for new Claude sessions with all context needed</div>
                    <button class="btn btn-success" onclick="generateDocument('handoff')" style="width: 100%;">📋 Generate Session Handoff</button>
                </div>
                
                <div class="generator-card">
                    <div class="card-title">🏗️ System Architecture</div>
                    <div class="card-description">Current system architecture analysis with component connections and data flows</div>
                    <button class="btn btn-info" onclick="generateDocument('architecture')" style="width: 100%;">🏗️ Generate Architecture Map</button>
                </div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">📊 Generation Controls</h2>
                <div style="text-align: center; margin: 20px 0;">
                    <button class="btn btn-warning" onclick="copyToClipboard()">📋 Copy Generated Content</button>
                    <button class="btn btn-secondary" onclick="downloadAsFile()">💾 Download as File</button>
                    <button class="btn btn-info" onclick="viewSavedFiles()">📁 View Saved Files</button>
                </div>
                
                <div id="status-message"></div>
            </div>
            
            <div class="content-section">
                <h2 class="section-title">📄 Generated Content</h2>
                <div id="generated-content" class="report-area">
Select a blueprint type above to generate comprehensive documentation...

🏗️ Phase Blueprint: Complete technical overview of the selected phase
🤝 Session Handoff: Everything needed for Claude session continuity  
🏗️ System Architecture: Technical component mapping and data flows

Generated documents are automatically saved to docs/blueprints/ for future reference.
                </div>
            </div>
        </div>
        
        <script>
        let currentContent = '';
        let currentFilename = '';
        
        function generateDocument(docType) {
            const phaseId = document.getElementById('phase-select').value;
            
            showMessage(`Generating ${docType} documentation...`, 'info');
            
            const requestData = {
                type: docType,
                phase_id: parseInt(phaseId)
            };
            
            fetch('/api/generate_blueprint', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentContent = data.content;
                    currentFilename = data.filename || data.filepath || `${docType}_${phaseId}.md`;
                    
                    document.getElementById('generated-content').textContent = currentContent;
                    showMessage(`✅ ${docType} documentation generated successfully!`, 'success');
                    
                    if (data.filepath) {
                        showMessage(`💾 Saved to: ${data.filepath}`, 'info');
                    }
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error}`, 'error');
            });
        }
        
        function copyToClipboard() {
            if (!currentContent) {
                showMessage('Generate content first before copying', 'error');
                return;
            }
            
            navigator.clipboard.writeText(currentContent).then(() => {
                showMessage('📋 Content copied to clipboard! Ready for Claude handoff.', 'success');
            }).catch(() => {
                showMessage('❌ Failed to copy to clipboard', 'error');
            });
        }
        
        function downloadAsFile() {
            if (!currentContent) {
                showMessage('Generate content first before downloading', 'error');
                return;
            }
            
            const blob = new Blob([currentContent], { type: 'text/markdown' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentFilename || 'blueprint.md';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showMessage(`💾 Downloaded: ${a.download}`, 'success');
        }
        
        function viewSavedFiles() {
            showMessage('📁 Generated files are saved to: docs/blueprints/ and docs/sessions/', 'info');
        }
        
        function showMessage(message, type) {
            const statusDiv = document.getElementById('status-message');
            statusDiv.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
            
            // Auto-clear success messages after 5 seconds
            if (type === 'success' || type === 'info') {
                setTimeout(() => {
                    statusDiv.innerHTML = '';
                }, 5000);
            }
        }
        </script>
    </body>
    </html>
    """
    
    return html

@app.route('/reports')
@requires_auth
def reports():
    tasks_data = task_manager.load_tasks()
    tasks = tasks_data.get("tasks", [])
    reportable_tasks = [t for t in tasks if t.get('status') in ['completed', 'blocked', 'in-progress']]
    
    # Get task from URL parameter if specified
    selected_task = request.args.get('task', '')
    
    html = get_base_html("Claude Reports", "reports")
    
    html += f"""
            <div class="content-section">
                <h2 class="section-title">📈 Claude Handoff Reports</h2>
                <p style="color: #ccc; margin-bottom: 20px;">Generate status reports for Claude session handoffs</p>
                
                <div class="form-group">
                    <label for="task-select">Select Task:</label>
                    <select id="task-select" onchange="updateSummary()">
                        <option value="">Choose a task...</option>
    """
    
    # Group tasks by phase for better organization
    tasks_by_phase = {}
    for task in reportable_tasks:
        phase = task.get('phase', 0)
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = []
        tasks_by_phase[phase].append(task)
    
    for phase_id in sorted(tasks_by_phase.keys()):
        phase_name = f"Phase {phase_id}" if phase_id > 0 else "Legacy"
        html += f'<optgroup label="{phase_name}">'
        
        for task in tasks_by_phase[phase_id]:
            selected = 'selected' if task['id'] == selected_task else ''
            status_icon = {'pending': '⏳', 'in-progress': '🔄', 'completed': '✅', 'blocked': '🚫'}.get(task.get('status'), '❓')
            html += f'<option value="{task["id"]}" {selected}>{status_icon} {task["id"]} - {task.get("description", "")[:60]}</option>'
        
        html += '</optgroup>'
    
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
                    <label>Generated Report (For Claude Handoff):</label>
                    <div id="report-output" class="report-area">
Click "Generate Report" to create a Claude handoff report...

The report will include:
• Task ID and phase information
• Current status and progress
• Summary of work completed
• Files/artifacts created
• Context for continuing work

Reports are automatically saved to: claude_reports/Claude_Handoff_taskname_MMDD_HHMM.txt
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
                showMessage('📋 Report copied to clipboard! Ready for Claude handoff.', 'success');
            }).catch(() => {
                showMessage('❌ Failed to copy to clipboard', 'error');
            });
        }
        
        function openReportsFolder() {
            showMessage('📁 Reports are saved to: claude_reports/ folder in your project directory', 'info');
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
                <h2 class="section-title">📖 HDW User Guide - Enhanced Edition</h2>
                
                <h3 style="color: #ffd700; margin-top: 25px;">🎯 What's New</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Enhanced Context:</strong> Rich context with related tasks and architecture</li>
                    <li><strong>Blueprint Generator:</strong> Comprehensive technical documentation system</li>
                    <li><strong>Multi-Phase Support:</strong> Tasks organized by project phases</li>
                    <li><strong>Phase Progress Tracking:</strong> Visual progress bars for each phase</li>
                    <li><strong>Enhanced Dashboard:</strong> Phase overview with completion percentages</li>
                    <li><strong>Session Handoffs:</strong> Complete context preservation for Claude sessions</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">✨ Enhanced Context Features</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Architecture Diagrams:</strong> Shows where your task fits in the system</li>
                    <li><strong>Related Tasks:</strong> Automatically finds and displays related completed work</li>
                    <li><strong>Decision History:</strong> Captures and presents key decisions from the phase</li>
                    <li><strong>Preview Before Start:</strong> See what context will be generated</li>
                    <li><strong>Toggle Option:</strong> Choose between enhanced or basic context</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">🏗️ Blueprint Generator Features</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Phase Blueprints:</strong> Complete technical overview with tasks and architecture</li>
                    <li><strong>Session Handoffs:</strong> Everything needed for Claude session continuity</li>
                    <li><strong>System Architecture:</strong> Component mapping and data flow analysis</li>
                    <li><strong>Document Management:</strong> Auto-saving with one source of truth per phase</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">🔄 Enhanced Workflow</h3>
                <ol style="margin-left: 20px; line-height: 2;">
                    <li><strong>Check Dashboard</strong> - See phase progress at a glance</li>
                    <li><strong>View Phases</strong> - Detailed phase breakdown and statistics</li>
                    <li><strong>Start Task</strong> - Choose enhanced context for richer information</li>
                    <li><strong>Preview Context</strong> - See what will be generated before starting</li>
                    <li><strong>Use Generator</strong> - Create blueprints and handoff documents</li>
                    <li><strong>Generate Reports</strong> - Quick Claude handoff reports</li>
                </ol>
                
                <h3 style="color: #ffd700; margin-top: 25px;">📁 Page Overview</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>📊 Dashboard:</strong> Project overview and phase progress</li>
                    <li><strong>📋 Tasks:</strong> Phase-organized task management with enhanced context</li>
                    <li><strong>📁 Phases:</strong> Detailed phase tracking and progress</li>
                    <li><strong>🏗️ Generator:</strong> Blueprint and handoff document creation</li>
                    <li><strong>📈 Reports:</strong> Quick task-specific Claude reports</li>
                    <li><strong>❓ Help:</strong> This user guide</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">🏗️ Generator Page Usage</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Phase Blueprint:</strong> Generate complete technical documentation for a phase</li>
                    <li><strong>Session Handoff:</strong> Create comprehensive handoff for Claude sessions</li>
                    <li><strong>System Architecture:</strong> Generate current system architecture analysis</li>
                    <li><strong>Copy/Download:</strong> Easy sharing and preservation of generated documents</li>
                </ul>
                
                <h3 style="color: #ffd700; margin-top: 25px;">💡 CLI Commands</h3>
                <pre style="background: #333; padding: 15px; border-radius: 8px; color: #0f0;">
# Start task with enhanced context (default)
python3 cli/hdw-task.py start task-id

# Start task with basic context
python3 cli/hdw-task.py start task-id --basic

# List all tasks grouped by phase
python3 cli/hdw-task.py list

# Show phase progress
python3 cli/hdw-task.py phases

# Generate blueprints via CLI
python3 src/blueprint_generator.py update --phase-id 1
                </pre>
                
                <div style="background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; border-radius: 8px; padding: 20px; margin: 25px 0;">
                    <h4 style="color: #ffd700;">🎯 Pro Tip: Enhanced Context</h4>
                    <p>The enhanced context feature automatically finds related tasks, shows where you're working in the system architecture, and includes relevant decisions from completed work. This creates perfect continuity between Claude sessions!</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

# API Endpoints with Enhanced Context Support
@app.route('/api/start_task', methods=['POST'])
@requires_auth
def start_task():
    data = request.json
    task_id = data.get('task_id')
    use_enhanced = data.get('enhanced', True)  # Default to enhanced
    
    if not task_id:
        return jsonify({"success": False, "error": "No task ID provided"})
    
    # Use the enhanced parameter in the CLI command
    if use_enhanced:
        result = run_cli_command(f"start {task_id}")
    else:
        result = run_cli_command(f"start {task_id} --basic")
    
    # Add enhanced context info to response
    result['enhanced'] = use_enhanced
    
    return jsonify(result)

@app.route('/api/preview_context/<task_id>')
@requires_auth
def preview_context(task_id):
    """Preview the enhanced context that would be generated"""
    try:
        # Check if enhanced parameter is provided
        use_enhanced = request.args.get('enhanced', 'true').lower() == 'true'
        
        # Generate the context without saving
        if use_enhanced:
            context_content = task_manager.generate_enhanced_context(task_id)
        else:
            # Generate basic context
            tasks_data = task_manager.load_tasks()
            task = next((t for t in tasks_data['tasks'] if t['id'] == task_id), None)
            
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            
            context_content = f"# Context for Task: {task_id}\n\n"
            context_content += f"**Phase:** {task.get('phase', 0)} - {task.get('phase_name', 'Legacy')}\n"
            context_content += f"**Description:** {task['description']}\n\n"
            context_content += f"**Expected Output:** {task.get('output', 'Not specified')}\n\n"
            
            if task.get('acceptance_criteria'):
                context_content += "**Acceptance Criteria:**\n"
                for criteria in task['acceptance_criteria']:
                    context_content += f"- {criteria}\n"
                context_content += "\n"
        
        return jsonify({
            'task_id': task_id,
            'context': context_content,
            'type': 'enhanced' if use_enhanced else 'basic'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/related_tasks/<task_id>')
@requires_auth
def get_related_tasks(task_id):
    """Get tasks related to the specified task"""
    try:
        related_tasks = task_manager.find_related_tasks(task_id, limit=5)
        
        # Format for JSON response
        formatted_tasks = []
        for task in related_tasks:
            formatted_tasks.append({
                'id': task['id'],
                'description': task.get('description', ''),
                'status': task.get('status', 'unknown'),
                'phase': task.get('phase', 0),
                'output': task.get('output', '')
            })
        
        return jsonify({
            'task_id': task_id,
            'related_tasks': formatted_tasks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/generate_blueprint', methods=['POST'])
@requires_auth
def generate_blueprint():
    """Generate blueprint documentation via API"""
    data = request.json
    blueprint_type = data.get('type', 'phase')  # 'phase', 'handoff', or 'architecture'
    phase_id = data.get('phase_id', 1)
    
    try:
        from src.blueprint_generator import PhaseBlueprintGenerator
        generator = PhaseBlueprintGenerator(PROJECT_ROOT)
        
        if blueprint_type == 'phase':
            content = generator.generate_comprehensive_phase_blueprint(phase_id)
            filename = f"phase_{phase_id}_blueprint.md"
            # Save the blueprint
            filepath = generator.update_phase_blueprint(phase_id)
        elif blueprint_type == 'handoff':
            # Generate session handoff
            content = generator.generate_session_handoff()
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"session_{timestamp}.md"
            filepath = PROJECT_ROOT / "docs" / "sessions" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            filepath = str(filepath)
        elif blueprint_type == 'architecture':
            # Generate system architecture analysis
            content = generator.generate_system_architecture_blueprint()
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"architecture_{timestamp}.md"
            filepath = PROJECT_ROOT / "docs" / "blueprints" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            filepath = str(filepath)
        else:
            return jsonify({"success": False, "error": "Invalid blueprint type"})
        
        return jsonify({
            "success": True,
            "content": content,
            "filepath": filepath,
            "filename": filename
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/generate_report', methods=['POST'])
@requires_auth
def generate_report():
    data = request.json
    task_id = data.get('task_id')
    custom_summary = data.get('summary', '')
    
    if not task_id:
        return jsonify({"success": False, "error": "No task ID provided"})
    
    # Find the task using TaskManager
    tasks_data = task_manager.load_tasks()
    task = next((t for t in tasks_data.get("tasks", []) if t['id'] == task_id), None)
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
    phase_info = f"Phase {task.get('phase', 0)}: {task.get('phase_name', 'Legacy')}"
    
    # Create Claude-focused report
    report = f"""=== CLAUDE HANDOFF REPORT ===
Task: {task_id}
{phase_info}
Status: {status}
Summary: "{summary}"
Expected Output: {task.get('output', 'Not specified')}
Artifacts: {artifacts}

Context: This task is part of the Honey Duo Wealth project management system.
Next Steps: Continue with remaining Phase {task.get('phase', 0)} tasks or begin next phase.
==========================="""
    
    # Save to file
    timestamp = datetime.datetime.now().strftime('%m%d_%H%M')
    reports_dir = PROJECT_ROOT / "claude_reports"
    reports_dir.mkdir(exist_ok=True)
    
    filename = f"Claude_Handoff_{task_id}_{timestamp}.txt"
    report_file = reports_dir / filename
    
    with open(report_file, 'w') as f:
        f.write(f"# Claude Handoff Report\n")
        f.write(f"# Generated: {datetime.datetime.now().strftime('%A %B %d, %Y at %I:%M %p')}\n")
        f.write(f"# Task: {task_id}\n\n")
        f.write(report)
        f.write(f"\n\n# Phase Progress:\n")
        
        # Add phase progress info
        phase_progress = task_manager.get_phase_progress()
        for phase_id, progress in phase_progress.items():
            f.write(f"Phase {phase_id} ({progress['name']}): {progress['percentage']:.0f}% complete\n")
    
    return jsonify({
        "success": True, 
        "report": report, 
        "filename": filename,
        "filepath": str(report_file)
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "domain": "hdw.honey-duo.com", "version": "3.1-enhanced-context"})

if __name__ == "__main__":
    print("🌐 HDW Complete Management Interface - Enhanced Context Edition")
    print("🔐 Access: https://hdw.honey-duo.com")
    print("🔑 Login: hdw / HoneyDuo2025!")
    print("")
    print("💡 New Features:")
    print("  ✨ Enhanced Context - Related tasks, architecture, decisions")
    print("  📁 Phases - Multi-phase project organization")
    print("  📊 Dashboard - Phase progress tracking")
    print("  📋 Tasks - Grouped by phase with context preview")
    print("  🏗️ Generator - Blueprint and handoff document creation")
    print("  📈 Reports - Claude handoff reports")
    print("  ❓ Help - Updated user guide")
    print("")
    print("🚀 Ready for enhanced context generation and blueprint creation!")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)