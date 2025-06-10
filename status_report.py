#!/usr/bin/env python3
"""
Status Report Generator for ChatGPT
Generates formatted status updates after task completion
"""

import yaml
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def get_task_info(task_id):
    """Get task information from tasks.yaml"""
    tasks_file = Path("tasks.yaml")
    if not tasks_file.exists():
        return None
    
    with open(tasks_file, 'r') as f:
        tasks_data = yaml.safe_load(f)
    
    for task in tasks_data.get("tasks", []):
        if task["id"] == task_id:
            return task
    return None

def get_recent_git_files():
    """Get files changed in the last commit"""
    try:
        result = subprocess.run(
            ["git", "show", "--name-only", "--pretty=format:", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        return files
    except:
        return []

def generate_status_report(task_id, status=None, summary=None, custom_artifacts=None):
    """Generate a formatted status report for ChatGPT"""
    
    task = get_task_info(task_id)
    if not task:
        print(f"❌ Task '{task_id}' not found")
        return
    
    # Auto-detect status if not provided
    if not status:
        status = task.get("status", "Unknown").title()
    
    # Auto-generate summary if not provided
    if not summary:
        if status.lower() == "completed":
            summary = f"Implemented {task.get('description', 'task requirements')}"
        else:
            summary = f"Working on {task.get('description', 'task')}"
    
    # Auto-detect artifacts if not provided
    if not custom_artifacts:
        recent_files = get_recent_git_files()
        if recent_files:
            artifacts = ", ".join(recent_files)
        else:
            # Use expected output from task definition
            expected_output = task.get("output", "")
            test_file = task.get("tests", "")
            artifacts_list = []
            if "src/" in expected_output or expected_output.endswith(".py"):
                artifacts_list.append("src/")
            if test_file:
                artifacts_list.append(test_file)
            artifacts = ", ".join(artifacts_list) if artifacts_list else "No artifacts specified"
    else:
        artifacts = custom_artifacts
    
    # Generate the report
    report = f"""Task: {task_id}
Status: {status}
Summary: "{summary}"
Artifacts: {artifacts}"""
    
    print("\n" + "="*50)
    print("STATUS REPORT FOR CHATGPT")
    print("="*50)
    print(report)
    print("="*50)
    print("\n📋 Copy the above report and send it to ChatGPT")
    
    # Save to file for easy copying
    report_file = Path(f"status_report_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    return report

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 status_report.py <task-id> [status] [summary]")
        print("\nExamples:")
        print("  python3 status_report.py csv-loader")
        print("  python3 status_report.py csv-loader Completed 'Added error handling'")
        print("  python3 status_report.py api-client Blocked 'API key not working'")
        return
    
    task_id = sys.argv[1]
    status = sys.argv[2] if len(sys.argv) > 2 else None
    summary = sys.argv[3] if len(sys.argv) > 3 else None
    
    generate_status_report(task_id, status, summary)

if __name__ == "__main__":
    main()