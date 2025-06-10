#!/usr/bin/env python3
"""
Honey Duo Wealth Terminal Interface
Interactive terminal app for easy project management
"""

import os
import sys
import yaml
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class HDWTerminalApp:
    def __init__(self):
        self.project_root = Path.cwd()
        self.tasks_file = self.project_root / "tasks.yaml"
        self.cli_path = self.project_root / "cli" / "hdw-task.py"
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def load_tasks(self) -> List[Dict]:
        """Load tasks from tasks.yaml"""
        if not self.tasks_file.exists():
            return []
        
        with open(self.tasks_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('tasks', [])
    
    def run_cli_command(self, command: str) -> str:
        """Run a CLI command and return output"""
        try:
            cmd = f"python3 {self.cli_path} {command}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error: {e}"
    
    def show_header(self):
        """Display the app header"""
        print("=" * 80)
        print("🍯 HONEY DUO WEALTH - PROJECT MANAGEMENT TERMINAL")
        print("=" * 80)
        print(f"📁 Project: {self.project_root.name}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def show_dashboard(self):
        """Display project dashboard"""
        tasks = self.load_tasks()
        
        if not tasks:
            print("📋 No tasks found")
            return
        
        # Count tasks by status
        status_counts = {}
        for task in tasks:
            status = task.get('status', 'pending')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Show summary
        print("📊 PROJECT STATUS")
        print("-" * 40)
        status_icons = {
            'pending': '⏳',
            'in-progress': '🔄', 
            'completed': '✅',
            'blocked': '🚫'
        }
        
        for status, count in status_counts.items():
            icon = status_icons.get(status, '❓')
            print(f"  {icon} {status.title()}: {count}")
        
        print()
        
        # Show recent tasks
        print("📋 RECENT TASKS")
        print("-" * 40)
        
        # Sort by status priority (in-progress first, then pending, then others)
        priority_order = {'in-progress': 0, 'pending': 1, 'blocked': 2, 'completed': 3}
        sorted_tasks = sorted(tasks, key=lambda x: priority_order.get(x.get('status', 'pending'), 4))
        
        for i, task in enumerate(sorted_tasks[:10], 1):
            status = task.get('status', 'pending')
            icon = status_icons.get(status, '❓')
            desc = task.get('description', 'No description')[:50]
            print(f"  {i:2}. {icon} {task['id']:<20} {desc}")
        
        print()
    
    def show_task_details(self, task_id: str):
        """Show detailed information about a task"""
        tasks = self.load_tasks()
        task = next((t for t in tasks if t['id'] == task_id), None)
        
        if not task:
            print(f"❌ Task '{task_id}' not found")
            return
        
        print(f"📄 TASK DETAILS: {task_id}")
        print("-" * 50)
        print(f"Description: {task.get('description', 'No description')}")
        print(f"Status: {task.get('status', 'pending')}")
        print(f"Output: {task.get('output', 'Not specified')}")
        
        if task.get('tests'):
            print(f"Tests: {task['tests']}")
        
        if task.get('context'):
            print(f"Context: {', '.join(task['context'])}")
        
        if task.get('updated'):
            print(f"Updated: {task['updated']}")
        
        if task.get('notes'):
            print("\nNotes:")
            for note in task['notes']:
                print(f"  - {note.get('timestamp', '')}: {note.get('note', '')}")
        print()
    
    def start_task_interactive(self):
        """Interactive task starting"""
        tasks = self.load_tasks()
        pending_tasks = [t for t in tasks if t.get('status') == 'pending']
        
        if not pending_tasks:
            print("📋 No pending tasks available")
            input("Press Enter to continue...")
            return
        
        print("📋 PENDING TASKS")
        print("-" * 40)
        
        for i, task in enumerate(pending_tasks, 1):
            desc = task.get('description', 'No description')[:60]
            print(f"  {i}. {task['id']:<20} {desc}")
        
        print()
        try:
            choice = input("🚀 Select task number to start (or 'q' to cancel): ").strip()
            
            if choice.lower() == 'q':
                return
            
            task_num = int(choice) - 1
            if 0 <= task_num < len(pending_tasks):
                task_id = pending_tasks[task_num]['id']
                print(f"\n🚀 Starting task: {task_id}")
                
                # Run the CLI command
                output = self.run_cli_command(f"start {task_id}")
                print(output)
                
                input("Press Enter to continue...")
            else:
                print("❌ Invalid selection")
                input("Press Enter to continue...")
        
        except ValueError:
            print("❌ Invalid input")
            input("Press Enter to continue...")
    
    def complete_task_interactive(self):
        """Interactive task completion"""
        tasks = self.load_tasks()
        in_progress_tasks = [t for t in tasks if t.get('status') == 'in-progress']
        
        if not in_progress_tasks:
            print("📋 No in-progress tasks to complete")
            input("Press Enter to continue...")
            return
        
        print("🔄 IN-PROGRESS TASKS")
        print("-" * 40)
        
        for i, task in enumerate(in_progress_tasks, 1):
            desc = task.get('description', 'No description')[:60]
            print(f"  {i}. {task['id']:<20} {desc}")
        
        print()
        try:
            choice = input("✅ Select task number to complete (or 'q' to cancel): ").strip()
            
            if choice.lower() == 'q':
                return
            
            task_num = int(choice) - 1
            if 0 <= task_num < len(in_progress_tasks):
                task_id = in_progress_tasks[task_num]['id']
                
                # Optional custom message
                message = input("💬 Custom commit message (or Enter for default): ").strip()
                
                print(f"\n✅ Completing task: {task_id}")
                
                # Run the CLI command
                if message:
                    output = self.run_cli_command(f'commit {task_id} --message "{message}"')
                else:
                    output = self.run_cli_command(f"commit {task_id}")
                
                print(output)
                input("Press Enter to continue...")
            else:
                print("❌ Invalid selection")
                input("Press Enter to continue...")
        
        except ValueError:
            print("❌ Invalid input")
            input("Press Enter to continue...")
    
    def show_menu(self):
        """Display main menu options"""
        print("🎛️  MAIN MENU")
        print("-" * 40)
        print("  1. 📊 Dashboard")
        print("  2. 📋 List All Tasks")
        print("  3. 🚀 Start Task")
        print("  4. ✅ Complete Task")
        print("  5. 🚫 Block Task")
        print("  6. 📄 Task Details")
        print("  7. 📈 Generate Status Report")
        print("  8. 🔄 Refresh")
        print("  9. ❓ Help")
        print("  0. 🚪 Exit")
        print()
    
    def show_help(self):
        """Show help information"""
        print("📖 HELP")
        print("-" * 40)
        print("This terminal app helps you manage your Honey Duo Wealth project.")
        print()
        print("Workflow:")
        print("  1. Check Dashboard for project status")
        print("  2. Start a pending task")
        print("  3. Work with Claude using the context file")
        print("  4. Complete the task when done")
        print("  5. Generate status report for ChatGPT")
        print()
        print("Tips:")
        print("  - Context files are created in .task_context_<task-id>.md")
        print("  - Share these with Claude for implementation")
        print("  - Status reports help keep ChatGPT updated")
        print()
        input("Press Enter to continue...")
    
    def generate_report_interactive(self):
        """Interactive status report generation"""
        tasks = self.load_tasks()
        recent_tasks = [t for t in tasks if t.get('status') in ['completed', 'blocked', 'in-progress']]
        
        if not recent_tasks:
            print("📋 No tasks available for reporting")
            input("Press Enter to continue...")
            return
        
        print("📈 GENERATE STATUS REPORT")
        print("-" * 40)
        
        for i, task in enumerate(recent_tasks[-10:], 1):  # Last 10 tasks
            status = task.get('status', 'pending')
            desc = task.get('description', 'No description')[:50]
            print(f"  {i}. {task['id']:<20} [{status}] {desc}")
        
        print()
        try:
            choice = input("📈 Select task number for report (or 'q' to cancel): ").strip()
            
            if choice.lower() == 'q':
                return
            
            task_num = int(choice) - 1
            if 0 <= task_num < len(recent_tasks[-10:]):
                task_id = recent_tasks[-10:][task_num]['id']
                
                # Run status report generation
                if (self.project_root / "status_report.py").exists():
                    cmd = f"python3 status_report.py {task_id}"
                    os.system(cmd)
                else:
                    print("📈 Status report generator not found")
                
                input("Press Enter to continue...")
            else:
                print("❌ Invalid selection")
                input("Press Enter to continue...")
        
        except ValueError:
            print("❌ Invalid input")
            input("Press Enter to continue...")
    
    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            self.show_header()
            self.show_dashboard()
            self.show_menu()
            
            try:
                choice = input("🎯 Select option: ").strip()
                
                if choice == '0':
                    print("\n👋 Goodbye! Happy coding!")
                    break
                elif choice == '1':
                    # Dashboard is already shown
                    input("Press Enter to continue...")
                elif choice == '2':
                    print("\n📋 ALL TASKS")
                    print("-" * 40)
                    output = self.run_cli_command("list")
                    print(output)
                    input("Press Enter to continue...")
                elif choice == '3':
                    self.start_task_interactive()
                elif choice == '4':
                    self.complete_task_interactive()
                elif choice == '5':
                    # Block task functionality
                    task_id = input("🚫 Task ID to block: ").strip()
                    reason = input("❓ Reason for blocking: ").strip()
                    if task_id and reason:
                        output = self.run_cli_command(f'block {task_id} "{reason}"')
                        print(output)
                    input("Press Enter to continue...")
                elif choice == '6':
                    task_id = input("📄 Task ID for details: ").strip()
                    if task_id:
                        self.show_task_details(task_id)
                    input("Press Enter to continue...")
                elif choice == '7':
                    self.generate_report_interactive()
                elif choice == '8':
                    continue  # Refresh by reloading
                elif choice == '9':
                    self.show_help()
                else:
                    print("❌ Invalid option")
                    input("Press Enter to continue...")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")

def main():
    # Check if we're in the right directory
    if not Path("tasks.yaml").exists():
        print("❌ Error: tasks.yaml not found")
        print("Please run this from your honey_duo_wealth project directory")
        print("cd ~/hdw_setup/honey_duo_wealth")
        sys.exit(1)
    
    app = HDWTerminalApp()
    app.run()

if __name__ == "__main__":
    main()