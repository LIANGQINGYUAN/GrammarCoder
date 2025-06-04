import pickle 
from tqdm import tqdm
from utils import Node
import json
import sys
sys.setrecursionlimit(1000000)
simplestmt = ['assignment_py', 'return_statement_py', 'import_statement_py', 'raise_statement_py', 'pass_statement_py', 'delete_statement_py', 'yield_py', 'assert_statement_py', 'break_statement_py', 'continue_statement_py', 'global_statement_py', ' nonlocal_statement_py', 'import_from_statement_py', 'future_import_statement_py', 'expression_statement_py', 'exec_statement_py', 'comment_py']
compound_stmt = ['if_statement_py', 'while_statement_py', 'for_statement_py', 'try_statement_py', 'with_statement_py', 'function_definition_py', 'class_definition_py', 'decorator_py']
identifiers_py = ['identifier', 'integer', 'float', 'string_literal', 'comment', 'line_continuation']
for i in range(len(identifiers_py)):
    identifiers_py[i] += '_py'



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


def stringfy(node, hasspace=False):
    ans = ""
    if len(node.child) == 0:
        if node.name == 'updates':
            return ""

        if node.father.name in identifiers_py:
            ans = node.name[:-4].replace(' ', 'Ġ').replace('\n', 'Ċ').replace('\t', 'ĉ')
        else:
            ans = node.name[:-4]
    else:
        # if node.name == 'concatenated_string_py':
        #     for x in node.child[:-1]:
        #         codestr = stringfy(x, hasspace)
        #         ans += codestr + '\\Ċ'
        #     codestr = stringfy(node.child[-1], hasspace)
        #     ans += codestr
        # else:
            for x in node.child:
                codestr = stringfy(x, hasspace)
                ans += codestr + ' '
    if hasspace:
        if node.name == 'block_py':
            ans = ' <newline>' + ' <indent> ' + ans + ' <dedent> '
        if node.name in simplestmt:
            ans = ans + ' <newline> '
        if node.name in compound_stmt:
            ans = ans + ' <newline> '
    return ans
def normalize(codestr):
    lst = codestr.split()
    ans = ""
    currentBlock = ""
    for x in lst:
        if x == '<newline>':
            ans += '\n' + currentBlock
        elif x == '<indent>':
            currentBlock += '    '
            ans += '    '
        elif x == '<dedent>':
            currentBlock = currentBlock[:-4]
            ans = ans[:-4]
        else:
            ans += x + ' '
    return ans.replace('Ġ', ' ').replace('Ċ', '\n').replace('ĉ', '\t')

def printnode(node, depth):
    print('  ' * depth, node.name)
    for x in node.child:
        printnode(x, depth + 1)

def tree_to_code(tstr):
    root = parseTree(tstr)
    # printnode(root, 0)
    codestr = stringfy(root, True)
    # print(codestr)
    codestr = normalize(codestr)
    return codestr