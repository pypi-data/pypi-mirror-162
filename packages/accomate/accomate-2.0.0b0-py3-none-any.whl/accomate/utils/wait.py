import time
import typer

def run_process_for(seconds):
    with typer.progressbar(range(seconds)) as progress:
        for i in progress:
            time.sleep(1)
