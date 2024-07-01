import click
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

console = Console()

def get_info():
    info_lines = subprocess.check_output("sensors").decode("utf-8").split("\n")
    result = []
    count = 0
    for i in info_lines:
        if "Core" in i:
            result.append(f"Core {count}: {i.split(':')[-1].split('(')[0].strip()}")
            count += 1
        if "fan" in i:
            result.append(f"Вентилятор: {i.split(':')[-1].strip()}")
    return result

def set_speed(speed=None):
    with Progress() as progress:
        task = progress.add_task("[cyan]Установка скорости вентилятора...", total=100)
        for i in range(100):
            time.sleep(0.01)
            progress.update(task, advance=1)
        
    return subprocess.check_output(
        f'echo level {speed} | sudo tee "/proc/acpi/ibm/fan"',
        shell=True
    ).decode()

@click.group()
def cli():
    """Утилита управления вентилятором ThinkFan"""
    pass

@cli.command()
def info():
    """Показать информацию о температуре и скорости вентилятора"""
    info = get_info()
    table = Table(title="Информация о системе")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="magenta")
    
    for line in info:
        param, value = line.split(": ")
        table.add_row(param, value)
    
    console.print(table)

@cli.command()
@click.argument('speed', type=click.Choice(['0', '1', '2', '3', '4', '5', '6', '7', 'auto', 'full']))
def set(speed):
    """Установить скорость вентилятора"""
    result = set_speed(speed)
    console.print(Panel(f"[green]Скорость вентилятора установлена на {speed}[/green]"))

@cli.command()
def interactive():
    """Интерактивный режим управления вентилятором"""
    while True:
        console.print("\n[bold cyan]Выберите действие:[/bold cyan]")
        console.print("1. Показать информацию")
        console.print("2. Установить скорость")
        console.print("3. Выход")
        
        choice = click.prompt("Ваш выбор", type=int)
        
        if choice == 1:
            info()
        elif choice == 2:
            speed = click.prompt("Введите скорость (0-7, auto, full)", type=click.Choice(['0', '1', '2', '3', '4', '5', '6', '7', 'auto', 'full']))
            set_speed(speed)
            console.print(f"[green]Скорость вентилятора установлена на {speed}[/green]")
        elif choice == 3:
            break
        else:
            console.print("[red]Неверный выбор. Попробуйте снова.[/red]")

if __name__ == "__main__":
    cli()

