from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import Progress
from rich.console import Console

console: Console = Console()

P: list = ["╰",  "─", "╯", "│", "╭", "╮"]

def progress(text: str) -> Progress:
    progress: Progress = Progress(SpinnerColumn(), TextColumn(f" {text}"))
    progress.add_task('test')
    return progress



def print_files(files: list) -> None:
    sorted_folders: list = sorted([f"\033[1;34m{i}\033[0m" for i in files if i.endswith("/")])
    sorted_files: list = sorted([i for i in files if not i.endswith("/")])
    for i in sorted_folders + sorted_files:
        print(i)

def prompet(path: str, addr: tuple, devices: int) -> str:
	return f"{P[4]}{P[1]*2}( {addr[0]}:{addr[1]} ) ( {devices} devices )\n{P[3]}\n{P[0]}{P[1]*2}( {path} ) > "
 