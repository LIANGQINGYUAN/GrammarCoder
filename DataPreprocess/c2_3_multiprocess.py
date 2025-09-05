import multiprocessing
import subprocess
import argparse

def run_command(index):
    wfile = f"./c2_rules/xxx_{index}.jsonl"
    rfile = f"./c1_data/xxx_{index}.jsonl"
    logfile = f"./c2_logs/xxx_{index}.log"
    command = f"python c2_3_mytree2tokens.py --rfile {rfile} --wfile {wfile} > {logfile}"
    subprocess.run(command, shell=True, check=True)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--begin_index", type=int, default=0)
    parser.add_argument("--end_index", type=int, default=50)

    args = parser.parse_args()
    begin_index = args.begin_index
    end_index = args.end_index

    max_processes = end_index - begin_index

    with multiprocessing.Pool(processes=max_processes) as pool:
        pool.map(run_command, range(begin_index, end_index))
