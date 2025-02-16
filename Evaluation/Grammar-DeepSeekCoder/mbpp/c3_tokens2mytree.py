import pickle
from utils import *
from tqdm import tqdm
import time
import json
from transformers import AutoTokenizer
import sys
sys.setrecursionlimit(1000000)
# rules = pickle.load(open('pythonrule.pkl', 'rb'))

base_dir = '../../../Models/GrammarCoder-1.3B-Base'
tokenizer = AutoTokenizer.from_pretrained(base_dir)
rules = tokenizer.get_vocab()
rrdict = {}
for x in rules:
    rrdict[rules[x]] = x
# print("the length of rules is {}".format(len(rules)))

expandedname = []
for x in rules:
    tmpname = x.strip().split()[0]
    if len(x.strip().split()) < 3: # adding expandedname
        # idenid.append(c3_data[x])
        continue
    expandedname.append(tmpname)

identifiers_py = ['identifier', 'integer', 'float', 'string_literal', 'comment', 'line_continuation']
onelist = ['argument_list', 'block', 'tuple', 'list', 'expression_list', 'subscript', 'conditional_expression', 'tuple', 'comparison_operator', 'body', 'lambda_parameters', 'dictionary', 'tuple', 'slice', 'set', 'assert_statement', 'if_statement', 'pattern_list', 'tuple_pattern', 'concatenated_string', 'import_from_statement', 'list_pattern', 'try_statement', 'parameters', 'expression_statement', 'print_statement', 'module', "dictionary_comprehension", "global_statement", "decorated_definition", "generator_expression", "dotted_name"]
for i in range(len(onelist)):
    onelist[i] = onelist[i] + '_py'
for i in range(len(identifiers_py)):
    identifiers_py[i] += '_py'
expandedname.extend(identifiers_py)
pyonelistadd  = ["import_prefix_py", "list_comprehension_py",'for_in_clause_py','with_clause_py','type_parameter_py', 'set_comprehension_py','nonlocal_statement_py','import_statement_py','case_clause_py','future_import_statement_py','class_pattern_py','union_pattern_py','dict_pattern_py']
onelist += pyonelistadd

# pyonelistadd = ['type_parameter_py', 'try_statement_py', 'with_statement_py', 'for_statement_py', 'binary_operator_py', 'while_statement_py', 'list_comprehension_py', 'generator_expression_py', 'conditional_expression_py', 'concatenated_string_py', 'parenthesized_expression_py', 'attribute_py', 'block_py', 'parameters_py', 'for_in_clause_py', 'elif_clause_py', 'dictionary_py', 'lambda_py', 'tuple_py', 'argument_list_py', 'list_py', 'else_clause_py', 'finally_clause_py', 'function_definition_py', 'if_statement_py', 'class_definition_py', 'except_clause_py', 'boolean_operator_py', 'dictionary_comprehension_py', 'return_statement_py', 'assignment_py', 'augmented_assignment_py', 'with_clause_py', 'not_operator_py', 'as_pattern_py']
# onelist += pyonelistadd
length = []


    
def convertrulelist2tree(rulelist, lang='java', mode='gen'):
    if mode == 'gen':
        if lang == 'java':
            root = Node('java', 1)
        elif lang == 'python':
            root = Node('python', 1)
        elif lang == 'csharp':
            root = Node('csharp', 1)
    else:
        root = Node('<extra_id_0>', 1)
    expanded = [root]

    not_first_token = False
    for i in range(1, len(rulelist)):

        # start_time = time.time()    
        currexpanded = expanded[-1]
        rule = rrdict[rulelist[i]]
        lst = rule.strip().split()
        if len(lst) > 2:
            
            if not_first_token:
                if 'string_literal' not in currexpanded.name and 'comment' not in currexpanded.name and 'line_continuation' not in currexpanded.name:
                    expanded = expanded[:-1]
                    not_first_token = False
                else:
                    if rule.strip() == currexpanded.name + " -> End":
                        expanded = expanded[:-1]
                        not_first_token = False
                        continue
            
            currexpanded = expanded[-1]

            if rule.strip() == currexpanded.name + " -> End":
                expanded = expanded[:-1]
                # if 'string_literal' in currexpanded.name:
                #     currexpanded.child.reverse()
                continue

            if currexpanded.name not in onelist:
                expanded = expanded[:-1]
            if lst[0] != currexpanded.name:
                print(lst[0], i, currexpanded.name)
            if currexpanded.name != '<extra_id_0>':
                assert lst[0] == currexpanded.name, "lst[0] is {}, currexpanded.name is {}, i is {}".format(lst[0], currexpanded.name, i)
            for x in lst[2:]:
                newnode = Node(x, 1)
                newnode.father = currexpanded
                currexpanded.child.append(newnode)
            for j in range(len(currexpanded.child) - 1, len(currexpanded.child) - len(lst[2:]) - 1, -1):
                if currexpanded.child[j].name in expandedname:
                    expanded.append(currexpanded.child[j])
            # print("time0 is {}".format(endtime - start_time))
        else:

            if 'Ġ' in rule and not_first_token and 'string_literal' not in currexpanded.name and 'comment' not in currexpanded.name and 'line_continuation' not in currexpanded.name:
                expanded = expanded[:-1]
                
                newnode = Node(rule + '_ter', 1)
                currexpanded = expanded[-1]
                currexpanded.child.append(newnode)
                not_first_token = True

            else:
                newnode = Node(rule + '_ter', 1)
                currexpanded.child.append(newnode)
                not_first_token = True
            # print("time1 is {}".format(endtime - start_time))
    return root

# def mergeIdentifier(root):
#     if root.name in identifiers_py:
#         oname = ""
#         for x in root.child:
#             oname += x.name[:-4]
#         oname += "_ter"
#         nnode = Node(oname, 0)
#         nnode.father = root
#         root.child = [nnode]
#     for x in root.child:
#         mergeIdentifier(x)
#     return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--f_index', type=str, default="0")
    parser.add_argument('--lang', type=str, default="python")
    parser.add_argument('--rfile', type=str, default="")
    parser.add_argument('--wfile', type=str, default="")
    parser.add_argument('--isDebug', type=bool, default=False)
    args = parser.parse_args()

    lang = args.lang
    f_index = args.f_index
    tag = ""    

    rfile = args.rfile
    wfile = args.wfile


    if args.isDebug:
        tokendatas = pickle.load(open('mytokens.pkl', 'rb'))
        unparsetree = []
        for i in tqdm(range(len(tokendatas))):
            # try:
                tree = convertrulelist2tree(tokendatas[i]['rulelist'], 'python', 'gen')
                treestring = tree.printTree(tree)
                unparsetree.append({'id': tokendatas[i]['id'], 'tree': treestring})
            # except:
            #     print(tokendatas[i]['id'])
            #     continue
        

        with open('unparsetree.pkl', 'wb') as f:
            pickle.dump(unparsetree, f)
    else:
        datas = []
        with open(rfile, "r") as f:
            for i in f.readlines():
                datas.append(json.loads(i))

        with open(wfile, "w") as f:
            for i in tqdm(range(len(datas))):
                try:
                    tree = convertrulelist2tree(datas[i]['outrulelist'], 'python', 'gen')
                    treestring = tree.printTree(tree)
                    datas[i]['parseroot'] = treestring
                    f.write(json.dumps(datas[i]) + '\n')
                except:
                    datas[i]['parseroot'] = "error"
                    f.write(json.dumps(datas[i]) + '\n')
                    print("error")
                    print(i)
                    continue