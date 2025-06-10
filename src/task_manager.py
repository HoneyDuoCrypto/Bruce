#!/usr/bin/env python3
"""
Enhanced Task Manager with Multi-Phase Support
Save as: src/task_manager.py
"""

import yaml
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import shutil

class TaskManager:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.tasks_file = self.project_root / "tasks.yaml"  # Legacy support
        self.phases_dir = self.project_root / "phases"
        self.contexts_dir = self.project_root / "contexts"  # New organized location
        self.docs_dir = self.project_root / "docs"
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        
        # Create directories if they don't exist
        self.phases_dir.mkdir(exist_ok=True)
        self.contexts_dir.mkdir(exist_ok=True)
        
    def load_tasks(self) -> Dict[str, Any]:
        """Load tasks from tasks.yaml AND phases/*.yml files"""
        all_tasks = {"tasks": []}
        
        # Load original tasks.yaml (backward compatibility)
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and data.get("tasks"):
                        # Add phase 0 to legacy tasks if not specified
                        for task in data["tasks"]:
                            if "phase" not in task:
                                task["phase"] = 0
                        all_tasks["tasks"].extend(data["tasks"])
            except Exception as e:
                print(f"Warning: Could not load tasks.yaml: {e}")
        
        # Load phase files
        if self.phases_dir.exists():
            for phase_file in sorted(self.phases_dir.glob("phase*_*.yml")):
                try:
                    with open(phase_file, 'r') as f:
                        phase_data = yaml.safe_load(f)
                        
                        # Extract phase info
                        phase_info = phase_data.get("phase", {})
                        phase_id = phase_info.get("id", "unknown")
                        phase_name = phase_info.get("name", "Unknown Phase")
                        
                        # Add phase metadata to tasks
                        if phase_data.get("tasks"):
                            for task in phase_data["tasks"]:
                                task["phase"] = phase_id
                                task["phase_name"] = phase_name
                                task["phase_file"] = phase_file.name
                            all_tasks["tasks"].extend(phase_data["tasks"])
                            
                        # Store phase metadata
                        if "phases" not in all_tasks:
                            all_tasks["phases"] = {}
                        all_tasks["phases"][phase_id] = {
                            "name": phase_name,
                            "description": phase_info.get("description", ""),
                            "file": phase_file.name,
                            "task_count": len(phase_data.get("tasks", []))
                        }
                except Exception as e:
                    print(f"Warning: Could not load {phase_file}: {e}")
        
        return all_tasks
    
    def save_task_updates(self, task_id: str, updates: Dict[str, Any]):
        """Save task updates to the appropriate file"""
        tasks_data = self.load_tasks()
        
        for task in tasks_data.get("tasks", []):
            if task["id"] == task_id:
                # Update task
                task.update(updates)
                
                # Determine which file to save to
                if task.get("phase_file"):
                    # Save to phase file
                    phase_file = self.phases_dir / task["phase_file"]
                    self._update_phase_file(phase_file, task_id, task)
                else:
                    # Save to legacy tasks.yaml
                    self._update_legacy_tasks(task_id, task)
                break
    
    def _update_phase_file(self, phase_file: Path, task_id: str, updated_task: Dict):
        """Update a task in a phase file"""
        with open(phase_file, 'r') as f:
            phase_data = yaml.safe_load(f)
        
        # Update the specific task
        for i, task in enumerate(phase_data.get("tasks", [])):
            if task["id"] == task_id:
                # Preserve phase metadata in task
                phase_meta = {
                    "phase": updated_task.get("phase"),
                    "phase_name": updated_task.get("phase_name"),
                    "phase_file": updated_task.get("phase_file")
                }
                # Remove phase metadata before saving
                clean_task = {k: v for k, v in updated_task.items() 
                             if k not in ["phase", "phase_name", "phase_file"]}
                phase_data["tasks"][i] = clean_task
                break
        
        # Save back to file
        with open(phase_file, 'w') as f:
            yaml.dump(phase_data, f, default_flow_style=False, indent=2, sort_keys=False)
    
    def _update_legacy_tasks(self, task_id: str, updated_task: Dict):
        """Update a task in legacy tasks.yaml"""
        with open(self.tasks_file, 'r') as f:
            tasks_data = yaml.safe_load(f) or {"tasks": []}
        
        # Update the specific task
        for i, task in enumerate(tasks_data.get("tasks", [])):
            if task["id"] == task_id:
                # Remove phase metadata if it's a legacy task
                clean_task = {k: v for k, v in updated_task.items() 
                             if k not in ["phase_name", "phase_file"]}
                tasks_data["tasks"][i] = clean_task
                break
        
        # Save back to file
        with open(self.tasks_file, 'w') as f:
            yaml.dump(tasks_data, f, default_flow_style=False, indent=2, sort_keys=False)
    
    def get_context(self, context_paths: List[str]) -> str:
        """Retrieve context from specified paths - handles multiple locations"""
        context_content = []
        
        for path in context_paths:
            # Try multiple locations
            locations = [
                self.project_root / path,  # Direct path
                self.docs_dir / path,       # In docs/
                self.src_dir / path,        # In src/
                Path(path)                  # Absolute path
            ]
            
            found = False
            for location in locations:
                if location.exists() and location.is_file():
                    with open(location, 'r') as f:
                        content = f.read()
                        
                        # Handle section references (e.g., file.py#section)
                        if '#' in path:
                            section = path.split('#')[1]
                            # Simple section extraction (looks for function/class)
                            lines = content.split('\n')
                            section_content = []
                            in_section = False
                            
                            for line in lines:
                                if f"def {section}" in line or f"class {section}" in line:
                                    in_section = True
                                elif in_section and (line.startswith('def ') or 
                                                    line.startswith('class ') or 
                                                    line.strip() == ''):
                                    if line.strip() != '':
                                        break
                                
                                if in_section:
                                    section_content.append(line)
                            
                            content = '\n'.join(section_content) if section_content else content
                        
                        context_content.append(f"=== {path} ===\n{content}\n")
                        found = True
                        break
            
            if not found:
                context_content.append(f"=== {path} (NOT FOUND) ===\n")
                print(f"Warning: Context file not found: {path}")
        
        return "\n".join(context_content)
    
    def cmd_start(self, task_id: str):
        """Start working on a task - enhanced version"""
        tasks_data = self.load_tasks()
        task = None
        
        for t in tasks_data.get("tasks", []):
            if t["id"] == task_id:
                task = t
                break
        
        if not task:
            print(f"❌ Task '{task_id}' not found")
            return
        
        print(f"🚀 Starting task: {task_id}")
        if task.get("phase"):
            print(f"📁 Phase {task['phase']}: {task.get('phase_name', 'Unknown')}")
        print(f"📝 Description: {task['description']}")
        
        # Update status
        self.save_task_updates(task_id, {
            "status": "in-progress",
            "updated": datetime.now().isoformat(),
            "notes": task.get("notes", []) + [{
                "timestamp": datetime.now().isoformat(),
                "note": "Task started"
            }]
        })
        
        # Create organized context file
        phase_dir = self.contexts_dir / f"phase{task.get('phase', 0)}"
        phase_dir.mkdir(exist_ok=True)
        
        context_file = phase_dir / f"context_{task_id}.md"
        
        with open(context_file, 'w') as f:
            f.write(f"# Context for Task: {task_id}\n\n")
            f.write(f"**Phase:** {task.get('phase', 0)} - {task.get('phase_name', 'Legacy')}\n")
            f.write(f"**Description:** {task['description']}\n\n")
            f.write(f"**Expected Output:** {task.get('output', 'Not specified')}\n\n")
            
            if task.get('acceptance_criteria'):
                f.write("**Acceptance Criteria:**\n")
                for criteria in task['acceptance_criteria']:
                    f.write(f"- {criteria}\n")
                f.write("\n")
            
            if task.get('depends_on'):
                f.write(f"**Dependencies:** {', '.join(task['depends_on'])}\n\n")
            
            f.write("## Context Documentation:\n\n")
            
            if task.get("context"):
                context = self.get_context(task["context"])
                f.write(context)
            else:
                f.write("No context files specified.\n")
        
        print(f"✓ Context saved to: {context_file}")
        print(f"\n💡 Ready for implementation!")
        print(f"   Use 'hdw-task commit {task_id}' when complete")
    
    def get_phase_progress(self) -> Dict[int, Dict[str, Any]]:
        """Calculate progress for each phase"""
        tasks_data = self.load_tasks()
        phase_progress = {}
        
        # Initialize phases
        for phase_id, phase_info in tasks_data.get("phases", {}).items():
            phase_progress[phase_id] = {
                "name": phase_info["name"],
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "pending": 0,
                "blocked": 0
            }
        
        # Count tasks by phase and status
        for task in tasks_data.get("tasks", []):
            phase = task.get("phase", 0)
            if phase not in phase_progress:
                phase_progress[phase] = {
                    "name": "Legacy Tasks",
                    "total": 0,
                    "completed": 0,
                    "in_progress": 0,
                    "pending": 0,
                    "blocked": 0
                }
            
            phase_progress[phase]["total"] += 1
            status = task.get("status", "pending")
            if status in phase_progress[phase]:
                phase_progress[phase][status] += 1
        
        # Calculate percentages
        for phase_id, progress in phase_progress.items():
            if progress["total"] > 0:
                progress["percentage"] = int(
                    (progress["completed"] / progress["total"]) * 100
                )
            else:
                progress["percentage"] = 0
        
        return phase_progress

# Create backward-compatible wrapper functions
def main():
    """Maintain CLI compatibility with enhanced features"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HDW Task Management CLI")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # ... (keep existing CLI structure, just use TaskManager class)
    
    args = parser.parse_args()
    
    # Initialize enhanced task manager
    task_manager = TaskManager(args.project_root)
    
    # Route commands to TaskManager methods
    # (Implementation continues with existing CLI structure...)

if __name__ == "__main__":
    print("This is the enhanced task manager library.")
    print("Import and use the TaskManager class in your code.")
    print("Or update hdw-task.py to use this implementation.")