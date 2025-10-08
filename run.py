#!/usr/bin/env python3
import subprocess
import time
from tqdm import tqdm

def run_script_with_progress(script_path):
    print(f"\n--- Running {script_path} ---\n")
    
    # Start the process
    process = subprocess.Popen(
        ["python3", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Create a progress bar that will fill gradually
    pbar = tqdm(total=100, desc=f"{script_path} Progress", ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}%')
    
    while True:
        line = process.stdout.readline()
        if line:
            print(line, end="")  # Print script output in real time
        retcode = process.poll()
        # Update progress bar slowly
        if pbar.n < pbar.total:
            pbar.update(0.5)  # adjust speed of increment
        if retcode is not None:
            break
        time.sleep(0.05)  # small delay to avoid busy waiting

    # Fill progress bar to 100% when done
    if pbar.n < pbar.total:
        pbar.update(pbar.total - pbar.n)
    pbar.close()
    print(f"\n--- Finished {script_path} ---\n")

def main():
    # Run test1.py
    run_script_with_progress("stage1.py")

    # Run test2.py three times
    for i in range(10):
        print(f"\n=== Running test2.py iteration {i+1}/10 ===")
        run_script_with_progress("stage2.py")

if __name__ == "__main__":
    main()

