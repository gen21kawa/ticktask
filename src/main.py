import click
import asyncio
from .commands.task import task
from .commands.project import project
from .commands.auth import auth
from .commands.workflow import workflow
from .integrations.obsidian import obsidian
from .utils.config import Config


@click.group()
@click.pass_context
def cli(ctx):
    """TickTask - Manage your TickTick tasks from the command line"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config()


cli.add_command(task)
cli.add_command(project)
cli.add_command(auth)
cli.add_command(workflow)
cli.add_command(obsidian)


@cli.command()
@click.pass_context
def interactive(ctx):
    """Enter interactive mode for rapid task management"""
    click.echo("Entering interactive mode. Type 'help' for commands, 'exit' to quit.")
    
    while True:
        try:
            command = click.prompt("ticktask", type=str, default="", show_default=False)
            if command.lower() in ["exit", "quit", "q"]:
                break
            elif command.lower() == "help":
                click.echo("\nAvailable commands:")
                click.echo("  task create <title>     - Create a new task")
                click.echo("  task list              - List tasks")
                click.echo("  task complete <id>     - Complete a task")
                click.echo("  project list           - List projects")
                click.echo("  exit                   - Exit interactive mode")
                click.echo()
            elif command:
                # Parse and execute command
                parts = command.split()
                if len(parts) >= 2:
                    if parts[0] == "task" and parts[1] == "create":
                        # Quick task creation
                        title = " ".join(parts[2:])
                        ctx.invoke(task.commands["create"], title=title)
                    else:
                        click.echo(f"Unknown command: {command}")
                else:
                    click.echo(f"Unknown command: {command}")
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            click.echo(f"Error: {e}")
    
    click.echo("\nExiting interactive mode.")


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()