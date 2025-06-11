# 📋 Phase 2: Make Bruce Portable Blueprint

**Status:** ⏳ NOT STARTED
**Progress:** 0/5 tasks (0.0%)
**Last Updated:** 2025-06-11 10:29:38
**Source of Truth:** This document contains ALL information for Phase 2

---

## 🎯 Phase Overview

Complete PM system for seamless Claude handoffs

### 📊 Progress Summary
- **⚪ Total Tasks:** 5
- **✅ Completed:** 0 
- **🔄 In Progress:** 0
- **⏳ Pending:** 5
- **🚫 Blocked:** 0

### Progress Visualization
`[░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.0%`

---

## 📋 Task Implementation Details

### ⏳ Pending Tasks

#### bruce-branding
**Description:** Rebrand everything from HDW to Bruce
**Expected Output:** All UI/CLI showing Bruce branding
**Status:** pending

#### bruce-config
**Description:** Create bruce.yaml config system
**Expected Output:** Config loader and bruce.yaml format
**Status:** pending

#### bruce-init
**Description:** Create 'bruce init' command
**Expected Output:** Command that sets up Bruce in any directory
**Status:** pending

#### relative-paths
**Description:** Make all paths project-relative
**Expected Output:** Updated path handling throughout
**Status:** pending

#### blueprint-import
**Description:** Build blueprint and the build import feature
**Expected Output:** UI and API for importing phase designs
**Status:** pending

---

## 🔧 Implementation Details

### Enhanced System Components

#### TaskManager Methods
```python
# Context & Enhancement Methods
get_context(self, context_paths)
find_related_tasks(self, task_id, limit)
generate_architecture_context(self, task_id)
generate_enhanced_context(self, task_id)

# Phase Management Methods
_update_phase_file(self, phase_file, task_id, updated_task)
get_phase_progress(self)

# Core Methods
load_tasks(self)
save_task_updates(self, task_id, updates)
cmd_start(self, task_id, enhanced)
```

#### API Endpoints (Enhanced Analysis)

**hdw_secure.py:** (8 endpoints)
- Other endpoints: 8 additional endpoints

**hdw_complete.py:** (18 endpoints)
- Context Management:
  - `GET /api/preview_context/<task_id>`
  - `GET /api/related_tasks/<task_id>`
- Blueprint Generation:
  - `POST /api/generate_blueprint`
- Other endpoints: 15 additional endpoints

**Total API Endpoints:** 26

#### Frontend Enhancements

**JavaScript Functions (33):**
- `addContextField()` - Enhanced context UI
- `addEditContextField()` - Enhanced context UI
- `closeModal()` - Enhanced context UI
- `previewContext()` - Enhanced context UI
- `previewContextInModal()` - Enhanced context UI
- `showRelatedTasks()` - Enhanced context UI

**Modal Dialogs:**
- contextModal
- modalContent

**UI Components:**
- Enhanced Start Dialog
- Context Modal System
- Enhanced Context Toggle
- Context Preview Feature
- Related Tasks Viewer
---

## 🏗️ System Architecture

### Component Overview
```
📁 HONEY DUO WEALTH - PHASE 2 ARCHITECTURE
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
    ├── Phase Definition (phases/phase2_*.yml)
    ├── Context Files (contexts/phase2/)
    └── This Blueprint (docs/blueprints/phase_2_blueprint.md)
```

### 🔄 Data Flow Analysis


---

## 🚀 Session Handoff Information

### For New Claude Sessions

**You're working on:** Phase 2 of the Honey Duo Wealth project management system.

**Goal:** Build a system for seamless Claude session handoffs

**Current Status:** 0/5 tasks completed (0.0%)

### Quick Start Commands
```bash
# Check current status
python cli/hdw-task.py status

# See phase progress  
python cli/hdw-task.py phases

# List available tasks
python cli/hdw-task.py list --phase 2

# Start next task (with enhanced context)
python cli/hdw-task.py start <task-id>

# Start with basic context
python cli/hdw-task.py start <task-id> --basic
```

### Key Files for This Phase
- **Phase Definition:** `phases/phase2_*.yml`
- **Context Files:** `contexts/phase2/`
- **This Blueprint:** `docs/blueprints/phase_2_blueprint.md`

---

**🎯 This is the complete source of truth for Phase 2. Everything you need to continue development is documented above.**

*Last updated: 2025-06-11 10:29:38*
