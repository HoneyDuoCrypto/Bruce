# Context for Task: bruce-config

**Phase:** 2 - Make Bruce Portable
**Description:** Create bruce.yaml config system
**Expected Output:** Config loader and bruce.yaml format


## Architecture Context: Where This Task Fits

Current Task: bruce-config
Component: Unknown Component

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
│ Context System  │     │ Blueprint Gen   │
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
