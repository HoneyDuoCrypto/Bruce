#!/bin/bash
# HDW Quick Launcher
# Easy access to your Honey Duo Wealth project management system

HDW_PROJECT_DIR="$HOME/hdw_setup/honey_duo_wealth"

echo "🍯 Honey Duo Wealth - Quick Launcher"
echo "=================================="

# Check if project exists
if [ ! -d "$HDW_PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $HDW_PROJECT_DIR"
    echo "Please verify your project location"
    exit 1
fi

# Navigate to project directory
cd "$HDW_PROJECT_DIR"

# Check if terminal app exists
if [ ! -f "hdw_terminal.py" ]; then
    echo "⚠️  Terminal app not found, launching basic CLI instead..."
    echo "Available commands:"
    echo "  python3 cli/hdw-task.py list"
    echo "  python3 cli/hdw-task.py start <task-id>"
    echo "  python3 cli/hdw-task.py commit <task-id>"
    echo ""
    echo "📁 Current directory: $(pwd)"
    exec bash
else
    echo "🚀 Launching HDW Terminal Interface..."
    echo "📁 Project: $HDW_PROJECT_DIR"
    echo ""
    python3 hdw_terminal.py
fi