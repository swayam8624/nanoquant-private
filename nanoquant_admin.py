#!/usr/bin/env python3
"""
Admin CLI tool for NanoQuant
Manage coupons, users, and system administration
"""

import typer
import secrets
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from nanoquant.core.user_management import UserManager

app = typer.Typer(
    name="nanoquant-admin",
    help="Admin CLI tool for NanoQuant system management",
    no_args_is_help=True
)

@app.command()
def create_coupon(
    credits: int = typer.Option(..., "--credits", "-c", help="Number of credits for the coupon"),
    count: int = typer.Option(1, "--count", "-n", help="Number of coupons to generate"),
    admin_key: str = typer.Option("nanoquant_admin_secret", "--admin-key", "-k", help="Admin key for authorization")
):
    """
    Create coupon codes for users
    """
    user_manager = UserManager()
    
    typer.echo(f"Creating {count} coupon(s) with {credits} credits each...")
    
    for i in range(count):
        coupon_code = user_manager.create_coupon(credits, admin_key)
        if coupon_code:
            typer.echo(f"Coupon {i+1}: {coupon_code}")
        else:
            typer.echo(f"Failed to create coupon {i+1}")
    
    typer.echo("Coupon creation completed!")

@app.command()
def list_users():
    """
    List all registered users
    """
    user_manager = UserManager()
    users = user_manager.users.get("users", {})
    
    if not users:
        typer.echo("No users found.")
        return
    
    typer.echo(f"Found {len(users)} user(s):")
    for user_id, user_data in users.items():
        typer.echo(f"  - {user_data.get('email', 'N/A')} ({user_data.get('tier', 'N/A')}) - {user_data.get('credits', 0)} credits")

@app.command()
def add_credits(
    email: str = typer.Option(..., "--email", "-e", help="User email"),
    credits: int = typer.Option(..., "--credits", "-c", help="Number of credits to add"),
    admin_key: str = typer.Option("nanoquant_admin_secret", "--admin-key", "-k", help="Admin key for authorization")
):
    """
    Add credits to a user's account
    """
    # Simple admin check
    if admin_key != "nanoquant_admin_secret":
        typer.echo("Invalid admin key!")
        raise typer.Exit(1)
    
    user_manager = UserManager()
    users = user_manager.users.get("users", {})
    
    # Find user by email
    user_id = None
    for uid, user_data in users.items():
        if user_data.get("email") == email:
            user_id = uid
            break
    
    if not user_id:
        typer.echo(f"User with email {email} not found!")
        raise typer.Exit(1)
    
    if user_manager.add_credits(user_id, credits, "admin_grant"):
        typer.echo(f"Successfully added {credits} credits to {email}")
    else:
        typer.echo(f"Failed to add credits to {email}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()