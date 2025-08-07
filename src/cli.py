"""
Command Line Interface for Auto-Newsletter Generator

This module provides a CLI interface using Typer for the Auto-Newsletter Generator.
It allows users to run the application with various options and view the results.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(project_root))

try:
    import typer
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    HAS_RICH = True
except ImportError:
    typer = None
    HAS_RICH = False
    print("For a better CLI experience, install typer and rich: pip install typer rich")

from src.main import NewsletterApp
from src.user_profile import UserProfile

# Initialize Typer app if available
app = typer.Typer(help="Auto-Newsletter Generator CLI") if typer else None
console = Console() if HAS_RICH else None

def display_welcome():
    """Display a welcome message with application information."""
    if HAS_RICH:
        console.print(Panel.fit(
            "[bold blue]Auto-Newsletter Generator[/bold blue]\n\n"
            "A professional-grade Python application that automatically generates\n"
            "personalized newsletters from trending news articles.",
            title="Welcome",
            border_style="blue"
        ))
    else:
        print("\n=== Auto-Newsletter Generator ===\n")
        print("A professional-grade Python application that automatically generates")
        print("personalized newsletters from trending news articles.\n")

def display_results(output_files):
    """Display the results of newsletter generation.

    Args:
        output_files: Dictionary with paths to generated files
    """
    if not output_files:
        if HAS_RICH:
            console.print("[bold red]No newsletter files were generated.[/bold red]")
        else:
            print("No newsletter files were generated.")
        return

    if HAS_RICH:
        table = Table(title="Generated Newsletter Files")
        table.add_column("Format", style="cyan")
        table.add_column("Path", style="green")
        
        for format_type, file_path in output_files.items():
            table.add_row(format_type.upper(), file_path)
        
        console.print(table)
        
        # If markdown file was generated, show a preview
        if 'markdown' in output_files and os.path.exists(output_files['markdown']):
            try:
                with open(output_files['markdown'], 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                console.print(Panel.fit(
                    Markdown(md_content[:1000] + "..." if len(md_content) > 1000 else md_content),
                    title="Newsletter Preview",
                    border_style="green"
                ))
            except Exception as e:
                console.print(f"[red]Error displaying preview: {str(e)}[/red]")
    else:
        print("\nGenerated Newsletter Files:")
        for format_type, file_path in output_files.items():
            print(f"- {format_type.upper()}: {file_path}")

def list_user_profiles():
    """List available user profiles.

    Returns:
        List of profile names
    """
    profiles_dir = project_root / "data" / "user_profiles"
    if not profiles_dir.exists():
        return []
    
    profiles = []
    for file in profiles_dir.glob("*.json"):
        profile_name = file.stem.replace('_', ' ').title()
        profiles.append(profile_name)
    
    return profiles

def display_profiles(profiles):
    """Display available user profiles.

    Args:
        profiles: List of profile names
    """
    if not profiles:
        if HAS_RICH:
            console.print("[yellow]No user profiles found.[/yellow]")
        else:
            print("No user profiles found.")
        return

    if HAS_RICH:
        table = Table(title="Available User Profiles")
        table.add_column("Profile Name", style="cyan")
        
        for profile in profiles:
            table.add_row(profile)
        
        console.print(table)
    else:
        print("\nAvailable User Profiles:")
        for profile in profiles:
            print(f"- {profile}")

# Define CLI commands if Typer is available
if app:
    @app.command()
    def generate(
        config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file"),
        profile: Optional[str] = typer.Option(None, "--profile", "-p", help="User profile to use"),
        output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory for newsletter files")
    ):
        """Generate a newsletter using the configured settings."""
        display_welcome()
        
        # Initialize the application
        newsletter_app = NewsletterApp(config)
        
        # Override output directory if specified
        if output:
            newsletter_app.config['newsletter']['output_dir'] = output
        
        # Load user profile if specified
        if profile:
            newsletter_app.user_profile = UserProfile.load_user_profile(newsletter_app.config, profile)
        
        # Run the pipeline
        console.print("[bold]Generating newsletter...[/bold]")
        output_files = newsletter_app.run()
        
        # Display results
        display_results(output_files)

    @app.command()
    def profiles():
        """List available user profiles."""
        display_welcome()
        profiles_list = list_user_profiles()
        display_profiles(profiles_list)

    @app.command()
    def schedule(
        time: str = typer.Option("08:00", "--time", "-t", help="Time to schedule (HH:MM format)"),
        config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file"),
        profile: Optional[str] = typer.Option(None, "--profile", "-p", help="User profile to use")
    ):
        """Schedule newsletter generation to run daily at the specified time."""
        display_welcome()
        
        try:
            from apscheduler.schedulers.blocking import BlockingScheduler
            from apscheduler.triggers.cron import CronTrigger
        except ImportError:
            console.print("[bold red]APScheduler not installed. Install with: pip install apscheduler[/bold red]")
            return
        
        # Initialize the application
        newsletter_app = NewsletterApp(config)
        
        # Load user profile if specified
        if profile:
            newsletter_app.user_profile = UserProfile.load_user_profile(newsletter_app.config, profile)
        
        # Set up scheduler
        scheduler = BlockingScheduler()
        hour, minute = time.split(":")
        
        scheduler.add_job(
            newsletter_app.run,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            id="newsletter_generation",
            name="Daily Newsletter Generation"
        )
        
        console.print(f"[bold green]Scheduled newsletter generation for {time} daily[/bold green]")
        console.print("[yellow]Press Ctrl+C to exit[/yellow]")
        
        try:
            scheduler.start()
        except KeyboardInterrupt:
            console.print("[bold]Scheduler stopped[/bold]")

def main():
    """Main entry point for the CLI."""
    if app:
        app()
    else:
        # Fallback if Typer is not available
        display_welcome()
        
        # Parse basic arguments
        import argparse
        parser = argparse.ArgumentParser(description="Auto-Newsletter Generator CLI")
        parser.add_argument("-c", "--config", help="Path to configuration file")
        parser.add_argument("-p", "--profile", help="User profile to use")
        parser.add_argument("-o", "--output", help="Output directory for newsletter files")
        parser.add_argument("--profiles", action="store_true", help="List available user profiles")
        args = parser.parse_args()
        
        if args.profiles:
            profiles_list = list_user_profiles()
            display_profiles(profiles_list)
            return
        
        # Initialize the application
        newsletter_app = NewsletterApp(args.config)
        
        # Override output directory if specified
        if args.output:
            newsletter_app.config['newsletter']['output_dir'] = args.output
        
        # Load user profile if specified
        if args.profile:
            newsletter_app.user_profile = UserProfile.load_user_profile(newsletter_app.config, args.profile)
        
        # Run the pipeline
        print("Generating newsletter...")
        output_files = newsletter_app.run()
        
        # Display results
        display_results(output_files)

if __name__ == "__main__":
    main()