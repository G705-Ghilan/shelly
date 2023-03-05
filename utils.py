
import os
import zipfile

from tqdm import tqdm

from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import Progress
from rich.console import Console

console: Console = Console()
print = console.print

P: list = ["╰",  "─", "╯", "│", "╭", "╮"]


def progress(text: str) -> Progress:
    progress: Progress = Progress(
        SpinnerColumn(),
        TextColumn(text + "  [progress.description]{task.description}"),
        refresh_per_second=90000*10,
    )
    progress.add_task('test')
    return progress


def print_files(files: list) -> None:
    sorted_folders: list = sorted(
        [f"[bold][blue]{i}[/blue][/bold]" for i in files if i.endswith("/")])
    sorted_files: list = sorted([i for i in files if not i.endswith("/")])
    for i in sorted_folders + sorted_files:
        print(i)


def get_size(s: int) -> str:
    levels: list = ['Bytes', 'KB', 'MB', 'GB', "TB"]
    for level in levels:
        if s <= 1024:
            return f"[green]{round(s, 2)} {level}[/green]"
        s /= 1024
    return "Unknown"

def prompet(path: str, addr: tuple, devices: int) -> str:
    return f"[red]{P[4]}{P[1]*2}[/red][{addr[0]}:{addr[1]}][red]{P[1]}[/red][{devices} devices]\n[red]{P[3]}\n{P[0]}{P[1]*2}[/red][[cyan] {path} [/cyan]][red] >[/red] "


class Ziper:
    @staticmethod
    def zip(path: str) -> None:
        original_path: str = os.getcwd()
        os.chdir(path)
        with zipfile.ZipFile(path + ".zip", "w") as z:
            for file in Ziper.getFiles(path):
                print(file)
                z.write(file[len(path)+1:])
        os.chdir(original_path)
        print(os.getcwd())

    @staticmethod
    def unZip(path: str) -> None:
        with zipfile.ZipFile(path, "r") as z:
            max: int = len(z.filelist)
            with progress("Extracting ") as p:
                for i, file in enumerate(z.filelist, start=1):
                    z.extract(file, path=os.path.basename(path[:-4]))
                    p.update(
                        0, description=f"[cyan]{str(i / max * 100).split('.')[0]}%[/cyan]")

    @staticmethod
    def getFiles(path: str) -> list[str]:
        result = []
        for i in os.listdir(path):
            if os.path.isdir(i := os.path.join(path, i)):
                result += Ziper.getFiles(i)
            else:
                result.append(i)
        return result


# os.chdir("E:")
# print(os.listdir())
# path = "test_charts.zip"

# Ziper.unZip(path)
