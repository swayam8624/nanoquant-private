"""
CLI interface for NanoQuant (Core Version)
Provides command-line access to model compression functionality without business logic
"""
import typer
import time
from typing import Optional
from pathlib import Path
import logging
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import print as rprint
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()

app = typer.Typer(
    name="nanoquant",
    help="Compress LLMs into NanoQuants with ultra-advanced techniques",
    no_args_is_help=True
)

@app.command()
def compress(
    model_id: str = typer.Option(..., "--model", "-m", help="Model ID or path to compress"),
    level: str = typer.Option("medium", "--level", "-l", help="Compression level (light, medium, heavy, extreme, ultra, nano, atomic)"),
    output_dir: str = typer.Option("./nanoquants", "--output", "-o", help="Output directory for compressed models"),
    push_to_ollama: bool = typer.Option(True, "--push-to-ollama/--no-push", help="Push compressed models to Ollama")
):
    """
    Compress a model into NanoQuants
    """
    console.print(Panel("[bold blue]🚀 Compressing Model[/bold blue]", expand=False))
    console.print(f"[cyan]Model:[/cyan] {model_id}")
    console.print(f"[cyan]Level:[/cyan] {level}")
    console.print(f"[cyan]Output:[/cyan] {output_dir}")
    console.print(f"[cyan]Push to Ollama:[/cyan] {push_to_ollama}")
    
    try:
        # Import the compression pipeline
        from nanoquant.core.compression_pipeline import CompressionPipeline
        
        # Create pipeline
        pipeline = CompressionPipeline(output_base_dir=output_dir)
        
        # Process model
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Compressing model...", total=None)
            
            result = pipeline.process_model(
                model_id=model_id,
                compression_level=level,
                push_to_ollama=push_to_ollama
            )
            
            progress.update(task, completed=True)
        
        # Display results
        console.print("[bold green]✅ Compression completed successfully![/bold green]")
        
        # Create results table
        results_table = Table(title="Compression Results", show_header=True, header_style="bold magenta")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")
        
        results_table.add_row("Original Model", result["model_id"])
        results_table.add_row("Compression Level", level)
        results_table.add_row("Models Generated", str(len(result["generated_models"])))
        results_table.add_row("Output Directory", result["output_directory"])
        
        console.print(results_table)
        
        # Display Ollama information
        if result["ollama_tags"]:
            console.print("\n[bold blue]📦 Ollama Models:[/bold blue]")
            for tag in result["ollama_tags"]:
                console.print(f"   [green]ollama pull {tag}[/green]")
            
            console.print("\n[bold blue]🏃 Running Compressed Models:[/bold blue]")
            for tag, command in result["pull_commands"].items():
                console.print(f"   [green]{command}[/green]")
        else:
            console.print("[yellow]⚠️  Models were not pushed to Ollama[/yellow]")
            
    except Exception as e:
        console.print(f"[bold red]❌ Error during compression: {e}[/bold red]")
        logger.error(f"Compression error: {e}")

@app.command()
def levels():
    """
    Show available compression levels
    """
    try:
        from nanoquant.core.compression_pipeline import CompressionPipeline
        pipeline = CompressionPipeline()
        levels_info = pipeline.get_compression_levels()
        
        console.print(Panel("[bold blue]🔧 Compression Levels[/bold blue]", expand=False))
        
        levels_table = Table(show_header=True, header_style="bold magenta")
        levels_table.add_column("Level", style="cyan")
        levels_table.add_column("Name", style="green")
        levels_table.add_column("Description", style="yellow")
        
        for level_key, level_info in levels_info.items():
            levels_table.add_row(
                level_key,
                level_info["name"],
                level_info["description"]
            )
        
        console.print(levels_table)
        
    except Exception as e:
        console.print(f"[bold red]❌ Error getting compression levels: {e}[/bold red]")

@app.command()
def info(
    model_id: str = typer.Option(..., "--model", "-m", help="Model ID or path to analyze")
):
    """
    Analyze a model for compression suitability
    """
    console.print(Panel("[bold blue]🔍 Analyzing Model[/bold blue]", expand=False))
    console.print(f"[cyan]Model:[/cyan] {model_id}")
    
    try:
        from nanoquant.core.model_ingestion import ModelIngestionPipeline
        
        # Create ingestion pipeline
        ingestion = ModelIngestionPipeline()
        
        # Analyze model
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing model...", total=None)
            
            model_info = ingestion.analyze_model(model_id)
            
            progress.update(task, completed=True)
        
        # Display results
        console.print("[bold green]✅ Analysis completed![/bold green]")
        
        # Create info table
        info_table = Table(title="Model Information", show_header=True, header_style="bold magenta")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")
        
        info_table.add_row("Model ID", model_info.get("model_id", "N/A"))
        info_table.add_row("Architecture", model_info.get("architecture", "N/A"))
        info_table.add_row("Model Family", model_info.get("model_family", "N/A"))
        info_table.add_row("Hidden Size", str(model_info.get("hidden_size", "N/A")))
        info_table.add_row("Number of Layers", str(model_info.get("num_layers", "N/A")))
        
        console.print(info_table)
        
        # Display recommended compression
        if "recommended_compression" in model_info:
            console.print("\n[bold blue]🎯 Recommended Compression:[/bold blue]")
            rec = model_info["recommended_compression"]
            console.print(f"   Level: [green]{rec.get('level', 'N/A')}[/green]")
            console.print(f"   Reason: [yellow]{rec.get('reason', 'N/A')}[/yellow]")
            console.print(f"   Expected Size Reduction: [cyan]{rec.get('size_reduction', 'N/A')}[/cyan]")
            
    except Exception as e:
        console.print(f"[bold red]❌ Error during analysis: {e}[/bold red]")
        logger.error(f"Analysis error: {e}")

if __name__ == "__main__":
    app()