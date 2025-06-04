import json
import re
from tqdm import tqdm
from c3_tokens2mytree import tokenlist_to_tree
from c4_mytree2code import tree_to_code
from transformers import AutoTokenizer
import argparse

grammartokenizer = AutoTokenizer.from_pretrained("../../Models/GrammarCoder-7B")
def extract_java_code_from_dicts(dict_list):

    r_dick_list = []
    python_code_pattern = re.compile(r"```python\n.*?```", re.DOTALL)
    pygrammar_code_pattern = re.compile(r"```pygrammar\n.*?```", re.DOTALL)

    for item in tqdm(dict_list):

        python_code_matches = python_code_pattern.findall(item['output'])
        pygrammar_code_matches = pygrammar_code_pattern.findall(item['output'])            

        python_code_matches = [code[10:-3].strip() for code in python_code_matches]
        pygrammar_code_matches = [code[13:-4].strip() for code in pygrammar_code_matches]

        if len(python_code_matches) > 0:
            item['solution'] = python_code_matches[0]
        elif len(pygrammar_code_matches) > 0:
            try :
                item['solution'] = tree_to_code(tokenlist_to_tree(grammartokenizer.tokenize(pygrammar_code_matches[0])))
            except:
                item['solution'] = "'grammar_wrong'"
        else:
            item['solution'] = "'no_code'"

        r_dick_list.append(json.dumps({"task_id": item['task_id'], "solution":item["solution"]}))
    return r_dick_list

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    basedir = '.'
    argparser.add_argument('--input', type=str, default=f'{basedir}/xxx.json')
    argparser.add_argument('--output', type=str, default=f'{basedir}/xxx.jsonl')
    args = argparser.parse_args()
    with open(args.input, 'r') as f:
        dict_list = [json.loads(line) for line in f]
    r_dict_list = extract_java_code_from_dicts(dict_list)
    with open(args.output, 'w') as f:
        f.write("\n".join(r_dict_list))