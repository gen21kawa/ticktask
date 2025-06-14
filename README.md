# TickTask

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Built with Claude Code](https://img.shields.io/badge/built%20with-Claude%20Code-blueviolet)](https://claude.ai/code)

A powerful command-line interface (CLI) tool for TickTick task management, featuring seamless integration with Obsidian and workflow automation capabilities.

> 🤖 **Built with [Claude Code](https://claude.ai/code)** - This project was developed using Claude Code, Anthropic's AI-powered coding assistant.

## 🌟 Features

- **🔐 Secure Authentication**: OAuth2 flow with encrypted token storage
- **📝 Complete Task Management**: Create, read, update, and delete tasks with ease
- **📁 Project Organization**: Full project management capabilities
- **🗓️ Natural Language Dates**: Use phrases like "tomorrow", "next week", or "in 3 days"
- **🔄 Obsidian Integration**: Export tasks to daily notes with beautiful formatting
- **🤖 Workflow Automation**: Daily planning, batch operations, and task templates
- **🎨 Rich Terminal UI**: Beautiful tables and formatted output using Rich
- **⚡ Async Architecture**: Built with modern async/await for optimal performance
- **🔧 Extensible**: Plugin system for custom workflows

## 📋 Prerequisites

- Python 3.8 or higher
- A TickTick account
- TickTick API credentials (see [Setup](#setup))

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install ticktask
```

### From Source

```bash
git clone https://github.com/yourusername/ticktask.git
cd ticktask
pip install -e .
```

## 🔧 Setup

### 1. Get Your Own TickTick API Credentials

> **Important**: Each user needs their own API credentials. Never share your client ID and secret!

1. Visit [TickTick Developer Center](https://developer.ticktick.com/manage)
2. Sign in with your TickTick account
3. Click "Create App" or "Register Application"
4. Fill in the application details:
   - **App Name**: Choose any name (e.g., "My TickTask CLI")
   - **App Description**: Personal CLI tool
   - **Website URL**: Can be this GitHub repo or your own
   - **Redirect URI**: `http://localhost:8080/callback` (must be exactly this)
5. After creation, you'll receive:
   - **Client ID**: Your unique app identifier
   - **Client Secret**: Your secret key (NEVER share this!)

### 2. Configure TickTask

> **Security Note**: See [SECURITY.md](SECURITY.md) for important security information.

Create a configuration file at `~/.ticktask/config.yaml`:

```yaml
api:
  client_id: "your_client_id_here"      # Your personal client ID
  client_secret: "your_client_secret_here"  # Your personal secret (keep private!)
  redirect_uri: "http://localhost:8080/callback"

defaults:
  project: "inbox"
  priority: 0

obsidian:
  vault_path: "~/Documents/ObsidianVault"
  daily_notes_path: "Daily Notes"
```

> **Tip**: Copy `config.example.yaml` as a starting template

Alternatively, use environment variables:

```bash
export TICKTICK_CLIENT_ID="your_client_id_here"
export TICKTICK_CLIENT_SECRET="your_client_secret_here"
```

### 3. Authenticate

```bash
ticktask auth login
```

This will open your browser for authentication. After approving access, you'll be logged in.

## 📖 Usage

### Basic Commands

```bash
# Simple task
ticktask task create "Buy groceries"

# Task with due date and priority
ticktask task create "Finish report" --due tomorrow --priority 5

# Task with project and subtasks
ticktask task create "Plan vacation" -p Personal -s "Book flights" -s "Reserve hotel"
```

## Command Reference

### Authentication

```bash
ticktask auth login     # Login to TickTick
ticktask auth logout    # Logout and clear credentials
ticktask auth status    # Check authentication status
```

### Task Management

```bash
# Create tasks
ticktask task create "Task title" [options]
  -p, --project TEXT     # Project name or ID
  -d, --due TEXT         # Due date (natural language supported)
  --priority [0|1|3|5]   # Priority level
  -c, --content TEXT     # Task description
  -s, --subtask TEXT     # Add subtask (multiple allowed)
  -r, --reminder TEXT    # Set reminder

# List tasks
ticktask task list [options]
  -p, --project TEXT     # Filter by project
  --due TEXT             # Filter by due date (today, tomorrow, week, overdue)
  --priority [0|1|3|5]   # Filter by priority
  --status [open|completed]  # Filter by status
  --format [table|json|markdown]  # Output format

# Update tasks
ticktask task update TASK_ID -p PROJECT_ID [options]
  --title TEXT           # New title
  -d, --due TEXT        # New due date
  --priority [0|1|3|5]  # New priority
  -c, --content TEXT    # New content

# Complete and delete tasks
ticktask task complete TASK_ID -p PROJECT_ID
ticktask task delete TASK_ID -p PROJECT_ID
```

### Project Management

```bash
# List all projects
ticktask project list

# Create a project
ticktask project create "Project Name" [options]
  --color TEXT          # Hex color code
  --kind [TASK|NOTE]    # Project type

# Show project details with tasks
ticktask project show PROJECT_ID

# Update project
ticktask project update PROJECT_ID [options]
  --name TEXT           # New name
  --color TEXT          # New color
  --view-mode [list|kanban|timeline]  # View mode

# Delete project
ticktask project delete PROJECT_ID
```

### Workflow Automation

```bash
# Generate daily plan
ticktask workflow daily-plan [options]
  --export-obsidian     # Export to Obsidian

# Batch complete tasks
ticktask workflow batch-complete [options]
  -p, --project TEXT    # Filter by project
  --pattern TEXT        # Title pattern to match
```

### Obsidian Integration

```bash
# Export daily task log to Obsidian
ticktask obsidian daily-log [options]
  --date TEXT           # Date to export (default: today)

# Sync tasks (coming soon)
ticktask obsidian sync [options]
  --direction [to-obsidian|from-obsidian|bidirectional]
  --vault PATH          # Obsidian vault path
```

## Natural Language Date Support

The package supports natural language for due dates:

- `today`, `tomorrow`, `yesterday`
- `next week`, `next month`
- `next Monday`, `next Friday`
- `in 3 days`, `in 2 weeks`
- Standard dates: `2024-03-15`, `03/15/2024`

## 🔗 Obsidian Integration

TickTask can export your tasks to Obsidian daily notes with a beautiful format:

```markdown
## TickTick Task Log

*Generated at: 14:30*

### ✅ Completed Tasks
- [x] Finish project proposal (Work) 🔴
  - Reviewed by manager

### ⚠️ Overdue Tasks
- [ ] Call dentist (Personal) 📅 2024-03-10 🟡

### 📅 Today's Tasks
- [ ] Team meeting (Work) 🔴
  - [ ] Prepare slides
  - [ ] Review agenda
- [ ] Grocery shopping (Personal)

### 📆 Upcoming Tasks
- [ ] Submit report (Work) 📅 2024-03-20 🟡

### 📊 Summary
- Total completed: 5
- Overdue: 1
- Due today: 3
- Upcoming: 7
```

## 🐍 Python API

You can also use TickTask as a Python library:

```python
import asyncio
from ticktask import TickTickClient, TaskManager

async def main():
    # Initialize client with your access token
    client = TickTickClient(access_token="your_token")
    task_manager = TaskManager(client)
    
    # Create a task
    task = await task_manager.create_task(
        title="Important task",
        due="tomorrow",
        priority=5,
        content="Don't forget this!"
    )
    
    # List today's tasks
    tasks = await task_manager.list_tasks(due_filter="today")
    for task in tasks:
        print(f"- {task.title} (Due: {task.due_date})")

asyncio.run(main())
```

## ⚙️ Configuration

TickTask looks for configuration in the following order:

1. `ticktask_config.yaml` in the current directory
2. `~/.ticktask/config.yaml` in your home directory
3. Environment variables

### Full Configuration Example

```yaml
api:
  base_url: "https://api.ticktick.com"
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  redirect_uri: "http://localhost:8080/callback"

defaults:
  project: "inbox"
  priority: 0
  reminder: "9:00"

obsidian:
  vault_path: "~/Documents/ObsidianVault"
  daily_notes_path: "Daily Notes"
  task_log_template: "templates/task-log.md"

workflows:
  daily_plan:
    include_overdue: true
    include_today: true
    include_tomorrow: false
    
formatting:
  date_format: "%Y-%m-%d"
  time_format: "%H:%M"
  timezone: "America/Los_Angeles"
```

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/ticktask.git
cd ticktask

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_models.py
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your PR:
- Passes all tests
- Includes tests for new functionality
- Follows the existing code style
- Updates documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Claude Code](https://claude.ai/code) - This entire project was developed using Claude Code
- [TickTick](https://ticktick.com) for providing the API
- [Click](https://click.palletsprojects.com/) for the excellent CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal formatting
- [httpx](https://www.python-httpx.org/) for async HTTP client
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

## 📮 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ticktask/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ticktask/discussions)
- **TickTick API Support**: support@ticktick.com

## 🗺️ Roadmap

- [ ] Bidirectional Obsidian sync
- [ ] Task templates system
- [ ] Time tracking integration
- [ ] Pomodoro timer
- [ ] Natural language task parsing
- [ ] Web dashboard
- [ ] Mobile companion app

---

<p align="center">
Made with ❤️ using <a href="https://claude.ai/code">Claude Code</a><br>
<sub>An AI-powered development experience by Anthropic</sub>
</p>