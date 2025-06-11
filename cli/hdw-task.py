#!/usr/bin/env python3
"""
Bruce Task CLI - Enhanced with Dynamic Task/Phase Management
Enhanced with multi-phase support and enhanced context generation
Plus new commands: add-task, add-phase, edit-task
Save as: cli/bruce-task.py
"""

import argparse
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add src to path to import TaskManager
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.task_manager import TaskManager

def main():
    parser = argparse.ArgumentParser(description="Bruce Project Management CLI")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Existing commands
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--phase", type=int, help="Filter by phase")
    
    status_parser = subparsers.add_parser("status", help="Show task status")
    status_parser.add_argument("task_id", nargs="?", help="Specific task ID")
    
    start_parser = subparsers.add_parser("start", help="Start a task")
    start_parser.add_argument("task_id", help="Task ID to start")
    start_parser.add_argument("--basic", action="store_true", 
                            help="Use basic context instead of enhanced (default: enhanced)")
    
    commit_parser = subparsers.add_parser("commit", help="Commit completed task")
    commit_parser.add_argument("task_id", help="Task ID to commit")
    commit_parser.add_argument("--message", help="Commit message")
    
    block_parser = subparsers.add_parser("block", help="Mark task as blocked")
    block_parser.add_argument("task_id", help="Task ID to block")
    block_parser.add_argument("reason", help="Reason for blocking")
    
    phase_parser = subparsers.add_parser("phases", help="Show phase progress")
    
    # NEW COMMANDS
    # Add task command
    add_task_parser = subparsers.add_parser("add-task", help="Add new task to phase")
    add_task_parser.add_argument("--phase", type=int, required=True, help="Phase ID")
    add_task_parser.add_argument("--id", required=True, help="Task ID")
    add_task_parser.add_argument("--description", required=True, help="Task description")
    add_task_parser.add_argument("--output", help="Expected output")
    add_task_parser.add_argument("--context", nargs="*", help="Context files")
    add_task_parser.add_argument("--tests", help="Test file")
    add_task_parser.add_argument("--depends-on", nargs="*", help="Task dependencies")
    add_task_parser.add_argument("--acceptance-criteria", nargs="*", help="Acceptance criteria")
    
    # Add phase command
    add_phase_parser = subparsers.add_parser("add-phase", help="Add new phase")
    add_phase_parser.add_argument("--id", type=int, required=True, help="Phase ID")
    add_phase_parser.add_argument("--name", required=True, help="Phase name")
    add_phase_parser.add_argument("--description", required=True, help="Phase description")
    
    # Edit task command
    edit_task_parser = subparsers.add_parser("edit-task", help="Edit existing task")
    edit_task_parser.add_argument("--id", required=True, help="Task ID to edit")
    edit_task_parser.add_argument("--description", help="New description")
    edit_task_parser.add_argument("--output", help="New expected output")
    edit_task_parser.add_argument("--context", nargs="*", help="New context files")
    edit_task_parser.add_argument("--tests", help="New test file")
    edit_task_parser.add_argument("--depends-on", nargs="*", help="New dependencies")
    edit_task_parser.add_argument("--acceptance-criteria", nargs="*", help="New acceptance criteria")
    
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
        task_manager.cmd_start(args.task_id, enhanced=not args.basic)
    elif args.command == "commit":
        cmd_commit_enhanced(task_manager, args.task_id, args.message)
    elif args.command == "block":
        cmd_block_enhanced(task_manager, args.task_id, args.reason)
    elif args.command == "phases":
        cmd_phases(task_manager)
    # NEW COMMAND HANDLERS
    elif args.command == "add-task":
        cmd_add_task(task_manager, args)
    elif args.command == "add-phase":
        cmd_add_phase(task_manager, args)
    elif args.command == "edit-task":
        cmd_edit_task(task_manager, args)

# NEW COMMAND FUNCTIONS

def cmd_add_task(tm: TaskManager, args):
    """Add a new task to an existing phase"""
    
    # Check if task ID already exists
    tasks_data = tm.load_tasks()
    existing_task = next((t for t in tasks_data.get("tasks", []) if t["id"] == args.id), None)
    if existing_task:
        print(f"❌ Task '{args.id}' already exists")
        return
    
    # Find the phase file
    phase_file = find_phase_file(tm, args.phase)
    if not phase_file:
        print(f"❌ Phase {args.phase} not found. Create it first with 'add-phase'")
        return
    
    # Create new task
    new_task = {
        "id": args.id,
        "description": args.description,
        "status": "pending"
    }
    
    # Add optional fields
    if args.output:
        new_task["output"] = args.output
    if args.context:
        new_task["context"] = args.context
    if args.tests:
        new_task["tests"] = args.tests
    if args.depends_on:
        new_task["depends_on"] = args.depends_on
    if args.acceptance_criteria:
        new_task["acceptance_criteria"] = args.acceptance_criteria
    
    # Load existing phase data
    with open(phase_file, 'r') as f:
        phase_data = yaml.safe_load(f)
    
    # Add task to phase
    if "tasks" not in phase_data:
        phase_data["tasks"] = []
    
    phase_data["tasks"].append(new_task)
    
    # Save updated phase file
    with open(phase_file, 'w') as f:
        yaml.dump(phase_data, f, default_flow_style=False, indent=2, sort_keys=False)
    
    print(f"✅ Added task '{args.id}' to phase {args.phase}")
    print(f"📁 File: {phase_file.name}")
    print(f"📝 Description: {args.description}")

def cmd_add_phase(tm: TaskManager, args):
    """Add a new phase"""
    
    # Check if phase already exists
    existing_file = find_phase_file(tm, args.id)
    if existing_file:
        print(f"❌ Phase {args.id} already exists: {existing_file.name}")
        return
    
    # Create new phase file
    # Format: phase{id}_{name_snake_case}.yml
    safe_name = args.name.lower().replace(" ", "_").replace("-", "_")
    phase_filename = f"phase{args.id}_{safe_name}.yml"
    phase_file = tm.phases_dir / phase_filename
    
    # Create phase data structure
    phase_data = {
        "phase": {
            "id": args.id,
            "name": args.name,
            "description": args.description
        },
        "tasks": []
    }
    
    # Save phase file
    with open(phase_file, 'w') as f:
        yaml.dump(phase_data, f, default_flow_style=False, indent=2, sort_keys=False)
    
    print(f"✅ Created new phase {args.id}: {args.name}")
    print(f"📁 File: {phase_filename}")
    print(f"📝 Description: {args.description}")
    print(f"💡 Add tasks with: bruce-task add-task --phase {args.id} --id <task-id> --description '<description>'")

def cmd_edit_task(tm: TaskManager, args):
    """Edit an existing task"""
    
    # Find the task
    tasks_data = tm.load_tasks()
    task = None
    for t in tasks_data.get("tasks", []):
        if t["id"] == args.id:
            task = t
            break
    
    if not task:
        print(f"❌ Task '{args.id}' not found")
        return
    
    # Determine which file contains this task
    phase_id = task.get("phase", 0)
    
    if phase_id == 0:
        # Legacy task in tasks.yaml
        edit_legacy_task(tm, args, task)
    else:
        # Task in phase file
        edit_phase_task(tm, args, task, phase_id)

def edit_legacy_task(tm: TaskManager, args, task):
    """Edit task in legacy tasks.yaml"""
    
    # Load tasks.yaml
    with open(tm.tasks_file, 'r') as f:
        tasks_data = yaml.safe_load(f) or {"tasks": []}
    
    # Find and update the task
    for i, t in enumerate(tasks_data["tasks"]):
        if t["id"] == args.id:
            # Update fields that were provided
            if args.description:
                t["description"] = args.description
                print(f"✓ Updated description")
            if args.output:
                t["output"] = args.output
                print(f"✓ Updated output")
            if args.context is not None:
                t["context"] = args.context
                print(f"✓ Updated context")
            if args.tests:
                t["tests"] = args.tests
                print(f"✓ Updated tests")
            if args.depends_on is not None:
                t["depends_on"] = args.depends_on
                print(f"✓ Updated dependencies")
            if args.acceptance_criteria is not None:
                t["acceptance_criteria"] = args.acceptance_criteria
                print(f"✓ Updated acceptance criteria")
            
            # Add update timestamp
            t["updated"] = datetime.now().isoformat()
            break
    
    # Save updated file
    with open(tm.tasks_file, 'w') as f:
        yaml.dump(tasks_data, f, default_flow_style=False, indent=2, sort_keys=False)
    
    print(f"✅ Updated task '{args.id}' in {tm.tasks_file.name}")

def edit_phase_task(tm: TaskManager, args, task, phase_id):
    """Edit task in phase file"""
    
    # Find phase file
    phase_file = find_phase_file(tm, phase_id)
    if not phase_file:
        print(f"❌ Could not find phase file for phase {phase_id}")
        return
    
    # Load phase data
    with open(phase_file, 'r') as f:
        phase_data = yaml.safe_load(f)
    
    # Find and update the task
    for i, t in enumerate(phase_data.get("tasks", [])):
        if t["id"] == args.id:
            # Update fields that were provided
            if args.description:
                t["description"] = args.description
                print(f"✓ Updated description")
            if args.output:
                t["output"] = args.output
                print(f"✓ Updated output")
            if args.context is not None:
                t["context"] = args.context
                print(f"✓ Updated context")
            if args.tests:
                t["tests"] = args.tests
                print(f"✓ Updated tests")
            if args.depends_on is not None:
                t["depends_on"] = args.depends_on
                print(f"✓ Updated dependencies")
            if args.acceptance_criteria is not None:
                t["acceptance_criteria"] = args.acceptance_criteria
                print(f"✓ Updated acceptance criteria")
            
            # Add update timestamp
            t["updated"] = datetime.now().isoformat()
            break
    
    # Save updated file
    with open(phase_file, 'w') as f:
        yaml.dump(phase_data, f, default_flow_style=False, indent=2, sort_keys=False)
    
    print(f"✅ Updated task '{args.id}' in {phase_file.name}")

def find_phase_file(tm: TaskManager, phase_id: int) -> Optional[Path]:
    """Find the phase file for a given phase ID"""
    for phase_file in tm.phases_dir.glob(f"phase{phase_id}_*.yml"):
        # Verify this is the right phase by checking content
        try:
            with open(phase_file, 'r') as f:
                phase_data = yaml.safe_load(f)
                if phase_data.get("phase", {}).get("id") == phase_id:
                    return phase_file
        except Exception:
            continue
    return None

# EXISTING COMMAND FUNCTIONS

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
                print(f"  [{bar}] {progress['percentage']:.0f}% ({progress['completed']}/{progress['total']})")

def cmd_commit_enhanced(tm: TaskManager, task_id: str, message=None):
    """Enhanced commit with proper task updates and blueprint generation"""
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
        from src.blueprint_generator import PhaseBlueprintGenerator
        generator = PhaseBlueprintGenerator(tm.project_root)
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
        
        print(f"\n   Progress: [{bar}] {progress['percentage']:.0f}%")
        print(f"   Tasks: {progress['completed']} completed, {progress['in_progress']} in progress, {progress['pending']} pending")
        
        if progress["blocked"] > 0:
            print(f"   ⚠️  Blocked: {progress['blocked']} tasks")

def generate_claude_report(task, status, summary):
    """Generate a report for Claude handoff"""
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