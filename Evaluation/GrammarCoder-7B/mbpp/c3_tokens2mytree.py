import pickle
from utils import *
from tqdm import tqdm
import time
import json
from transformers import AutoTokenizer
import sys
sys.setrecursionlimit(1000000)

tokenizer = AutoTokenizer.from_pretrained('../../Models/GrammarCoder-7B')

onelist = ['argument_list', 'block', 'tuple', 'list', 'expression_list', 'subscript', 'conditional_expression', 'tuple', 'comparison_operator', 'body', 'lambda_parameters', 'dictionary', 'tuple', 'slice', 'set', 'assert_statement', 'if_statement', 'pattern_list', 'tuple_pattern', 'concatenated_string', 'import_from_statement', 'list_pattern', 'try_statement', 'parameters', 'expression_statement', 'print_statement', 'module', "dictionary_comprehension", "global_statement", "decorated_definition", "generator_expression", "dotted_name"]
for i in range(len(onelist)):
    onelist[i] = onelist[i] + '_py'
pyonelistadd  = ["import_prefix_py", "list_comprehension_py",'for_in_clause_py','with_clause_py','type_parameter_py', 'set_comprehension_py','nonlocal_statement_py','import_statement_py','case_clause_py','future_import_statement_py','class_pattern_py','union_pattern_py','dict_pattern_py']
onelist += pyonelistadd

left_border = "<|"
right_border = "|>"

def check_and_sub_borders(s):
    if s.startswith(left_border) and s.endswith(right_border):
        return True, s[2:-2]
    return False, s
def stringfy(l):
    return tokenizer.convert_tokens_to_string(l)

def convertrulelist2tree(rulelist, lang='python'):
    if lang == 'java':
        root = Node('java', 1)
    elif lang == 'python':
        root = Node('python', 1)
    elif lang == 'csharp':
        root = Node('csharp', 1)
    
    expanded = [root]

    last_is_terminal = False
    terminal = []

    for i in range(1, len(rulelist)):

        currexpanded = expanded[-1]
        isrule, token = check_and_sub_borders(rulelist[i])
        # for i in range(len(expanded) - 1, -1, -1):
        #     print(expanded[i].name, end=' ')
        # print(currexpanded.name, token)
        if not isrule:
            if last_is_terminal:
                if token.startswith("Ġ"):
                    if 'string_literal' not in currexpanded.name and 'comment' not in currexpanded.name and 'line_continuation' not in currexpanded.name:
                        
                        currexpanded.child.append(Node(stringfy(terminal)[1:] + '_ter', 1))
                        expanded = expanded[:-1]
                        terminal = [token]
                        last_is_terminal = True
                    else:
                        terminal += [token]
                        last_is_terminal = True
                else:
                    terminal += [token]
                    last_is_terminal = True
            else:
                terminal = [token]
                last_is_terminal = True
        else:
            
            lst = token.strip().split(" ")
            if last_is_terminal:
                if 'string_literal' not in currexpanded.name and 'comment' not in currexpanded.name and 'line_continuation' not in currexpanded.name:
                    currexpanded.child.append(Node(stringfy(terminal)[1:] + '_ter', 1))
                    expanded = expanded[:-1]
                    terminal = []
                    last_is_terminal = False
                else:
                    if token.strip() == currexpanded.name + " -> End":
                        currexpanded.child.append(Node(stringfy(terminal)[1:] + '_ter', 1))
                        expanded = expanded[:-1]
                        terminal = []
                        last_is_terminal = False
                        continue
            
            currexpanded = expanded[-1]

            if token.strip() == currexpanded.name + " -> End":
                expanded = expanded[:-1]
                continue

            if currexpanded.name not in onelist:
                expanded = expanded[:-1]
            
            assert lst[0] == currexpanded.name, "lst[0] is {}, currexpanded.name is {}, i is {}".format(lst[0], currexpanded.name, i)
            
            for x in lst[2:]:
                newnode = Node(x, 1)
                newnode.father = currexpanded
                currexpanded.child.append(newnode)
            for j in range(len(currexpanded.child) - 1, len(currexpanded.child) - len(lst[2:]) - 1, -1):
                if not currexpanded.child[j].name.endswith('_ter'):
                    expanded.append(currexpanded.child[j])

    return root

def tokenlist_to_tree(tokenlist):
    try:
        root = convertrulelist2tree(tokenlist)
        return root.printTree(root)
    except Exception as e:
        print(e)
        return None

