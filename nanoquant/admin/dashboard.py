"""
Admin dashboard for NanoQuant Enterprise
Provides administrative interface and controls
"""
import typer
from typing import Dict, Any
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import logging

logger = logging.getLogger(__name__)
console = Console()

class AdminDashboard:
    def __init__(self):
        """Initialize admin dashboard"""
        self.admin_users = set()  # In production, use proper authentication
    
    def authenticate_admin(self, username: str, password: str) -> bool:
        """Authenticate admin user"""
        # In a real implementation, we would check against a secure database
        # For now, we'll simulate authentication
        admin_credentials = {
            "admin": "admin123",
            "root": "root123"
        }
        
        return admin_credentials.get(username) == password
    
    def perform_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform an administrative action"""
        try:
            if action == "list_users":
                return self._list_users()
            elif action == "get_user_info":
                return self._get_user_info(parameters.get("user_id"))
            elif action == "create_coupon":
                return self._create_coupon(parameters.get("credits", 100))
            elif action == "system_stats":
                return self._get_system_stats()
            else:
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            logger.error(f"Error performing admin action {action}: {e}")
            raise
    
    def _list_users(self) -> Dict[str, Any]:
        """List all users"""
        # In a real implementation, we would query the database
        # For now, we'll return simulated data
        return {
            "users": [
                {"id": "user1", "email": "user1@example.com", "credits": 500, "tier": "premium"},
                {"id": "user2", "email": "user2@example.com", "credits": 100, "tier": "free"},
                {"id": "user3", "email": "user3@example.com", "credits": 1200, "tier": "enterprise"}
            ]
        }
    
    def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get information about a specific user"""
        # In a real implementation, we would query the database
        # For now, we'll return simulated data
        if user_id == "user1":
            return {
                "id": "user1",
                "email": "user1@example.com",
                "credits": 500,
                "tier": "premium",
                "compression_history": [
                    {"model": "meta-llama/Llama-2-7b-hf", "level": "heavy", "date": "2023-01-15"},
                    {"model": "mistralai/Mistral-7B-v0.1", "level": "medium", "date": "2023-01-20"}
                ]
            }
        else:
            return {"error": f"User {user_id} not found"}
    
    def _create_coupon(self, credits: int) -> Dict[str, Any]:
        """Create a new coupon"""
        # In a real implementation, we would generate and store the coupon
        # For now, we'll simulate coupon creation
        import secrets
        coupon_code = secrets.token_urlsafe(16)
        
        return {
            "coupon_code": coupon_code,
            "credits": credits,
            "message": f"Coupon created successfully with {credits} credits"
        }
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        # In a real implementation, we would gather real system stats
        # For now, we'll return simulated data
        return {
            "total_users": 1250,
            "active_users": 842,
            "total_compressions": 3247,
            "storage_used": "2.4 TB",
            "uptime": "99.8%",
            "average_response_time": "1.2s"
        }
    
    def display_dashboard(self):
        """Display the admin dashboard"""
        console.print(Panel("[bold blue] NanoQuant Admin Dashboard [/bold blue]", expand=False))
        
        # Display system stats
        stats = self._get_system_stats()
        console.print("\n[bold]System Statistics:[/bold]")
        for key, value in stats.items():
            console.print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Display recent activity
        console.print("\n[bold]Recent Activity:[/bold]")
        console.print("  [green]✓[/green] User user1 compressed meta-llama/Llama-2-7b-hf (heavy)")
        console.print("  [green]✓[/green] User user3 registered for enterprise plan")
        console.print("  [yellow]![/yellow] Payment failed for user user2")
        console.print("  [green]✓[/green] Coupon ABC123 redeemed by user user1")

# CLI Application
app = typer.Typer()

@app.command()
def login(
    username: str = typer.Option(..., "--username", "-u", prompt=True, help="Admin username"),
    password: str = typer.Option(..., "--password", "-p", prompt=True, hide_input=True, help="Admin password")
):
    """
    Login to the admin dashboard
    """
    console.print(Panel("[bold blue]🔐 Admin Login[/bold blue]", expand=False))
    
    dashboard = AdminDashboard()
    if dashboard.authenticate_admin(username, password):
        console.print("[bold green]✅ Login successful![/bold green]")
        dashboard.display_dashboard()
    else:
        console.print("[bold red]❌ Invalid credentials[/bold red]")

@app.command()
def users():
    """
    List all users
    """
    console.print(Panel("[bold blue]👥 User Management[/bold blue]", expand=False))
    
    dashboard = AdminDashboard()
    try:
        result = dashboard.perform_action("list_users", {})
        users = result["users"]
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Email", style="green")
        table.add_column("Credits", justify="right", style="yellow")
        table.add_column("Tier", style="blue")
        
        for user in users:
            table.add_row(
                user["id"],
                user["email"],
                str(user["credits"]),
                user["tier"]
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]❌ Error fetching users: {e}[/bold red]")

@app.command()
def stats():
    """
    Display system statistics
    """
    console.print(Panel("[bold blue]📊 System Statistics[/bold blue]", expand=False))
    
    dashboard = AdminDashboard()
    try:
        stats = dashboard.perform_action("system_stats", {})
        
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]❌ Error fetching statistics: {e}[/bold red]")

@app.command()
def coupon(
    credits: int = typer.Option(100, "--credits", "-c", help="Number of credits for the coupon")
):
    """
    Create a new coupon
    """
    console.print(Panel("[bold blue]🎟️ Create Coupon[/bold blue]", expand=False))
    
    dashboard = AdminDashboard()
    try:
        result = dashboard.perform_action("create_coupon", {"credits": credits})
        console.print(f"[bold green]✅ {result['message']}[/bold green]")
        console.print(f"   Coupon Code: [bold yellow]{result['coupon_code']}[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ Error creating coupon: {e}[/bold red]")

def main():
    """Main entry point for the admin dashboard"""
    app()

if __name__ == "__main__":
    main()