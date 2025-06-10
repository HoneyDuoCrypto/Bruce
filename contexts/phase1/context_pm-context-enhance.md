# Context for Task: pm-context-enhance

**Phase:** 1 - Project Management System
**Description:** Include related tasks and decisions in context
**Expected Output:** Enhanced context generator


## Architecture Context: Where This Task Fits

Current Task: pm-context-enhance
Component: Blueprint Generator

System Overview:
┌─────────────────────┐     ┌─────────────────────┐
│   CLI Interface     │     │   Web Dashboard     │
│  (hdw-task.py)     │     │  (hdw_complete.py)  │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           └─────────┬─────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   TaskManager Core    │
         │  (task_manager.py)    │
         └───────────┬───────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌─────────────────┐     ┌─────────────────┐
│ Context System  │     │ Blueprint Gen   │ ← YOU ARE HERE
│ (contexts/)     │     │ (blueprints/)   │
└─────────────────┘     └─────────────────┘

Data Flow:
1. User triggers task via CLI/Web
2. TaskManager processes request
3. Context System generates/reads context
4. Work happens (YOU!)
5. Blueprint Generator creates documentation

## Related Completed Tasks

These completed tasks might provide useful context:

### pm-blueprint-gen: Auto-generate blueprint from completed tasks
- **Output:** src/blueprint_generator.py
- **Status:** completed

### pm-multi-phase: Update task manager to load from phases/*.yml files
- **Output:** src/task_manager.py with multi-file support
- **Status:** completed

### pm-phase-progress: Add phase progress calculation and display
- **Output:** Progress tracking per phase
- **Status:** completed

### pm-web-phases: Update web UI to show phase-based progress
- **Output:** hdw_complete.py with phase views
- **Status:** completed

## Decision History

Key decisions from this phase that may impact your work:

- No previous decisions found in this phase

## Context Documentation:

=== cli/hdw-task.py#get_context (NOT FOUND) ===
