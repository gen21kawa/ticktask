import click
import asyncio
from ..api.auth import OAuth2Handler
from ..utils.formatting import ProgressDisplay
from ..utils.config import Config


@click.group()
def auth():
    """Manage authentication"""
    pass


@auth.command()
@click.pass_context
def login(ctx):
    """Login to TickTick"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    # Check for client credentials
    if not config.client_id or not config.client_secret:
        progress.show_error("Client ID and Client Secret not configured")
        click.echo("\nPlease set your TickTick API credentials:")
        click.echo("1. Visit https://developer.ticktick.com/manage")
        click.echo("2. Register your application")
        click.echo("3. Add credentials to your config file or environment variables:")
        click.echo("   - TICKTICK_CLIENT_ID")
        click.echo("   - TICKTICK_CLIENT_SECRET")
        return
    
    auth_handler = OAuth2Handler(
        client_id=config.client_id,
        client_secret=config.client_secret,
        redirect_uri=config.redirect_uri
    )
    
    try:
        progress.show_progress("Opening browser for authorization")
        access_token = asyncio.run(auth_handler.login())
        progress.show_success("Successfully logged in!")
    except Exception as e:
        progress.show_error(f"Login failed: {e}")


@auth.command()
@click.pass_context
def logout(ctx):
    """Logout from TickTick"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    auth_handler = OAuth2Handler(
        client_id=config.client_id,
        client_secret=config.client_secret
    )
    
    auth_handler.logout()
    progress.show_success("Successfully logged out!")


@auth.command()
@click.pass_context
def status(ctx):
    """Check authentication status"""
    config = ctx.obj['config']
    progress = ProgressDisplay()
    
    auth_handler = OAuth2Handler(
        client_id=config.client_id,
        client_secret=config.client_secret
    )
    
    async def check_status():
        token = await auth_handler.get_access_token()
        if token:
            progress.show_success("Authenticated")
            return True
        else:
            progress.show_error("Not authenticated")
            return False
    
    is_authenticated = asyncio.run(check_status())
    if not is_authenticated:
        click.echo("Run 'ticktask auth login' to authenticate")