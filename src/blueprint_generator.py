#!/usr/bin/env python3
"""
Phase Blueprint Generator - One Source of Truth Per Phase
Creates comprehensive phase documents containing tasks, architecture, handoffs, and technical details
"""

import os
import sys
import re
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import glob

# Add src to path to import TaskManager
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.task_manager import TaskManager

class SystemArchitectureAnalyzer:
    """Analyzes actual code to map system connections and dependencies."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.python_files = []
        self.imports_map = {}
        self.api_endpoints = {}
        self.file_dependencies = {}
        self.data_flows = {}
        
    def analyze_project(self) -> Dict[str, Any]:
        """Perform complete system analysis."""
        self._find_python_files()
        self._analyze_imports()
        self._analyze_api_endpoints()
        self._analyze_file_dependencies()
        self._analyze_data_flows()
        
        return {
            'files': self.python_files,
            'imports': self.imports_map,
            'api_endpoints': self.api_endpoints,
            'dependencies': self.file_dependencies,
            'data_flows': self.data_flows
        }
    
    def _find_python_files(self):
        """Find all Python files in the project."""
        patterns = ['*.py', 'cli/*.py', 'src/*.py', 'tests/*.py']
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.project_root)
                    self.python_files.append(str(rel_path))
    
    def _analyze_imports(self):
        """Analyze import relationships between files."""
        for file_path in self.python_files:
            full_path = self.project_root / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                imports = []
                # Find import statements
                import_lines = re.findall(r'^(?:from\s+[\w.]+\s+)?import\s+[\w.,\s*]+', content, re.MULTILINE)
                for line in import_lines:
                    imports.append(line.strip())
                
                # Find local imports (from src, from cli, etc.)
                local_imports = []
                for imp in imports:
                    if any(local in imp for local in ['src.', 'cli.', 'from src', 'from cli']):
                        local_imports.append(imp)
                
                self.imports_map[file_path] = {
                    'all_imports': imports,
                    'local_imports': local_imports
                }
                
            except Exception as e:
                self.imports_map[file_path] = {'error': str(e)}
    
    def _analyze_api_endpoints(self):
        """Find Flask/API endpoints and their relationships."""
        for file_path in self.python_files:
            full_path = self.project_root / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find Flask routes
                routes = re.findall(r"@app\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?\)", content)
                if routes:
                    self.api_endpoints[file_path] = []
                    for route, methods in routes:
                        methods_list = [m.strip().strip('\'"') for m in methods.split(',')] if methods else ['GET']
                        self.api_endpoints[file_path].append({
                            'route': route,
                            'methods': methods_list
                        })
                
            except Exception as e:
                pass
    
    def _analyze_file_dependencies(self):
        """Analyze which files depend on which others."""
        for file_path in self.python_files:
            full_path = self.project_root / file_path
            dependencies = {
                'reads_files': [],
                'writes_files': [],
                'config_files': []
            }
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find file operations
                file_ops = re.findall(r'(?:open|Path|load|save|read|write)\([\'"]([^\'"]+)[\'"]', content)
                for file_op in file_ops:
                    if any(ext in file_op for ext in ['.yaml', '.yml', '.json', '.md', '.txt']):
                        if 'w' in content[content.find(file_op):content.find(file_op)+50]:
                            dependencies['writes_files'].append(file_op)
                        else:
                            dependencies['reads_files'].append(file_op)
                
                # Find config files
                config_patterns = ['.yaml', '.yml', '.json', '.env']
                for pattern in config_patterns:
                    matches = re.findall(rf'[\'"]([^\'\"]*{pattern})[\'"]', content)
                    dependencies['config_files'].extend(matches)
                
                self.file_dependencies[file_path] = dependencies
                
            except Exception as e:
                self.file_dependencies[file_path] = {'error': str(e)}
    
    def _analyze_data_flows(self):
        """Analyze how data flows through the system."""
        flow_patterns = {
            'YAML → TaskManager': [],
            'TaskManager → Context Files': [],
            'CLI → TaskManager': [],
            'Web UI → TaskManager': [],
            'TaskManager → Git': [],
            'Context → Blueprint': []
        }
        
        for file_path in self.python_files:
            full_path = self.project_root / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Identify data flow patterns
                if 'TaskManager' in content and any(ext in content for ext in ['.yaml', '.yml']):
                    flow_patterns['YAML → TaskManager'].append(file_path)
                
                if 'context' in content.lower() and 'taskmanager' in content.lower():
                    flow_patterns['TaskManager → Context Files'].append(file_path)
                
                if 'TaskManager' in content and 'argparse' in content:
                    flow_patterns['CLI → TaskManager'].append(file_path)
                
                if 'TaskManager' in content and 'Flask' in content:
                    flow_patterns['Web UI → TaskManager'].append(file_path)
                
                if 'git' in content.lower() and 'commit' in content.lower():
                    flow_patterns['TaskManager → Git'].append(file_path)
                
                if 'blueprint' in content.lower() and 'context' in content.lower():
                    flow_patterns['Context → Blueprint'].append(file_path)
                    
            except Exception:
                continue
        
        self.data_flows = flow_patterns

class PhaseDocumentManager:
    """Manages phase documents - one comprehensive document per phase."""
    
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.blueprints_dir = docs_dir / "blueprints"
        self.blueprints_dir.mkdir(parents=True, exist_ok=True)
    
    def get_phase_document_path(self, phase_id: int) -> Path:
        """Get the path for a phase document."""
        return self.blueprints_dir / f"phase_{phase_id}_blueprint.md"
    
    def backup_completed_phase(self, phase_id: int) -> Optional[str]:
        """Backup a completed phase document."""
        current_doc = self.get_phase_document_path(phase_id)
        if not current_doc.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        backup_name = f"phase_{phase_id}_completed_{timestamp}.md"
        backup_path = self.blueprints_dir / backup_name
        
        try:
            # Copy current to completed backup
            with open(current_doc, 'r') as src, open(backup_path, 'w') as dst:
                content = src.read()
                # Add completion header
                completion_header = f"""# ✅ PHASE {phase_id} COMPLETED

**Completion Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status:** All tasks completed successfully
**This is the final archived version of Phase {phase_id}**

---

"""
                dst.write(completion_header + content)
            
            print(f"📦 Phase {phase_id} completed and archived: {backup_name}")
            return str(backup_path)
            
        except Exception as e:
            print(f"⚠️  Couldn't backup phase {phase_id}: {e}")
            return None

class PhaseBlueprintGenerator:
    """Generates comprehensive phase blueprints - one source of truth per phase."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.task_manager = TaskManager(self.project_root)
        self.analyzer = SystemArchitectureAnalyzer(self.project_root)
        self.docs_path = self.project_root / "docs"
        self.doc_manager = PhaseDocumentManager(self.docs_path)
        
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
                'implementation_notes': self._extract_implementation_notes(content),
                'decisions': self._extract_decisions(content)
            }
            
            return context_data
            
        except Exception as e:
            print(f"Error reading context file {context_file}: {e}")
            return None
    
    def _extract_implementation_notes(self, content: str) -> List[str]:
        """Extract implementation details from task notes."""
        notes = []
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
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in 
                   ['decision', 'chose', 'approach', 'strategy', 'because', 'rationale']):
                decisions.append(line)
        return decisions
    
    def generate_comprehensive_phase_blueprint(self, phase_id: int) -> str:
        """Generate the ONE comprehensive blueprint for a phase."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get all data needed
        tasks_data = self.task_manager.load_tasks()
        phase_progress = self.task_manager.get_phase_progress()
        architecture = self.analyzer.analyze_project()
        
        if phase_id not in phase_progress:
            return f"Phase {phase_id} not found."
        
        progress = phase_progress[phase_id]
        phase_info = tasks_data.get("phases", {}).get(str(phase_id), {})
        
        # Determine phase status
        if progress['percentage'] == 100:
            status_badge = "✅ COMPLETE"
            status_color = "🟢"
        elif progress['completed'] > 0:
            status_badge = "🔄 IN PROGRESS"
            status_color = "🟡"
        else:
            status_badge = "⏳ NOT STARTED"
            status_color = "⚪"
        
        blueprint = f"""# 📋 Phase {phase_id}: {progress['name']} Blueprint

**Status:** {status_badge}
**Progress:** {progress['completed']}/{progress['total']} tasks ({progress['percentage']:.1f}%)
**Last Updated:** {timestamp}
**Source of Truth:** This document contains ALL information for Phase {phase_id}

---

## 🎯 Phase Overview

{phase_info.get('description', 'Complete PM system for seamless Claude handoffs')}

### 📊 Progress Summary
- **{status_color} Total Tasks:** {progress['total']}
- **✅ Completed:** {progress['completed']} 
- **🔄 In Progress:** {progress['in_progress']}
- **⏳ Pending:** {progress['pending']}
- **🚫 Blocked:** {progress['blocked']}

### Progress Visualization
"""
        
        # Add progress bar
        bar_length = 50
        filled = int(bar_length * progress['percentage'] / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        blueprint += f"`[{bar}] {progress['percentage']:.1f}%`\n\n"
        
        # Get all tasks for this phase
        phase_tasks = [t for t in tasks_data.get("tasks", []) if t.get("phase", 0) == phase_id]
        
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
        
        blueprint += """---

## 📋 Task Implementation Details

"""
        
        # Add detailed task information
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
                    blueprint += self._generate_detailed_task_section(task)
        
        blueprint += """---

## 🏗️ System Architecture

### Component Overview
```
📁 HONEY DUO WEALTH - PHASE """ + str(phase_id) + """ ARCHITECTURE
│
├── 🧠 CORE ENGINE
│   ├── TaskManager (src/task_manager.py)
│   │   ├── → reads: phases/*.yml, tasks.yaml
│   │   ├── → writes: contexts/phase*/context_*.md  
│   │   └── → manages: task status, progress tracking
│   │
│   └── BlueprintGenerator (src/blueprint_generator.py)
│       ├── → reads: context files, task data, system code
│       ├── → analyzes: imports, dependencies, data flows
│       └── → writes: docs/blueprints/phase_*_blueprint.md
│
├── 🖥️ USER INTERFACES  
│   ├── CLI Interface (cli/hdw-task.py)
│   │   ├── → imports: TaskManager
│   │   ├── → commands: start, commit, block, status, phases
│   │   └── → triggers: git operations, blueprint generation
│   │
│   └── Web Dashboard (hdw_complete.py)
│       ├── → imports: TaskManager
│       ├── → serves: Flask web interface
│       └── → endpoints: /api/start_task, /api/complete_task
│
└── 📄 DATA LAYER
    ├── Phase Definition (phases/phase""" + str(phase_id) + """_*.yml)
    ├── Context Files (contexts/phase""" + str(phase_id) + """/)
    └── This Blueprint (docs/blueprints/phase_""" + str(phase_id) + """_blueprint.md)
```

### 🔄 Data Flow Analysis
"""
        
        # Add data flow information
        for flow_name, files in architecture['data_flows'].items():
            if files:
                blueprint += f"**{flow_name}:**\n"
                for file_path in files[:2]:  # Show top 2 files
                    blueprint += f"- `{file_path}`\n"
                blueprint += "\n"
        
        blueprint += """### 🔗 Integration Points

"""
        
        # Add API endpoints if any
        if architecture['api_endpoints']:
            blueprint += "**Web API Endpoints:**\n"
            for file_path, endpoints in architecture['api_endpoints'].items():
                if endpoints:
                    blueprint += f"- `{file_path}`: {len(endpoints)} endpoints\n"
                    for endpoint in endpoints[:3]:  # Show top 3
                        methods = ', '.join(endpoint['methods'])
                        blueprint += f"  - `{methods} {endpoint['route']}`\n"
            blueprint += "\n"
        
        # Add file dependencies
        blueprint += "**File Dependencies:**\n"
        for file_path, deps in architecture['dependencies'].items():
            if deps.get('reads_files') or deps.get('writes_files'):
                blueprint += f"- `{file_path}`\n"
                if deps.get('reads_files'):
                    blueprint += f"  📖 Reads: {', '.join(deps['reads_files'][:2])}\n"
                if deps.get('writes_files'):
                    blueprint += f"  ✍️ Writes: {', '.join(deps['writes_files'][:2])}\n"
        
        blueprint += """

---

## 🚀 Session Handoff Information

### For New Claude Sessions

**You're working on:** Phase """ + str(phase_id) + f""" of the Honey Duo Wealth project management system.

**Goal:** {phase_info.get('description', 'Build a system for seamless Claude session handoffs')}

**Current Status:** {progress['completed']}/{progress['total']} tasks completed ({progress['percentage']:.1f}%)

### Quick Start Commands
```bash
# Check current status
python cli/hdw-task.py status

# See phase progress  
python cli/hdw-task.py phases

# List available tasks
python cli/hdw-task.py list --phase {phase_id}

# Start next task
python cli/hdw-task.py start <task-id>
```

### Next Immediate Actions
"""
        
        # Add next steps based on current progress
        if progress['percentage'] == 100:
            blueprint += f"""
**🎉 Phase {phase_id} Complete!**
- All tasks have been implemented successfully
- System architecture is stable and documented
- Ready to move to next phase or project completion

### Completion Summary
- ✅ All {progress['total']} tasks completed
- ✅ System architecture documented  
- ✅ Integration points verified
- ✅ Session handoff capability proven
"""
        else:
            if tasks_by_status['blocked']:
                blueprint += f"1. **Resolve {len(tasks_by_status['blocked'])} blocked tasks**\n"
                for task in tasks_by_status['blocked'][:2]:
                    blueprint += f"   - {task['id']}: {task.get('description', '')}\n"
                blueprint += "\n"
            
            if tasks_by_status['in-progress']:
                blueprint += f"2. **Complete {len(tasks_by_status['in-progress'])} in-progress tasks**\n"
                for task in tasks_by_status['in-progress']:
                    blueprint += f"   - {task['id']}: {task.get('description', '')}\n"
                blueprint += "\n"
            
            if tasks_by_status['pending']:
                blueprint += f"3. **Start next pending task** ({len(tasks_by_status['pending'])} remaining)\n"
                next_task = tasks_by_status['pending'][0]
                blueprint += f"   - **Recommended:** {next_task['id']} - {next_task.get('description', '')}\n"
                blueprint += f"   - **Output:** {next_task.get('output', '')}\n"
                blueprint += "\n"
        
        blueprint += f"""
### Key Files for This Phase
- **Phase Definition:** `phases/phase{phase_id}_*.yml`
- **Context Files:** `contexts/phase{phase_id}/`
- **This Blueprint:** `docs/blueprints/phase_{phase_id}_blueprint.md`

---

**🎯 This is the complete source of truth for Phase {phase_id}. Everything you need to continue development is documented above.**

*Last updated: {timestamp}*
"""
        
        return blueprint
    
    def _generate_detailed_task_section(self, task: Dict[str, Any]) -> str:
        """Generate detailed section for a single task."""
        task_id = task['id']
        status = task.get('status', 'pending')
        
        section = f"""#### {task_id}
**Description:** {task.get('description', '')}
**Expected Output:** {task.get('output', 'Not specified')}
**Status:** {status}
"""
        
        if task.get('updated'):
            section += f"**Last Updated:** {task['updated'][:19]}\n"
        
        # Add acceptance criteria if available
        if task.get('acceptance_criteria'):
            section += f"**Acceptance Criteria:**\n"
            for criteria in task['acceptance_criteria']:
                section += f"- {criteria}\n"
        
        # Add context information if available
        context_data = self.get_task_context_content(task_id, task.get('phase'))
        if context_data:
            if context_data['implementation_notes']:
                section += f"**Implementation Notes:**\n"
                for note in context_data['implementation_notes'][:2]:  # Show top 2
                    section += f"- {note}\n"
            
            if context_data['decisions']:
                section += f"**Key Decisions:**\n"
                for decision in context_data['decisions'][:2]:  # Show top 2
                    section += f"- {decision}\n"
        
        # Add task history
        if task.get('notes'):
            section += f"**History:**\n"
            for note in task['notes'][-3:]:  # Show last 3 notes
                timestamp = note.get('timestamp', 'Unknown time')[:19]
                note_text = note.get('note', '')
                section += f"- **{timestamp}:** {note_text}\n"
        
        section += "\n"
        return section
    
    def generate_session_handoff(self) -> str:
        """Generate comprehensive session handoff with architecture context."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        handoff = f"""# 🤝 Claude Session Handoff - Technical Deep Dive

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Session ID:** session_{timestamp}
**Project:** Honey Duo Wealth Project Management System

## 🎯 Mission Briefing

You're joining development of a **multi-phase project management system** designed for seamless Claude session handoffs. The system tracks tasks across phases, auto-generates documentation, and preserves context between sessions.

## 📊 Current Development Status

"""
        
        # Add current progress
        phase_progress = self.task_manager.get_phase_progress()
        tasks_data = self.task_manager.load_tasks()
        
        total_tasks = sum(p['total'] for p in phase_progress.values())
        total_completed = sum(p['completed'] for p in phase_progress.values())
        overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        handoff += f"**Overall Progress:** {total_completed}/{total_tasks} tasks ({overall_progress:.1f}%)\n\n"
        
        # Show what's been built and what's next
        handoff += "### ✅ What's Been Built\n"
        completed_tasks = [t for t in tasks_data.get("tasks", []) if t.get('status') == 'completed']
        for task in completed_tasks:
            handoff += f"- **{task['id']}:** {task.get('description', '')} → `{task.get('output', '')}`\n"
        
        handoff += "\n### 🔄 What You're Continuing\n"
        pending_tasks = [t for t in tasks_data.get("tasks", []) if t.get('status') == 'pending']
        for task in pending_tasks[:3]:
            handoff += f"- **{task['id']}:** {task.get('description', '')} → `{task.get('output', '')}`\n"
        
        handoff += f"""

## 🏗️ System Architecture Overview

### Core Components
```
TaskManager (src/task_manager.py)
├── Manages multi-phase task loading from YAML files
├── Handles context file generation and organization  
├── Tracks progress across phases
└── Integrates with CLI and Web UI

CLI Interface (cli/hdw-task.py)
├── Enhanced with blueprint auto-generation
├── Supports phase-aware task management
├── Triggers git operations and documentation
└── Generates Claude handoff reports

Web Dashboard (hdw_complete.py)  
├── Phase-aware progress tracking
├── RESTful API for task operations
├── Visual task management interface
├── Blueprint Generator integration
└── Integrated Claude report generation

BlueprintGenerator (src/blueprint_generator.py)
├── Analyzes system architecture automatically
├── Creates comprehensive technical blueprints
├── Maps component connections and data flows
└── Generates session handoff documents
```

## 🚀 How to Continue Development

### Immediate Commands
```bash
# Check current system status
python cli/hdw-task.py status

# See what tasks are available
python cli/hdw-task.py list

# Start a specific task
python cli/hdw-task.py start <task-id>

# Test blueprint generation
python src/blueprint_generator.py update --phase-id 1
```

### Web Interface
- **URL:** http://hdw.honey-duo.com
- **Login:** hdw / HoneyDuo2025!
- **Features:** Phase tracking, task management, blueprint generation

### Development Workflow
1. **Pick a pending task** from the list above
2. **Start the task** to generate context file
3. **Implement the required output** 
4. **Commit the task** - triggers auto-blueprint generation
5. **Generated blueprints** appear in `docs/blueprints/`

## 🎯 Next Immediate Actions

### Priority Tasks
"""
        
        for task in pending_tasks[:2]:  # Show top 2 pending
            handoff += f"- **{task['id']}:** {task.get('description', '')}\n"
        
        handoff += """

### Success Metrics
- ✅ Any Claude session can pick up work immediately  
- ✅ System generates comprehensive technical blueprints
- ✅ Architecture connections are clearly mapped
- ✅ Documentation stays current automatically

---

**🚀 Ready to continue development!** The system is designed to support you with context, documentation, and clear next steps.
"""
        
        return handoff
    
    def generate_system_architecture_blueprint(self) -> str:
        """Generate comprehensive system architecture blueprint."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Analyze the actual system
        architecture = self.analyzer.analyze_project()
        
        # Get current progress
        phase_progress = self.task_manager.get_phase_progress()
        tasks_data = self.task_manager.load_tasks()
        
        blueprint = f"""# 🏗️ Honey Duo Wealth System Architecture Blueprint

**Generated:** {timestamp}
**System Analysis:** {len(architecture['files'])} Python files analyzed

## 📊 Project Status Summary

"""
        
        # Add progress overview
        total_tasks = sum(p['total'] for p in phase_progress.values())
        total_completed = sum(p['completed'] for p in phase_progress.values())
        overall_progress = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        blueprint += f"**Overall Progress:** {total_completed}/{total_tasks} tasks ({overall_progress:.1f}%)\n\n"
        
        blueprint += f"""## 🏗️ System Architecture Map

### Core Components & Connections

```
📁 HONEY DUO WEALTH PROJECT MANAGEMENT SYSTEM
│
├── 🧠 CORE ENGINE
│   ├── TaskManager (src/task_manager.py)
│   │   ├── → reads: phases/*.yml, tasks.yaml
│   │   ├── → writes: contexts/phase*/context_*.md  
│   │   ├── → manages: task status, progress tracking
│   │   └── → provides: multi-phase support, context generation
│   │
│   └── BlueprintGenerator (src/blueprint_generator.py)
│       ├── → reads: context files, task data, system code
│       ├── → analyzes: imports, dependencies, data flows
│       ├── → writes: docs/blueprints/, docs/sessions/
│       └── → provides: architecture mapping, session handoffs
│
├── 🖥️ USER INTERFACES  
│   ├── CLI Interface (cli/hdw-task.py)
│   │   ├── → imports: TaskManager
│   │   ├── → commands: start, commit, block, status, phases
│   │   ├── → triggers: git operations, blueprint generation
│   │   └── → generates: Claude handoff reports
│   │
│   └── Web Dashboard (hdw_complete.py)
│       ├── → imports: TaskManager
│       ├── → serves: Flask web interface
│       ├── → endpoints: /api/start_task, /api/complete_task, /api/generate_blueprint
│       ├── → provides: visual progress tracking, task management
│       └── → features: blueprint generator UI, phase management
│
└── 📄 DATA & CONFIGURATION
    ├── Phase Definitions (phases/*.yml)
    │   └── → defines: tasks, acceptance criteria, dependencies
    │
    ├── Context Files (contexts/phase*/)
    │   └── → contains: task context, implementation notes
    │
    ├── Generated Documentation (docs/)
    │   ├── blueprints/ → system architecture, progress reports
    │   └── sessions/ → Claude handoff documents
    │
    └── Legacy Support (tasks.yaml)
        └── → backward compatibility with original task format
```

## 🔄 Data Flow Architecture

"""
        
        # Add data flow analysis
        for flow_name, files in architecture['data_flows'].items():
            if files:
                blueprint += f"### {flow_name}\n"
                for file_path in files[:2]:  # Show top 2 files
                    blueprint += f"- `{file_path}`\n"
                blueprint += "\n"
        
        blueprint += """## 🔗 Component Integration Points

### Current Integrations
- **CLI ↔ TaskManager:** Full integration with multi-phase support
- **TaskManager ↔ YAML Files:** Reads phase definitions and legacy tasks  
- **TaskManager ↔ Context Files:** Organized context generation by phase
- **CLI ↔ Git:** Automatic commits on task completion
- **CLI ↔ Blueprint Generator:** Auto-generation on task completion
- **Web UI ↔ TaskManager:** Phase-aware dashboard and task management
- **Web UI ↔ Blueprint Generator:** Integrated generator interface

---

**🎯 This blueprint provides a complete technical map of system connections, data flows, and integration points.**
"""
        
        return blueprint
    
    def update_phase_blueprint(self, phase_id: int) -> str:
        """Update the comprehensive phase blueprint."""
        content = self.generate_comprehensive_phase_blueprint(phase_id)
        doc_path = self.doc_manager.get_phase_document_path(phase_id)
        
        # Save the updated document
        with open(doc_path, 'w') as f:
            f.write(content)
        
        print(f"📋 Updated Phase {phase_id} blueprint: {doc_path.name}")
        return str(doc_path)
    
    def complete_phase(self, phase_id: int) -> str:
        """Mark a phase as complete and archive the blueprint."""
        # First update the blueprint one final time
        self.update_phase_blueprint(phase_id)
        
        # Then backup the completed phase
        backup_path = self.doc_manager.backup_completed_phase(phase_id)
        
        if backup_path:
            print(f"✅ Phase {phase_id} marked as complete and archived!")
            return backup_path
        else:
            return f"Phase {phase_id} blueprint updated but archiving failed"
    
    def auto_generate_on_completion(self, task_id: str) -> Dict[str, str]:
        """Auto-update phase blueprint when tasks complete."""
        results = {}
        
        try:
            # Find which phase this task belongs to
            tasks_data = self.task_manager.load_tasks()
            task = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
            
            if not task:
                return {"error": f"Task {task_id} not found"}
            
            phase_id = task.get('phase', 1)
            
            # Update the phase blueprint
            blueprint_path = self.update_phase_blueprint(phase_id)
            results["phase_blueprint"] = blueprint_path
            
            # Check if phase is now complete
            phase_progress = self.task_manager.get_phase_progress()
            if phase_id in phase_progress and phase_progress[phase_id]['percentage'] == 100:
                completed_path = self.complete_phase(phase_id)
                results["phase_completed"] = completed_path
            
            return results
            
        except Exception as e:
            return {"error": f"Phase blueprint update failed: {e}"}

def main():
    """CLI interface for phase blueprint generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate comprehensive phase blueprints")
    parser.add_argument('command', choices=['phase', 'complete', 'update', 'handoff', 'architecture'], 
                       help="Command to execute")
    parser.add_argument('--phase-id', type=int, default=1, help="Phase ID")
    parser.add_argument('--project-root', default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    generator = PhaseBlueprintGenerator(args.project_root)
    
    if args.command == 'phase':
        content = generator.generate_comprehensive_phase_blueprint(args.phase_id)
        print(content)
    
    elif args.command == 'update':
        filepath = generator.update_phase_blueprint(args.phase_id)
        print(f"Phase {args.phase_id} blueprint updated: {filepath}")
    
    elif args.command == 'complete':
        backup_path = generator.complete_phase(args.phase_id)
        print(f"Phase {args.phase_id} completed: {backup_path}")
    
    elif args.command == 'handoff':
        content = generator.generate_session_handoff()
        print(content)
    
    elif args.command == 'architecture':
        content = generator.generate_system_architecture_blueprint()
        print(content)

if __name__ == "__main__":
    main()