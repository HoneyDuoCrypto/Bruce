# Honey Duo Wealth AI Trading System

## Project Management & Development Framework

This repository contains the collaborative AI-driven trading platform development framework.

### Quick Start

```bash
cd honey_duo_wealth
python cli/hdw-task.py --help
```

### Architecture

- **docs/**: Planning documentation and specifications
- **src/**: Production code modules  
- **cli/**: Task management CLI tools
- **tests/**: Unit and integration tests
- **tasks.yaml**: Microtask definitions and status tracking

### Workflow

1. ChatGPT defines tasks in `tasks.yaml`
2. Claude implements via `hdw-task start <task-id>`
3. Auto-commit and status updates
4. Integration and validation

