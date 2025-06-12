# Context for Task: bruce-init

**Project:** Bruce Project
**Phase:** 2 - Make Bruce Portable
**Description:** Create 'bruce init' command
**Expected Output:** Command that sets up Bruce in any directory

## Project Configuration

- **Config loaded:** Yes
- **Project type:** general
- **Contexts directory:** contexts
- **Blueprints directory:** docs/blueprints


## Architecture Context: Where This Task Fits

Current Task: bruce-init
Component: CLI Interface
Project: Bruce Project

System Overview:
┌─────────────────────┐     ┌─────────────────────┐
│   CLI Interface     │ ← YOU ARE HERE     │   Web Dashboard     │
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
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Config Sys  │ │Context Sys  │ │Blueprint Gen│
│(config mgr) │ │(contexts/) │ │(blueprints)│
└─────────────┘ └─────────────┘ └─────────────┘

Data Flow:
1. User triggers task via CLI/Web
2. TaskManager processes request  
3. Config System provides settings
4. Context System generates/reads context
5. Work happens (YOU!)
6. Blueprint Generator creates documentation

## Related Completed Tasks

These completed tasks might provide useful context:

### bruce-config: Create bruce.yaml config system
- **Output:** Config loader and bruce.yaml format
- **Status:** completed

### bruce-branding: Rebrand everything from HDW to Bruce
- **Output:** All UI/CLI showing Bruce branding
- **Status:** completed

### hello-world: Create a simple hello world function
- **Output:** hello_world() function in src/utils.py
- **Status:** completed

## Decision History

Key decisions from this phase that may impact your work:

- No previous decisions found in this phase

## Context Documentation:

No additional context files specified.
