#!/usr/bin/env python3
"""
Phase Blueprint Generator - Enhanced with Deep Code Analysis
Creates comprehensive phase documents with detailed implementation tracking
"""

import os
import sys
import re
import ast
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import glob

# Add src to path to import TaskManager
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.task_manager import TaskManager

# Import the enhanced analyzer (would be in same file in production)
class EnhancedArchitectureAnalyzer:
    """Enhanced analyzer that captures implementation details using AST."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.python_files = []
        self.class_methods = {}
        self.function_signatures = {}
        self.api_endpoints = {}
        self.frontend_features = {}
        self.git_changes = {}
        
    def analyze_project(self) -> Dict[str, Any]:
        """Perform enhanced system analysis."""
        self._find_python_files()
        self._analyze_python_code_deep()
        self._analyze_api_endpoints_detailed()
        self._analyze_frontend_features()
        
        return {
            'files': self.python_files,
            'classes': self.class_methods,
            'functions': self.function_signatures,
            'api_endpoints': self.api_endpoints,
            'frontend_features': self.frontend_features
        }
    
    def _find_python_files(self):
        """Find all Python files in the project."""
        patterns = ['*.py', 'cli/*.py', 'src/*.py']
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and '__pycache__' not in str(file_path):
                    rel_path = file_path.relative_to(self.project_root)
                    self.python_files.append(str(rel_path))
    
    def _analyze_python_code_deep(self):
        """Use AST to deeply analyze Python code structure."""
        for file_path in self.python_files:
            full_path = self.project_root / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                classes = {}
                functions = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        methods = []
                        
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                method_info = self._extract_function_info(item)
                                methods.append(method_info)
                        
                        classes[class_name] = methods
                    
                    elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                        func_info = self._extract_function_info(node)
                        functions.append(func_info)
                
                if classes:
                    self.class_methods[file_path] = classes
                if functions:
                    self.function_signatures[file_path] = functions
                    
            except Exception as e:
                self.class_methods[file_path] = {'error': str(e)}
    
    def _extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract detailed function/method information."""
        params = []
        for arg in node.args.args:
            param_info = {'name': arg.arg}
            params.append(param_info)
        
        docstring = ast.get_docstring(node)
        
        return {
            'name': node.name,
            'parameters': params,
            'docstring': docstring,
            'line_number': node.lineno
        }
    
    def _analyze_api_endpoints_detailed(self):
        """Enhanced API endpoint analysis."""
        for file_path in self.python_files:
            full_path = self.project_root / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # First, let's try a simpler approach - find all routes
                self.api_endpoints[file_path] = []
                
                # Find all @app.route or @api.route decorators
                route_pattern = r"@(?:app|api)\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?\)"
                route_matches = list(re.finditer(route_pattern, content))
                
                for match in route_matches:
                    route = match.group(1)
                    methods = match.group(2)
                    methods_list = [m.strip().strip('\'"') for m in methods.split(',')] if methods else ['GET']
                    
                    # Now find the next function definition after this decorator
                    # Look for 'def function_name' after the decorator position
                    start_pos = match.end()
                    func_pattern = r"def\s+(\w+)\s*\("
                    func_match = re.search(func_pattern, content[start_pos:start_pos+500])
                    
                    if func_match:
                        func_name = func_match.group(1)
                        
                        endpoint_info = {
                            'route': route,
                            'methods': methods_list,
                            'function': func_name
                        }
                        
                        self.api_endpoints[file_path].append(endpoint_info)
                
            except Exception as e:
                # For debugging
                if 'hdw_complete' in file_path or 'debug' in str(e):
                    print(f"Error analyzing {file_path}: {e}")
    
    def _analyze_frontend_features(self):
        """Analyze frontend features in HTML/JS embedded in Python files."""
        for file_path in self.python_files:
            if 'hdw_complete' in file_path or 'web' in file_path.lower():
                full_path = self.project_root / file_path
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    features = {
                        'javascript_functions': [],
                        'modal_dialogs': [],
                        'ui_components': []
                    }
                    
                    # Find JavaScript functions - improved pattern
                    js_func_pattern = r'function\s+(\w+)\s*\([^)]*\)|(\w+)\s*=\s*function\s*\([^)]*\)|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
                    js_matches = re.findall(js_func_pattern, content)
                    for match in js_matches:
                        # Get the non-empty group (could be in position 0, 1, or 2)
                        func_name = next((m for m in match if m), None)
                        if func_name:
                            features['javascript_functions'].append(func_name)
                    
                    # Remove duplicates and sort
                    features['javascript_functions'] = sorted(list(set(features['javascript_functions'])))
                    
                    # Find modal references
                    modals = re.findall(r'id=["\'](\w*[Mm]odal\w*)["\']', content)
                    features['modal_dialogs'] = list(set(modals))
                    
                    # Find UI components based on specific patterns
                    if 'showStartDialog' in content:
                        features['ui_components'].append('Enhanced Start Dialog')
                    if 'modal' in content.lower() and 'context' in content.lower():
                        features['ui_components'].append('Context Modal System')
                    if 'checkbox' in content.lower() and 'enhanced' in content.lower():
                        features['ui_components'].append('Enhanced Context Toggle')
                    if 'preview' in content.lower() and 'context' in content.lower():
                        features['ui_components'].append('Context Preview Feature')
                    if 'related' in content.lower() and 'tasks' in content.lower():
                        features['ui_components'].append('Related Tasks Viewer')
                    
                    if any(features.values()):
                        self.frontend_features[file_path] = features
                        
                except Exception as e:
                    print(f"Error analyzing frontend features in {file_path}: {e}")


# Original classes from blueprint generator
class SystemArchitectureAnalyzer:
    """Original analyzer for backward compatibility."""
    
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
                import_lines = re.findall(r'^(?:from\s+[\w.]+\s+)?import\s+[\w.,\s*]+', content, re.MULTILINE)
                for line in import_lines:
                    imports.append(line.strip())
                
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
                
                routes = re.findall(r"@app\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?\)", content)
                if routes:
                    self.api_endpoints[file_path] = []
                    for route, methods in routes:
                        methods_list = [m.strip().strip('\'"') for m in methods.split(',')] if methods else ['GET']
                        self.api_endpoints[file_path].append({
                            'route': route,
                            'methods': methods_list
                        })
                
            except Exception:
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
                
                file_ops = re.findall(r'(?:open|Path|load|save|read|write)\([\'"]([^\'"]+)[\'"]', content)
                for file_op in file_ops:
                    if any(ext in file_op for ext in ['.yaml', '.yml', '.json', '.md', '.txt']):
                        if 'w' in content[content.find(file_op):content.find(file_op)+50]:
                            dependencies['writes_files'].append(file_op)
                        else:
                            dependencies['reads_files'].append(file_op)
                
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
            with open(current_doc, 'r') as src, open(backup_path, 'w') as dst:
                content = src.read()
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
    """Generates comprehensive phase blueprints with enhanced implementation details."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.task_manager = TaskManager(self.project_root)
        self.analyzer = SystemArchitectureAnalyzer(self.project_root)
        self.enhanced_analyzer = EnhancedArchitectureAnalyzer(self.project_root)
        self.docs_path = self.project_root / "docs"
        self.doc_manager = PhaseDocumentManager(self.docs_path)
    
    def get_task_context_content(self, task_id: str, phase: int = None) -> Optional[Dict[str, Any]]:
        """Get context file content for a specific task."""
        if phase is not None:
            context_file = self.task_manager.contexts_dir / f"phase{phase}" / f"context_{task_id}.md"
        else:
            context_file = None
            for phase_dir in self.task_manager.contexts_dir.glob("phase*"):
                potential_file = phase_dir / f"context_{task_id}.md"
                if potential_file.exists():
                    context_file = potential_file
                    break
        
        if not context_file or not context_file.exists():
            context_file = self.project_root / f".task_context_{task_id}.md"
        
        if not context_file or not context_file.exists():
            return None
        
        try:
            with open(context_file, 'r') as f:
                content = f.read()
            
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
    
    def _generate_implementation_details_section(self, phase_id: int) -> str:
        """Generate detailed implementation section using enhanced analysis."""
        enhanced_results = self.enhanced_analyzer.analyze_project()
        
        section = """---

## 🔧 Implementation Details

### Enhanced System Components

"""
        
        # Document TaskManager enhancements
        if 'src/task_manager.py' in enhanced_results['classes']:
            tm_methods = enhanced_results['classes']['src/task_manager.py'].get('TaskManager', [])
            if tm_methods:
                section += "#### TaskManager Methods\n```python\n"
                # Group methods by category
                context_methods = [m for m in tm_methods if any(word in m['name'].lower() for word in ['context', 'related', 'enhanced'])]
                phase_methods = [m for m in tm_methods if 'phase' in m['name'].lower()]
                core_methods = [m for m in tm_methods if m['name'] in ['load_tasks', 'save_task_updates', 'cmd_start']]
                other_methods = [m for m in tm_methods if m not in context_methods + phase_methods + core_methods]
                
                if context_methods:
                    section += "# Context & Enhancement Methods\n"
                    for method in context_methods:
                        params = ', '.join([p['name'] for p in method['parameters']])
                        section += f"{method['name']}({params})\n"
                
                if phase_methods:
                    section += "\n# Phase Management Methods\n"
                    for method in phase_methods:
                        params = ', '.join([p['name'] for p in method['parameters']])
                        section += f"{method['name']}({params})\n"
                
                if core_methods:
                    section += "\n# Core Methods\n"
                    for method in core_methods:
                        params = ', '.join([p['name'] for p in method['parameters']])
                        section += f"{method['name']}({params})\n"
                
                section += "```\n\n"
        
        # Document API endpoints with details
        total_endpoints = 0
        if enhanced_results['api_endpoints']:
            section += "#### API Endpoints (Enhanced Analysis)\n"
            for file, endpoints in enhanced_results['api_endpoints'].items():
                if endpoints:
                    section += f"\n**{file}:** ({len(endpoints)} endpoints)\n"
                    total_endpoints += len(endpoints)
                    
                    # Group by functionality
                    context_endpoints = [e for e in endpoints if 'context' in e['route'] or 'related' in e['route']]
                    blueprint_endpoints = [e for e in endpoints if 'blueprint' in e['route']]
                    other_endpoints = [e for e in endpoints if e not in context_endpoints + blueprint_endpoints]
                    
                    if context_endpoints:
                        section += "- Context Management:\n"
                        for endpoint in context_endpoints:
                            section += f"  - `{', '.join(endpoint['methods'])} {endpoint['route']}`\n"
                    
                    if blueprint_endpoints:
                        section += "- Blueprint Generation:\n"
                        for endpoint in blueprint_endpoints:
                            section += f"  - `{', '.join(endpoint['methods'])} {endpoint['route']}`\n"
                    
                    if len(other_endpoints) > 5:
                        section += f"- Other endpoints: {len(other_endpoints)} additional endpoints\n"
            
            section += f"\n**Total API Endpoints:** {total_endpoints}\n\n"
        
        # Document frontend features
        if enhanced_results['frontend_features']:
            section += "#### Frontend Enhancements\n"
            for file, features in enhanced_results['frontend_features'].items():
                if features['javascript_functions']:
                    section += f"\n**JavaScript Functions ({len(features['javascript_functions'])}):**\n"
                    # Focus on context-related functions
                    context_js = [f for f in features['javascript_functions'] 
                                 if any(keyword in f.lower() for keyword in ['context', 'modal', 'preview', 'related'])]
                    if context_js:
                        for func in context_js:
                            section += f"- `{func}()` - Enhanced context UI\n"
                
                if features['modal_dialogs']:
                    section += f"\n**Modal Dialogs:**\n"
                    for modal in features['modal_dialogs']:
                        section += f"- {modal}\n"
                
                if features['ui_components']:
                    section += f"\n**UI Components:**\n"
                    for component in features['ui_components']:
                        section += f"- {component}\n"
        
        return section
    
    def generate_comprehensive_phase_blueprint(self, phase_id: int) -> str:
        """Generate the ONE comprehensive blueprint for a phase with enhanced details."""
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
        
        # Add enhanced implementation details section
        blueprint += self._generate_implementation_details_section(phase_id)
        
        # Original architecture section
        blueprint += """---

## 🏗️ System Architecture

### Component Overview
"""
        
        blueprint += self._generate_architecture_section(phase_id)
        
        blueprint += self._generate_session_handoff_section(phase_id, progress, phase_info)
        
        return blueprint
    
    def _generate_architecture_section(self, phase_id: int) -> str:
        """Generate architecture section."""
        return """```
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
                for note in context_data['implementation_notes'][:2]:
                    section += f"- {note}\n"
            
            if context_data['decisions']:
                section += f"**Key Decisions:**\n"
                for decision in context_data['decisions'][:2]:
                    section += f"- {decision}\n"
        
        # Add task history
        if task.get('notes'):
            section += f"**History:**\n"
            for note in task['notes'][-3:]:
                timestamp = note.get('timestamp', 'Unknown time')[:19]
                note_text = note.get('note', '')
                section += f"- **{timestamp}:** {note_text}\n"
        
        section += "\n"
        return section
    
    def _generate_session_handoff_section(self, phase_id: int, progress: Dict, phase_info: Dict) -> str:
        """Generate session handoff section."""
        section = """

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

# Start next task (with enhanced context)
python cli/hdw-task.py start <task-id>

# Start with basic context
python cli/hdw-task.py start <task-id> --basic
```

### Key Files for This Phase
- **Phase Definition:** `phases/phase{phase_id}_*.yml`
- **Context Files:** `contexts/phase{phase_id}/`
- **This Blueprint:** `docs/blueprints/phase_{phase_id}_blueprint.md`

---

**🎯 This is the complete source of truth for Phase {phase_id}. Everything you need to continue development is documented above.**

*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return section
    
    def generate_session_handoff(self) -> str:
        """Generate comprehensive session handoff with enhanced details."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Run enhanced analysis
        enhanced_results = self.enhanced_analyzer.analyze_project()
        
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
        
        # Show what's been built
        handoff += "### ✅ What's Been Built\n"
        completed_tasks = [t for t in tasks_data.get("tasks", []) if t.get('status') == 'completed']
        for task in completed_tasks:
            handoff += f"- **{task['id']}:** {task.get('description', '')} → `{task.get('output', '')}`\n"
        
        handoff += "\n### 🔄 What You're Continuing\n"
        pending_tasks = [t for t in tasks_data.get("tasks", []) if t.get('status') == 'pending']
        for task in pending_tasks[:3]:
            handoff += f"- **{task['id']}:** {task.get('description', '')} → `{task.get('output', '')}`\n"
        
        # Add enhanced features section
        handoff += f"""

## 🎯 Key System Features

### Enhanced Context System
- **Automatic Related Task Discovery** - Finds relevant completed work
- **Architecture Visualization** - Shows where tasks fit in the system
- **Decision History Tracking** - Preserves implementation choices
- **Rich Context Preview** - See context before starting tasks
- **Toggle Modes** - Choose between enhanced or basic context

### Implementation Highlights
"""
        
        # Add method counts
        if 'src/task_manager.py' in enhanced_results['classes']:
            tm_methods = enhanced_results['classes']['src/task_manager.py'].get('TaskManager', [])
            context_methods = [m for m in tm_methods if 'context' in m['name'].lower()]
            handoff += f"- **TaskManager**: {len(tm_methods)} methods ({len(context_methods)} for context management)\n"
        
        # Add endpoint count
        total_endpoints = sum(len(eps) for eps in enhanced_results['api_endpoints'].values())
        handoff += f"- **API Endpoints**: {total_endpoints} total endpoints\n"
        
        # Add frontend features
        if enhanced_results['frontend_features']:
            for file, features in enhanced_results['frontend_features'].items():
                if features['javascript_functions']:
                    handoff += f"- **Frontend**: {len(features['javascript_functions'])} JavaScript functions\n"
                    break
        
        handoff += self._generate_architecture_overview()
        
        return handoff
    
    def _generate_architecture_overview(self) -> str:
        """Generate architecture overview section."""
        return """

## 🏗️ System Architecture Overview

### Core Components
```
TaskManager (src/task_manager.py)
├── Manages multi-phase task loading from YAML files
├── Handles context file generation and organization  
├── Tracks progress across phases
├── Enhanced context with related tasks and decisions
└── Integrates with CLI and Web UI

CLI Interface (cli/hdw-task.py)
├── Enhanced with blueprint auto-generation
├── Supports phase-aware task management
├── --basic flag for context mode selection
├── Triggers git operations and documentation
└── Generates Claude handoff reports

Web Dashboard (hdw_complete.py)  
├── Phase-aware progress tracking
├── RESTful API for task operations
├── Visual task management interface
├── Modal dialogs for enhanced context
├── Context preview functionality
└── Related tasks viewer

BlueprintGenerator (src/blueprint_generator.py)
├── Analyzes system architecture automatically
├── Deep code analysis with AST parsing
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

# Start a specific task with enhanced context
python cli/hdw-task.py start <task-id>

# Use basic context instead
python cli/hdw-task.py start <task-id> --basic

# Test blueprint generation
python src/blueprint_generator.py update --phase-id 1
```

### Web Interface
- **URL:** http://hdw.honey-duo.com
- **Login:** hdw / HoneyDuo2025!
- **Features:** Phase tracking, task management, enhanced context, blueprint generation

---

**🚀 Ready to continue development!** The system is designed to support you with context, documentation, and clear next steps.
"""
    
    def generate_system_architecture_blueprint(self) -> str:
        """Generate comprehensive system architecture blueprint with enhanced details."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Analyze the actual system with both analyzers
        architecture = self.analyzer.analyze_project()
        enhanced_results = self.enhanced_analyzer.analyze_project()
        
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
        
        # Add enhanced component details
        blueprint += "## 🔧 System Components (Enhanced Analysis)\n\n"
        
        # Show method counts by class
        if enhanced_results['classes']:
            blueprint += "### Core Classes and Methods\n"
            for file, classes in enhanced_results['classes'].items():
                if isinstance(classes, dict) and 'error' not in classes:
                    for class_name, methods in classes.items():
                        if class_name in ['TaskManager', 'PhaseBlueprintGenerator']:
                            blueprint += f"\n**{class_name}** ({file}):\n"
                            blueprint += f"- Total Methods: {len(methods)}\n"
                            key_methods = [m for m in methods if not m['name'].startswith('_')]
                            blueprint += f"- Public Methods: {len(key_methods)}\n"
        
        # Show API endpoint summary
        total_endpoints = sum(len(eps) for eps in enhanced_results['api_endpoints'].values())
        blueprint += f"\n### API Endpoints\n"
        blueprint += f"- **Total Endpoints:** {total_endpoints}\n"
        for file, endpoints in enhanced_results['api_endpoints'].items():
            if endpoints:
                blueprint += f"- **{file}:** {len(endpoints)} endpoints\n"
        
        # Show frontend features summary
        if enhanced_results['frontend_features']:
            blueprint += f"\n### Frontend Features\n"
            for file, features in enhanced_results['frontend_features'].items():
                if features['javascript_functions']:
                    blueprint += f"- **JavaScript Functions:** {len(features['javascript_functions'])}\n"
                if features['modal_dialogs']:
                    blueprint += f"- **Modal Dialogs:** {len(features['modal_dialogs'])}\n"
                if features['ui_components']:
                    blueprint += f"- **UI Components:** {len(features['ui_components'])}\n"
        
        blueprint += f"""

## 🏗️ System Architecture Map

### Core Components & Connections

```
📁 HONEY DUO WEALTH PROJECT MANAGEMENT SYSTEM
│
├── 🧠 CORE ENGINE
│   ├── TaskManager (src/task_manager.py)
│   │   ├── → reads: phases/*.yml, tasks.yaml
│   │   ├── → writes: contexts/phase*/context_*.md  
│   │   ├── → manages: task status, progress tracking
│   │   └── → provides: multi-phase support, enhanced context generation
│   │
│   └── BlueprintGenerator (src/blueprint_generator.py)
│       ├── → reads: context files, task data, system code
│       ├── → analyzes: imports, dependencies, data flows, AST parsing
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
│       └── → features: blueprint generator UI, phase management, enhanced context
│
└── 📄 DATA & CONFIGURATION
    ├── Phase Definitions (phases/*.yml)
    │   └── → defines: tasks, acceptance criteria, dependencies
    │
    ├── Context Files (contexts/phase*/)
    │   └── → contains: task context, implementation notes, architecture diagrams
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
- **CLI ↔ TaskManager:** Full integration with multi-phase support and enhanced context
- **TaskManager ↔ YAML Files:** Reads phase definitions and legacy tasks  
- **TaskManager ↔ Context Files:** Organized context generation by phase with enhanced features
- **CLI ↔ Git:** Automatic commits on task completion
- **CLI ↔ Blueprint Generator:** Auto-generation on task completion
- **Web UI ↔ TaskManager:** Phase-aware dashboard and task management
- **Web UI ↔ Blueprint Generator:** Integrated generator interface
- **Context System ↔ Related Tasks:** Automatic discovery of related work
- **Context System ↔ Architecture Diagrams:** Visual component placement

---

**🎯 This blueprint provides a complete technical map of system connections, data flows, and integration points.**
"""
        
        return blueprint
    
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
    
    def update_phase_blueprint(self, phase_id: int) -> str:
        """Update the comprehensive phase blueprint."""
        content = self.generate_comprehensive_phase_blueprint(phase_id)
        doc_path = self.doc_manager.get_phase_document_path(phase_id)
        
        # Save the updated document
        with open(doc_path, 'w') as f:
            f.write(content)
        
        print(f"📋 Updated Phase {phase_id} blueprint: {doc_path.name}")
        return str(doc_path)
    
    def auto_generate_on_completion(self, task_id: str) -> Dict[str, str]:
        """Auto-update phase blueprint when tasks complete."""
        results = {}
        
        try:
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
    parser.add_argument('command', choices=['phase', 'complete', 'update', 'handoff', 'architecture', 'test-enhanced'], 
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
        backup_path = generator.doc_manager.backup_completed_phase(args.phase_id)
        print(f"Phase {args.phase_id} completed: {backup_path}")
    
    elif args.command == 'handoff':
        content = generator.generate_session_handoff()
        print(content)
    
    elif args.command == 'test-enhanced':
        # Test the enhanced analyzer
        analyzer = EnhancedArchitectureAnalyzer(Path(args.project_root))
        results = analyzer.analyze_project()
        
        print("=== ENHANCED ANALYSIS RESULTS ===\n")
        
        # Show methods found
        for file, classes in results['classes'].items():
            if classes and isinstance(classes, dict) and 'error' not in classes:
                print(f"\n{file}:")
                for class_name, methods in classes.items():
                    print(f"  {class_name}: ({len(methods)} methods)")
                    # Show all methods for key classes
                    if 'TaskManager' in class_name or 'hdw_complete' in file:
                        for method in methods:
                            print(f"    - {method['name']}() (line {method['line_number']})")
                    else:
                        # Show first 5 for other classes
                        for method in methods[:5]:
                            print(f"    - {method['name']}() (line {method['line_number']})")
        
        # Show API endpoints
        print("\n=== API ENDPOINTS ===")
        for file, endpoints in results['api_endpoints'].items():
            if endpoints:
                print(f"\n{file}: {len(endpoints)} endpoints")
                for endpoint in endpoints:
                    print(f"  - {endpoint['methods']} {endpoint['route']} -> {endpoint['function']}()")
        
        # Show frontend features
        print("\n=== FRONTEND FEATURES ===")
        for file, features in results['frontend_features'].items():
            print(f"\n{file}:")
            if features['javascript_functions']:
                print(f"  JS Functions ({len(features['javascript_functions'])}): {', '.join(features['javascript_functions'][:10])}")
                if len(features['javascript_functions']) > 10:
                    print(f"    ... and {len(features['javascript_functions']) - 10} more")
            if features['modal_dialogs']:
                print(f"  Modals: {', '.join(features['modal_dialogs'])}")
            if features['ui_components']:
                print(f"  UI Components: {', '.join(features['ui_components'])}")

if __name__ == "__main__":
    main()