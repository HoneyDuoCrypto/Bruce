#!/usr/bin/env python3
"""
Blueprint Generator for Honey Duo Wealth Project Management System

Auto-generates comprehensive blueprint documentation from completed tasks.
Integrates with existing TaskManager and works alongside current report system.
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path to import TaskManager
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.task_manager import TaskManager

class BlueprintGenerator:
    """Generates blueprint documentation from completed tasks and project data."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.task_manager = TaskManager(self.project_root)
        self.docs_path = self.project_root / "docs"
        self.blueprints_path = self.docs_path / "blueprints"
        self.sessions_path = self.docs_path / "sessions"
        
        # Ensure directories exist
        self.blueprints_path.mkdir(parents=True, exist_ok=True)
        self.sessions_path.mkdir(parents=True, exist_ok=True)
    
    def get_task_context_content(self, task_id: str, phase: int = None) -> Optional[Dict[str, Any]]:
        """Get context file content for a specific task."""
        # Look in phase-specific context directory first
        if phase is not None:
            context_file = self.task_manager.contexts_dir / f"phase{phase}" / f"context_{task_id}.md"
        else:
            # Search all phase directories
            context_file = None
            for phase_dir in self.task_manager.contexts_dir.glob("phase*"):
                potential_file = phase_dir / f"context_{task_id}.md"
                if potential_file.exists():
                    context_file = potential_file
                    break
        
        # Fallback to legacy location
        if not context_file or not context_file.exists():
            context_file = self.project_root / f".task_context_{task_id}.md"
        
        if not context_file or not context_file.exists():
            return None
        
        try:
            with open(context_file, 'r') as f:
                content = f.read()
            
            # Parse the context file content
            context_data = {
                'task_id': task_id,
                'context_file': str(context_file),
                'raw_content': content,
                'last_modified': datetime.fromtimestamp(context_file.stat().st_mtime).isoformat(),
                'phase_info': self._extract_phase_info(content),
                'description': self._extract_description(content),
                'expected_output': self._extract_expected_output(content),
                'context_docs': self._extract_context_docs(content),
                'implementation_notes': self._extract_implementation_notes(content),
                'decisions': self._extract_decisions(content)
            }
            
            return context_data
            
        except Exception as e:
            print(f"Error reading context file {context_file}: {e}")
            return None
    
    def _extract_phase_info(self, content: str) -> str:
        """Extract phase information from context content."""
        match = re.search(r'\*\*Phase:\*\* (.+)', content)
        return match.group(1) if match else "Unknown"
    
    def _extract_description(self, content: str) -> str:
        """Extract task description from context content."""
        match = re.search(r'\*\*Description:\*\* (.+)', content)
        return match.group(1) if match else "No description"
    
    def _extract_expected_output(self, content: str) -> str:
        """Extract expected output from context content."""
        match = re.search(r'\*\*Expected Output:\*\* (.+)', content)
        return match.group(1) if match else "Not specified"
    
    def _extract_context_docs(self, content: str) -> List[str]:
        """Extract referenced documentation files from context."""
        docs = []
        # Look for === filename === patterns
        matches = re.findall(r'=== (.+?) ===', content)
        return matches
    
    def _extract_implementation_notes(self, content: str) -> List[str]:
        """Extract implementation details from task notes."""
        notes = []
        
        # Look for implementation-related keywords in the content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in 
                   ['implemented', 'created', 'added', 'modified', 'enhanced', 'built', 'fixed']):
                notes.append(line)
        
        return notes
    
    def _extract_decisions(self, content: str) -> List[str]:
        """Extract decision points from context content."""
        decisions = []
        lines = content.split('\n')
        
        # Look for decision-related patterns
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in 
                   ['decision', 'chose', 'approach', 'strategy', 'because', 'rationale']):
                decisions.append(line)
        
        return decisions
    
    def generate_task_blueprint(self, task_id: str, task_info: Dict[str, Any] = None) -> str:
        """Generate comprehensive blueprint documentation for a single task."""
        
        # Get task info from TaskManager if not provided
        if not task_info:
            tasks_data = self.task_manager.load_tasks()
            task_info = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
            if not task_info:
                return f"Task {task_id} not found."
        
        # Get context data
        context_data = self.get_task_context_content(task_id, task_info.get('phase'))
        
        # Build the blueprint
        blueprint = f"""## Task: {task_id}

**Status:** {task_info.get('status', 'Unknown')} 
**Phase:** {task_info.get('phase', 0)} - {task_info.get('phase_name', 'Legacy')}
**Description:** {task_info.get('description', 'No description available')}
**Expected Output:** {task_info.get('output', 'Not specified')}
"""
        
        # Add completion information
        if task_info.get('updated'):
            blueprint += f"**Last Updated:** {task_info['updated']}\n"
        
        if task_info.get('status') == 'completed':
            blueprint += f"**✅ Completion Status:** Task successfully completed\n"
        elif task_info.get('status') == 'blocked':
            # Extract block reason from notes
            if task_info.get('notes'):
                for note in reversed(task_info['notes']):
                    if 'Blocked:' in note.get('note', ''):
                        blueprint += f"**🚫 Blocked Reason:** {note['note']}\n"
                        break
        
        # Add acceptance criteria if available
        if task_info.get('acceptance_criteria'):
            blueprint += f"\n### Acceptance Criteria\n"
            for criteria in task_info['acceptance_criteria']:
                blueprint += f"- {criteria}\n"
        
        # Add context information if available
        if context_data:
            blueprint += f"\n### Implementation Context\n"
            blueprint += f"**Context File:** {context_data['context_file']}\n"
            
            if context_data['context_docs']:
                blueprint += f"\n**Referenced Files:**\n"
                for doc in context_data['context_docs']:
                    blueprint += f"- {doc}\n"
            
            if context_data['implementation_notes']:
                blueprint += f"\n**Implementation Notes:**\n"
                for note in context_data['implementation_notes']:
                    blueprint += f"- {note}\n"
            
            if context_data['decisions']:
                blueprint += f"\n**Key Decisions:**\n"
                for decision in context_data['decisions']:
                    blueprint += f"- {decision}\n"
        
        # Add task notes/history
        if task_info.get('notes'):
            blueprint += f"\n### Task History\n"
            for note in task_info['notes']:
                timestamp = note.get('timestamp', 'Unknown time')
                note_text = note.get('note', '')
                blueprint += f"- **{timestamp[:19]}:** {note_text}\n"
        
        blueprint += "\n---\n\n"
        return blueprint
    
    def generate_phase_blueprint(self, phase_name: str = None, phase_id: int = None) -> str:
        """Generate complete blueprint for a phase."""
        tasks_data = self.task_manager.load_tasks()
        phase_progress = self.task_manager.get_phase_progress()
        
        # Determine which phase to generate
        if phase_id is not None:
            target_phase = phase_id
        elif phase_name:
            # Try to find phase by name
            target_phase = None
            for pid, pinfo in tasks_data.get("phases", {}).items():
                if phase_name.lower() in pinfo["name"].lower():
                    target_phase = pid
                    break
        else:
            # Default to latest phase with activity
            target_phase = max(phase_progress.keys()) if phase_progress else 1
        
        if target_phase not in phase_progress:
            return f"Phase {target_phase} not found."
        
        progress = phase_progress[target_phase]
        phase_info = tasks_data.get("phases", {}).get(str(target_phase), {})
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        blueprint = f"""# Phase {target_phase}: {progress['name']} Blueprint

**Generated:** {timestamp}
**Completion Status:** {progress['completed']}/{progress['total']} tasks completed ({progress['percentage']:.1f}%)

## Phase Overview

{phase_info.get('description', 'No description available')}

### Progress Summary

- **Total Tasks:** {progress['total']}
- **✅ Completed:** {progress['completed']}  
- **🔄 In Progress:** {progress['in_progress']}
- **⏳ Pending:** {progress['pending']}
- **🚫 Blocked:** {progress['blocked']}
- **Overall Progress:** {progress['percentage']:.1f}%

### Phase Progress Visualization
"""
        
        # Add a text-based progress bar
        bar_length = 50
        filled = int(bar_length * progress['percentage'] / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        blueprint += f"`[{bar}] {progress['percentage']:.1f}%`\n\n"
        
        # Get all tasks for this phase
        phase_tasks = [t for t in tasks_data.get("tasks", []) if t.get("phase", 0) == target_phase]
        
        # Group tasks by status
        tasks_by_status = {
            'completed': [],
            'in-progress': [],
            'pending': [],
            'blocked': []
        }
        
        for task in phase_tasks:
            status = task.get('status', 'pending')
            if status in tasks_by_status:
                tasks_by_status[status].append(task)
        
        # Add detailed task information
        blueprint += "## Task Details\n\n"
        
        status_order = ['completed', 'in-progress', 'pending', 'blocked']
        status_emojis = {
            'completed': '✅',
            'in-progress': '🔄', 
            'pending': '⏳',
            'blocked': '🚫'
        }
        
        for status in status_order:
            if tasks_by_status[status]:
                blueprint += f"### {status_emojis[status]} {status.replace('-', ' ').title()} Tasks\n\n"
                for task in tasks_by_status[status]:
                    blueprint += self.generate_task_blueprint(task['id'], task)
        
        # Add phase completion summary if complete
        if progress['percentage'] == 100:
            blueprint += self._generate_completion_summary(target_phase, phase_tasks)
        else:
            blueprint += self._generate_next_steps(target_phase, tasks_by_status)
        
        return blueprint
    
    def _generate_completion_summary(self, phase_id: int, tasks: List[Dict]) -> str:
        """Generate summary for completed phase."""
        return f"""
## 🎉 Phase {phase_id} Completion Summary

**Status:** ✅ PHASE COMPLETE

All tasks in this phase have been successfully completed. The following deliverables are ready:

### Created Artifacts
"""
        # Could analyze actual files created, but for now provide structure
        # This could be enhanced to scan git commits, file system changes, etc.
    
    def _generate_next_steps(self, phase_id: int, tasks_by_status: Dict) -> str:
        """Generate next steps for incomplete phase."""
        next_steps = f"""
## 🚀 Next Steps for Phase {phase_id}

"""
        
        if tasks_by_status['blocked']:
            next_steps += f"### 🚫 Resolve Blocked Tasks ({len(tasks_by_status['blocked'])})\n"
            for task in tasks_by_status['blocked']:
                next_steps += f"- **{task['id']}**: {task.get('description', '')}\n"
            next_steps += "\n"
        
        if tasks_by_status['in-progress']:
            next_steps += f"### 🔄 Complete In-Progress Tasks ({len(tasks_by_status['in-progress'])})\n"
            for task in tasks_by_status['in-progress']:
                next_steps += f"- **{task['id']}**: {task.get('description', '')}\n"
            next_steps += "\n"
        
        if tasks_by_status['pending']:
            next_steps += f"### ⏳ Start Pending Tasks ({len(tasks_by_status['pending'])})\n"
            # Show first few pending tasks as immediate priorities
            for task in tasks_by_status['pending'][:3]:
                next_steps += f"- **{task['id']}**: {task.get('description', '')}\n"
            if len(tasks_by_status['pending']) > 3:
                next_steps += f"- ... and {len(tasks_by_status['pending']) - 3} more\n"
            next_steps += "\n"
        
        return next_steps
    
    def generate_session_handoff(self, include_phase: int = None) -> str:
        """Generate comprehensive session handoff document."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        handoff = f"""# 🤝 Claude Session Handoff Document

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Session ID:** session_{timestamp}
**Project:** Honey Duo Wealth Project Management System

## 📋 Project Overview

This is the **Honey Duo Wealth** project management system designed to enable seamless handoffs between Claude sessions for multi-phase development projects.

**Main Goal:** Create a system where any Claude session can pick up work exactly where the previous one left off, with full context and understanding.

## 🎯 Current System State

"""
        
        # Get current phase progress
        phase_progress = self.task_manager.get_phase_progress()
        tasks_data = self.task_manager.load_tasks()
        
        # Overall project status
        total_tasks = sum(p['total'] for p in phase_progress.values())
        total_completed = sum(p['completed'] for p in phase_progress.values())
        overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        handoff += f"**Overall Progress:** {total_completed}/{total_tasks} tasks ({overall_progress:.1f}%)\n\n"
        
        # Phase-by-phase status
        for phase_id in sorted(phase_progress.keys()):
            progress = phase_progress[phase_id]
            status_emoji = "✅" if progress['percentage'] == 100 else "🔄" if progress['completed'] > 0 else "⏳"
            
            handoff += f"### {status_emoji} Phase {phase_id}: {progress['name']}\n"
            handoff += f"- **Progress:** {progress['completed']}/{progress['total']} tasks ({progress['percentage']:.1f}%)\n"
            handoff += f"- **Status:** {'Complete' if progress['percentage'] == 100 else 'In Progress' if progress['completed'] > 0 else 'Not Started'}\n"
            
            if progress['in_progress'] > 0:
                # Show which tasks are currently in progress
                in_progress_tasks = [t for t in tasks_data.get("tasks", []) 
                                   if t.get("phase") == phase_id and t.get("status") == "in-progress"]
                if in_progress_tasks:
                    handoff += f"- **Active Tasks:** {', '.join(t['id'] for t in in_progress_tasks)}\n"
            
            if progress['blocked'] > 0:
                handoff += f"- **⚠️ Blocked Tasks:** {progress['blocked']}\n"
            
            handoff += "\n"
        
        handoff += """## 🛠️ What's Been Built

### Core System Components
- **✅ Multi-Phase Task Manager** (`src/task_manager.py`) - Loads tasks from phase files
- **✅ Enhanced CLI Tool** (`cli/hdw-task.py`) - Phase-aware task management  
- **✅ Web Dashboard** (`hdw_complete.py`) - Phase progress tracking and management
- **✅ Context System** - Organized context files in `contexts/phase*/`
- **🔄 Blueprint Generator** (`src/blueprint_generator.py`) - Auto-documentation (this module)

### File Structure
```
honey_duo_wealth/
├── phases/                    # Phase task definitions
│   └── phase1_pm_tasks.yml   # Current phase
├── contexts/                  # Organized context files
│   └── phase1/               # Phase-specific contexts
├── src/                      # Core modules
│   ├── task_manager.py       # Enhanced task management
│   └── blueprint_generator.py # Auto-documentation
├── docs/blueprints/          # Generated documentation
├── docs/sessions/            # Session handoff docs
└── claude_reports/           # Claude handoff reports
```

## 🧠 Recent Decisions & Context

"""
        
        # Add recent completed tasks and their context
        recent_completed = []
        for task in tasks_data.get("tasks", []):
            if task.get('status') == 'completed' and task.get('updated'):
                recent_completed.append(task)
        
        # Sort by update time, get most recent
        recent_completed.sort(key=lambda x: x.get('updated', ''), reverse=True)
        
        for task in recent_completed[:5]:  # Show last 5 completed
            context_data = self.get_task_context_content(task['id'], task.get('phase'))
            handoff += f"### ✅ {task['id']} (Phase {task.get('phase', 0)})\n"
            handoff += f"**Completed:** {task.get('updated', 'Unknown')[:10]}\n"
            handoff += f"**What:** {task.get('description', '')}\n"
            
            if context_data and context_data['decisions']:
                handoff += f"**Key Decisions:**\n"
                for decision in context_data['decisions'][:2]:  # Show top 2 decisions
                    handoff += f"- {decision}\n"
            handoff += "\n"
        
        handoff += """## 🚀 How to Continue

### Immediate Next Actions
1. **Check Current Status:** Review phase progress and active tasks
2. **Pick Up In-Progress Work:** Look for tasks with status "in-progress"  
3. **Use Context Files:** Check `contexts/phase*/context_*.md` for task details
4. **Update Progress:** Use CLI or web UI to mark tasks complete

### Key Commands
```bash
# See overall status
python cli/hdw-task.py status

# View phase progress  
python cli/hdw-task.py phases

# Start a task (creates context file)
python cli/hdw-task.py start <task-id>

# Complete a task
python cli/hdw-task.py commit <task-id>

# Generate blueprints
python src/blueprint_generator.py phase --phase 1 --save
python src/blueprint_generator.py handoff --save
```

### Web Interface
- **Dashboard:** http://localhost:5000 (hdw / HoneyDuo2025!)
- **Tasks:** Phase-organized task management
- **Reports:** Generate Claude handoff reports

## 🎯 Design Principles

1. **Keep It Simple** - No over-engineering, focus on practical handoffs
2. **Document Everything** - Auto-generate context and decisions  
3. **Phase-Based Organization** - Break work into manageable phases
4. **Session Continuity** - Enable seamless Claude handoffs
5. **Test by Using** - Build the system using the system itself

## 📞 Need Help?

- **Context Files:** Check `contexts/phase*/` for task-specific information
- **Recent Work:** Look at `claude_reports/` for latest handoff reports
- **System Status:** Use web dashboard or CLI status commands
- **Phase Progress:** Generated blueprints show detailed phase status

---

**Ready to continue development!** 🚀

This handoff document contains everything needed to understand the current state and continue work seamlessly.
"""
        
        return handoff
    
    def save_blueprint(self, content: str, filename: str) -> str:
        """Save blueprint to docs/blueprints/ directory."""
        filepath = self.blueprints_path / filename
        
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return str(filepath)
        except Exception as e:
            print(f"Error saving blueprint to {filepath}: {e}")
            return None
    
    def save_session_handoff(self, content: str) -> str:
        """Save session handoff document."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{timestamp}.md"
        filepath = self.sessions_path / filename
        
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return str(filepath)
        except Exception as e:
            print(f"Error saving session handoff to {filepath}: {e}")
            return None
    
    def auto_generate_on_completion(self, task_id: str) -> Dict[str, str]:
        """Auto-generate blueprint when a task is completed."""
        results = {}
        
        # Get task info
        tasks_data = self.task_manager.load_tasks()
        task = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
        
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # Generate task blueprint
        task_blueprint = self.generate_task_blueprint(task_id, task)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        task_filename = f"task_{task_id}_{timestamp}.md"
        task_filepath = self.save_blueprint(task_blueprint, task_filename)
        if task_filepath:
            results["task_blueprint"] = task_filepath
        
        # Check if phase is complete and generate phase blueprint
        phase_id = task.get('phase', 0)
        phase_progress = self.task_manager.get_phase_progress()
        
        if phase_id in phase_progress and phase_progress[phase_id]['percentage'] == 100:
            phase_blueprint = self.generate_phase_blueprint(phase_id=phase_id)
            phase_filename = f"phase{phase_id}_completed_{timestamp}.md"
            phase_filepath = self.save_blueprint(phase_blueprint, phase_filename)
            if phase_filepath:
                results["phase_blueprint"] = phase_filepath
        
        return results

def main():
    """CLI interface for blueprint generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate blueprint documentation")
    parser.add_argument('command', choices=['task', 'phase', 'handoff', 'auto'], 
                       help="Type of documentation to generate")
    parser.add_argument('--task', '-t', help="Task ID for task blueprint")
    parser.add_argument('--phase', '-p', help="Phase name/ID for phase blueprint")
    parser.add_argument('--phase-id', type=int, help="Specific phase ID")
    parser.add_argument('--output', '-o', help="Output filename")
    parser.add_argument('--save', '-s', action='store_true', 
                       help="Save to docs directory")
    parser.add_argument('--project-root', default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    generator = BlueprintGenerator(args.project_root)
    
    if args.command == 'task':
        if not args.task:
            print("Task ID required for task blueprint")
            return
        
        content = generator.generate_task_blueprint(args.task)
        
        if args.save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = args.output or f"task_{args.task}_{timestamp}.md"
            filepath = generator.save_blueprint(content, filename)
            print(f"Task blueprint saved to: {filepath}")
        else:
            print(content)
    
    elif args.command == 'phase':
        content = generator.generate_phase_blueprint(args.phase, args.phase_id)
        
        if args.save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            phase_name = args.phase or str(args.phase_id or "current")
            filename = args.output or f"phase_{phase_name}_{timestamp}.md"
            filepath = generator.save_blueprint(content, filename)
            print(f"Phase blueprint saved to: {filepath}")
        else:
            print(content)
    
    elif args.command == 'handoff':
        content = generator.generate_session_handoff()
        
        if args.save:
            filepath = generator.save_session_handoff(content)
            print(f"Session handoff saved to: {filepath}")
        else:
            print(content)
    
    elif args.command == 'auto':
        if not args.task:
            print("Task ID required for auto-generation")
            return
        
        results = generator.auto_generate_on_completion(args.task)
        if "error" in results:
            print(f"Error: {results['error']}")
        else:
            print("Auto-generated blueprints:")
            for doc_type, filepath in results.items():
                print(f"  {doc_type}: {filepath}")

if __name__ == "__main__":
    main()