from transformers import AutoTokenizer
from utils import Node
import numpy as np
from tqdm import tqdm
import pickle
import json
import sys
sys.setrecursionlimit(1000000)

def parseTree(treestr):
    
    tokens = treestr.strip().split('🚀')[:-1]
    root = Node(tokens[0], 0)
    currnode = root
    for i, x in enumerate(tokens[1:]):
        if x != "^":
            nnode = Node(x, i + 1)
            nnode.father = currnode
            currnode.child.append(nnode)
            currnode = nnode
        else:
            currnode = currnode.father
    return root
def filtererror(root):
    if root.name == 'ERROR' and len(root.child) != 0:
        return False
    for x in root.child:
        if not filtererror(x):
            return False
    return True
def removeComment(root):
    if root.name == "'comment'_ter":
        fnode = root.father.father.father
        if fnode is not None and root.father.father.name == 'expression_statement_py' and fnode.child.index(root.father.father) == 0:
            fnode.child = fnode.child[1:]
    for x in root.child:
        removeComment(x)

identifiers = ['identifier', 'integer', 'float', 'string_literal', 'comment', 'line_continuation']
base_dir = 'xxx'
tokenizer = AutoTokenizer.from_pretrained(base_dir)

onelist = ['argument_list', 'block', 'tuple', 'list', 'expression_list', 'subscript', 'conditional_expression', 'tuple', 'comparison_operator', 'body', 'lambda_parameters', 'dictionary', 'tuple', 'slice', 'set', 'assert_statement', 'if_statement', 'pattern_list', 'tuple_pattern', 'concatenated_string', 'import_from_statement', 'list_pattern', 'try_statement', 'parameters', 'expression_statement', 'print_statement', 'module', "dictionary_comprehension", "global_statement", "decorated_definition", "generator_expression", "dotted_name"]
for i in range(len(onelist)):
    onelist[i] = onelist[i] + '_py'
for i in range(len(identifiers)):
    identifiers[i] = identifiers[i] + '_py'
pyonelistadd  = ["import_prefix_py", "list_comprehension_py",'for_in_clause_py','with_clause_py','type_parameter_py', 'set_comprehension_py','nonlocal_statement_py','import_statement_py','case_clause_py','future_import_statement_py','class_pattern_py','union_pattern_py','dict_pattern_py']
# pyonelistadd = ['type_parameter_py', 'try_statement_py', 'with_statement_py', 'for_statement_py', 'binary_operator_py', 'while_statement_py', 'list_comprehension_py', 'generator_expression_py', 'conditional_expression_py', 'concatenated_string_py', 'parenthesized_expression_py', 'attribute_py', 'block_py', 'parameters_py', 'for_in_clause_py', 'elif_clause_py', 'dictionary_py', 'lambda_py', 'tuple_py', 'argument_list_py', 'list_py', 'else_clause_py', 'finally_clause_py', 'function_definition_py', 'if_statement_py', 'class_definition_py', 'except_clause_py', 'boolean_operator_py', 'dictionary_comprehension_py', 'return_statement_py', 'assignment_py', 'augmented_assignment_py', 'with_clause_py', 'not_operator_py', 'as_pattern_py']
onelist += pyonelistadd
rules = tokenizer.get_vocab()

rulelist = []


newrulelist = set()


def getRule(node, currId, d):
    global rules
    global onelist
    global rulelist
    # global endlist
    if node.name == "str_":
        assert(len(node.child) == 1)
    if len(node.child) == 0:
        return [], []
    
    child = node.child#sorted(node.child, key=lambda x:x.name)
    if len(node.child) == 1 and len(node.child[0].child) == 0 and node.name in identifiers:
        if node.name == "type":
            print(node.printTree(node))
            

        actions = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(" " + node.child[0].name[:-4]))

        if node.name == "string_literal_py":
            # if len(actions) > 512:
            #     print(node.child[0].name)

            node.child[0].name = "".join(tokenizer.convert_ids_to_tokens(actions)).replace("Ġ", " ").strip() + "_ter"
            actions = actions + [rules['string_literal_py -> End']]

        if node.name == "comment_py":
            node.child[0].name = "".join(tokenizer.convert_ids_to_tokens(actions)).replace("Ġ", " ").strip() + "_ter"
            actions = actions + [rules['comment_py -> End']]

        if node.name == "line_continuation_py":
            # print(node.child[0].name)
            node.child[0].name = "".join(tokenizer.convert_ids_to_tokens(actions)).replace("Ġ", " ").strip() + "_ter"
            actions = actions + [rules['line_continuation_py -> End']]

        # actions.reverse()

        for action in actions:
            rulelist.append(action)
            # endlist.append(len(rulelist) - 1)
        currid = len(rulelist) - 1
    else:
        if node.name not in onelist:
            rule = node.name + " -> "
            for x in child:
                rule += x.name + " "
            if rule in rules:
                rulelist.append(rules[rule])
            else:
                print("error in rule: " + rule + "\n")
                assert(0)
                rules[rule] = len(rules)
                rulelist.append(rules[rule])
                newrulelist.add(rule)
            # endlist.append(-1)
            currid = len(rulelist) - 1
            for x in child:
                getRule(x, currid, d + 1)
            # endlist[currid] = len(rulelist) - 1
        else:
            for x in (child):
                if (True):
                    rule = node.name + " -> " + x.name
                    if rule in rules:
                        rulelist.append(rules[rule])
                    else:
                        print("error in rule: " + rule + "\n")
                        assert(0)
                        rules[rule] = len(rules)
                        rulelist.append(rules[rule])
                        newrulelist.add(rule)
                    currid = len(rulelist) - 1
                # endlist.append(-1)
                getRule(x, len(rulelist) - 1, d + 1)
                # endlist[currid] = len(rulelist) - 1
            rule = node.name + " -> End "
            if rule in rules:
                rulelist.append(rules[rule])
            else:
                print("error in rule: " + rule + "\n")
                assert(0)
                rules[rule] = len(rules)
                rulelist.append(rules[rule])
                newrulelist.add(rule)
            # endlist.append(len(rulelist) - 1)
def mytree2tokens_json(rfile, wfile):
    global rulelist
    # global endlist
    datas = []
    with open(rfile, 'r') as f:
        for i in f.readlines():
            datas.append(json.loads(i))

    with open(wfile, 'w') as f:            
        for i in tqdm(range(len(datas))):
            try:
                root = parseTree(datas[i]['root'])
                nroot = Node("python", 0)
                nroot.child = [root]
                root.father = nroot
                root = nroot

                if not filtererror(root):
                    continue

                # removeComment(root)
                rulelist = []
                # endlist = []
                getRule(root, -1, 0)

                datas[i]['rulelist'] = [rules['start -> python']]+ rulelist
                # datas[i]['endlist'] = [2]+ endlist
                f.write(json.dumps(datas[i]) + "\n")
            except:
                continue

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--isDebug', type=bool, default=False)
    parser.add_argument('--rfile', type=str, default="")
    parser.add_argument('--wfile', type=str, default="")
    args = parser.parse_args()

    rfile = args.rfile
    wfile = args.wfile

    if args.isDebug:
        with open("mytree.pkl", "rb") as f:
            datas = pickle.load(f)
        tokendatas, rules = mytree2tokens(datas)
        print(newrulelist)
        pickle.dump(newrulelist, open("newrulelist.pkl", "wb"))
        with open("mytokens.pkl", "wb") as f:
            pickle.dump(tokendatas, f)
        with open("pythonrule.pkl", "wb") as f:
            pickle.dump(rules, f)

    else:
        mytree2tokens_json(rfile, wfile)