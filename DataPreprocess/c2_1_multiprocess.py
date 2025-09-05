import multiprocessing
import subprocess
import argparse

def run_command(index):
    wfile = f"./c2_addrules/output_{index}.pkl"
    rfile = f"./c1_data/output_{index}.jsonl"
    command = f"python c2_1_getNewRules.py --rfile {rfile} --wfile {wfile}"
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

