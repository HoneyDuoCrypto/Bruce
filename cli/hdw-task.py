#!/usr/bin/env python3
"""
HDW Task CLI - Honey Duo Wealth Task Management CLI
Enhanced with multi-phase support and better organization
"""

import argparse
import sys
from pathlib import Path

# Add src to path to import TaskManager
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.task_manager import TaskManager

def main():
    parser = argparse.ArgumentParser(description="HDW Task Management CLI")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--phase", type=int, help="Filter by phase")
    
    # Status command  
    status_parser = subparsers.add_parser("status", help="Show task status")
    status_parser.add_argument("task_id", nargs="?", help="Specific task ID")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a task")
    start_parser.add_argument("task_id", help="Task ID to start")
    
    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Commit completed task")
    commit_parser.add_argument("task_id", help="Task ID to commit")
    commit_parser.add_argument("--message", help="Commit message")
    
    # Block command
    block_parser = subparsers.add_parser("block", help="Mark task as blocked")
    block_parser.add_argument("task_id", help="Task ID to block")
    block_parser.add_argument("reason", help="Reason for blocking")
    
    # Phase command (new!)
    phase_parser = subparsers.add_parser("phases", help="Show phase progress")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize enhanced task manager
    task_manager = TaskManager(args.project_root)
    
    # Execute commands using TaskManager methods
    if args.command == "list":
        cmd_list_enhanced(task_manager, args.status, args.phase if hasattr(args, 'phase') else None)
    elif args.command == "status":
        cmd_status_enhanced(task_manager, args.task_id)
    elif args.command == "start":
        task_manager.cmd_start(args.task_id)
    elif args.command == "commit":
        cmd_commit_enhanced(task_manager, args.task_id, args.message)
    elif args.command == "block":
        cmd_block_enhanced(task_manager, args.task_id, args.reason)
    elif args.command == "phases":
        cmd_phases(task_manager)

def cmd_list_enhanced(tm: TaskManager, status_filter=None, phase_filter=None):
    """Enhanced list command with phase support"""
    tasks_data = tm.load_tasks()
    tasks = tasks_data.get("tasks", [])
    
    # Apply filters
    if status_filter:
        tasks = [t for t in tasks if t.get("status") == status_filter]
    if phase_filter is not None:
        tasks = [t for t in tasks if t.get("phase", 0) == phase_filter]
    
    if not tasks:
        print("No tasks found.")
        return
    
    # Group by phase
    tasks_by_phase = {}
    for task in tasks:
        phase = task.get("phase", 0)
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = []
        tasks_by_phase[phase].append(task)
    
    # Display tasks grouped by phase
    for phase in sorted(tasks_by_phase.keys()):
        phase_tasks = tasks_by_phase[phase]
        phase_info = tasks_data.get("phases", {}).get(str(phase), {})
        phase_name = phase_info.get("name", "Legacy Tasks" if phase == 0 else f"Phase {phase}")
        
        print(f"\n📋 {phase_name} ({len(phase_tasks)} tasks):")
        print("-" * 80)
        
        for task in phase_tasks:
            status = task.get("status", "pending")
            status_emoji = {
                "pending": "⏳",
                "in-progress": "🔄", 
                "completed": "✅",
                "blocked": "🚫"
            }.get(status, "❓")
            
            print(f"{status_emoji} {task['id']:<20} {status:<12} {task.get('description', '')}")

def cmd_status_enhanced(tm: TaskManager, task_id=None):
    """Enhanced status command with phase progress"""
    if task_id:
        # Show specific task details
        tasks_data = tm.load_tasks()
        task = None
        for t in tasks_data.get("tasks", []):
            if t["id"] == task_id:
                task = t
                break
        
        if not task:
            print(f"❌ Task '{task_id}' not found")
            return
        
        print(f"\n📄 Task: {task['id']}")
        print(f"Phase: {task.get('phase', 0)} - {task.get('phase_name', 'Legacy')}")
        print(f"Status: {task.get('status', 'pending')}")
        print(f"Description: {task.get('description', '')}")
        print(f"Output: {task.get('output', '')}")
        if task.get('context'):
            print(f"Context: {', '.join(task['context'])}")
        if task.get('acceptance_criteria'):
            print("Acceptance Criteria:")
            for criteria in task['acceptance_criteria']:
                print(f"  - {criteria}")
        if task.get('updated'):
            print(f"Updated: {task['updated']}")
    else:
        # Show overall project status with phase breakdown
        tasks_data = tm.load_tasks()
        tasks = tasks_data.get("tasks", [])
        
        print(f"\n📊 Project Status:")
        print("-" * 50)
        
        # Overall stats
        status_counts = {}
        for task in tasks:
            status = task.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Phase progress
        phase_progress = tm.get_phase_progress()
        if phase_progress:
            print(f"\n📈 Phase Progress:")
            print("-" * 50)
            for phase_id in sorted(phase_progress.keys()):
                progress = phase_progress[phase_id]
                bar_length = 20
                filled = int(bar_length * progress["percentage"] / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                print(f"Phase {phase_id}: {progress['name']}")
                print(f"  [{bar}] {progress['percentage']}% ({progress['completed']}/{progress['total']})")

def cmd_commit_enhanced(tm: TaskManager, task_id: str, message=None):
    """Enhanced commit with proper task updates"""
    import subprocess
    from datetime import datetime
    
    # Find task to get current data
    tasks_data = tm.load_tasks()
    task = None
    for t in tasks_data.get("tasks", []):
        if t["id"] == task_id:
            task = t
            break
    
    if not task:
        print(f"❌ Task '{task_id}' not found")
        return
    
    # Update task
    commit_message = message or f"Complete task: {task_id}"
    updates = {
        "status": "completed",
        "updated": datetime.now().isoformat(),
        "notes": task.get("notes", []) + [{
            "timestamp": datetime.now().isoformat(),
            "note": f"Task committed: {commit_message}"
        }]
    }
    
    tm.save_task_updates(task_id, updates)
    
    # Git operations
    try:
        subprocess.run(["git", "add", "."], cwd=tm.project_root, check=True)
        subprocess.run(["git", "commit", "-m", commit_message], cwd=tm.project_root, check=True)
        print(f"✅ Task {task_id} committed to git")
    except subprocess.CalledProcessError:
        print(f"⚠️  Git commit failed (not in git repo?)")
    except FileNotFoundError:
        print(f"⚠️  Git not found")
    
    # Clean up context file
    for context_dir in tm.contexts_dir.glob("phase*"):
        context_file = context_dir / f"context_{task_id}.md"
        if context_file.exists():
            context_file.unlink()
            break
    
    # Also check old location for backward compatibility
    old_context_file = tm.project_root / f".task_context_{task_id}.md"
    if old_context_file.exists():
        old_context_file.unlink()
    
    print(f"✅ Task {task_id} marked as completed")
    
    # Generate report
    generate_claude_report(task, "Completed", commit_message)
    
    # Auto-generate blueprint documentation
    try:
        from src.blueprint_generator import BlueprintGenerator
        generator = BlueprintGenerator(tm.project_root)
        blueprint_results = generator.auto_generate_on_completion(task_id)
        
        if blueprint_results and "error" not in blueprint_results:
            print("\n📋 Auto-generated blueprints:")
            for doc_type, filepath in blueprint_results.items():
                print(f"  ✅ {doc_type}: {Path(filepath).name}")
        elif blueprint_results and "error" in blueprint_results:
            print(f"\n⚠️  Blueprint generation warning: {blueprint_results['error']}")
    except ImportError:
        print("\n⚠️  Blueprint generator not available (src/blueprint_generator.py not found)")
    except Exception as e:
        print(f"\n⚠️  Blueprint generation failed: {e}")
        # Don't fail task completion if blueprint generation fails

def cmd_block_enhanced(tm: TaskManager, task_id: str, reason: str):
    """Enhanced block command"""
    from datetime import datetime
    
    # Find task
    tasks_data = tm.load_tasks()
    task = None
    for t in tasks_data.get("tasks", []):
        if t["id"] == task_id:
            task = t
            break
    
    if not task:
        print(f"❌ Task '{task_id}' not found")
        return
    
    # Update task
    updates = {
        "status": "blocked",
        "updated": datetime.now().isoformat(),
        "notes": task.get("notes", []) + [{
            "timestamp": datetime.now().isoformat(),
            "note": f"Blocked: {reason}"
        }]
    }
    
    tm.save_task_updates(task_id, updates)
    print(f"🚫 Task {task_id} marked as blocked: {reason}")
    
    # Generate report
    generate_claude_report(task, "Blocked", f"Blocked: {reason}")

def cmd_phases(tm: TaskManager):
    """Show detailed phase progress"""
    phase_progress = tm.get_phase_progress()
    tasks_data = tm.load_tasks()
    
    print("\n📊 Phase Overview")
    print("=" * 60)
    
    for phase_id in sorted(phase_progress.keys()):
        progress = phase_progress[phase_id]
        phase_info = tasks_data.get("phases", {}).get(str(phase_id), {})
        
        # Progress bar
        bar_length = 30
        filled = int(bar_length * progress["percentage"] / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\n📁 Phase {phase_id}: {progress['name']}")
        if phase_info.get("description"):
            print(f"   {phase_info['description']}")
        
        print(f"\n   Progress: [{bar}] {progress['percentage']}%")
        print(f"   Tasks: {progress['completed']} completed, {progress['in_progress']} in progress, {progress['pending']} pending")
        
        if progress["blocked"] > 0:
            print(f"   ⚠️  Blocked: {progress['blocked']} tasks")

def generate_claude_report(task, status, summary):
    """Generate a report for Claude (replacing ChatGPT report)"""
    print("\n" + "="*50)
    print("📋 STATUS REPORT FOR CLAUDE HANDOFF")
    print("="*50)
    print(f"Task: {task['id']}")
    print(f"Phase: {task.get('phase', 0)} - {task.get('phase_name', 'Legacy')}")
    print(f"Status: {status}")
    print(f"Summary: {summary}")
    if task.get("output"):
        print(f"Expected Output: {task['output']}")
    print("="*50)
    print("📋 Save this for session handoff\n")

if __name__ == "__main__":
    main()