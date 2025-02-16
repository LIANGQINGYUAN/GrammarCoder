import json

def trim_code_by_top_level_lines(code2):
    def count_top_level_lines(code):
        lines = code.split("\n")
        return sum(1 for line in lines if line and not line.startswith(" ") and not line.startswith("\t"))

    def trim_code(code, top_level_limit):
        lines = code.split("\n")
        top_level_lines = 0
        trimmed_lines = []
        
        for line in lines:
            if line and not line.startswith(" ") and not line.startswith("\t"):
                top_level_lines += 1
            if top_level_lines <= top_level_limit:
                trimmed_lines.append(line)
        
        return "\n".join(trimmed_lines)
    
    # Count top-level lines in the first code
    top_level_count_1 = 1
    
    # Trim the second code
    return trim_code(code2, top_level_count_1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rfile', type=str, default="")
    parser.add_argument('--wfile', type=str, default="")
    args = parser.parse_args()

    with open(args.rfile, "r") as f:
        data = [json.loads(line) for line in f]

    with open(args.wfile, "w") as f:
        for i in range(len(data)):
            entry = data[i]
            first_function_code = trim_code_by_top_level_lines(entry['parsecode'])
            task_id = entry['task_id']
            solution = first_function_code
            f.write(json.dumps({'task_id': task_id, 'solution': solution}) + "\n")
            

