# Context for Task: bruce-branding

**Phase:** 2 - Make Bruce Portable
**Description:** Rebrand everything from HDW to Bruce
**Expected Output:** All UI/CLI showing Bruce branding


## Architecture Context: Where This Task Fits

Current Task: bruce-branding
Component: CLI Interface

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

## Decision History

Key decisions from this phase that may impact your work:

- No previous decisions found in this phase

## Context Documentation:

No additional context files specified.
