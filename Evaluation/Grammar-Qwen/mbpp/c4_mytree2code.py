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
from transformers import AutoTokenizer
base_dir = '../../../Models/GrammarCoder-1.5B-Base'
tokenizer = AutoTokenizer.from_pretrained(base_dir)

def mergeIdentifier(root):
    if root.name in identifiers_py:
        # print('root:', root.name)
        if False:
            pass
        else:
            # oname = ''
            oname = []
            for x in root.child:
                if len(x.child) == 0:
                    # oname += x.name[:-4]
                    oname.append(x.name[:-4])
                else: # string_literal, comment
                    # print([y.name for y in x.child])
                    for y in range(len(x.child)):
                        # oname += x.child[y].name[:-4]
                        oname.append(x.child[y].name[:-4])
                    # print('oname:', oname)
            # oname = oname.replace('Ġ', ' ').replace('Ċ', ' ').replace('ĉ', ' ') # space, \n, \t
            # print("oname before: ", oname)
            # oname = tokenizer.decode(tokenizer.convert_tokens_to_ids(oname))
            oname = tokenizer.convert_tokens_to_string(oname) # decode is slightly different from convert_tokens_to_string when occurs special token string such as '\\t\
            # print("oname after: ", oname)
            oname += "_ter"
            # print(oname)
            nnode = Node(oname, 0)
            nnode.father = root
            root.child = [nnode]
    for x in root.child:
        mergeIdentifier(x)
    return



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
            ans = node.name[1:-4].replace(' ', 'Ġ').replace('\n', 'Ċ').replace('\t', 'ĉ')
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

if __name__ == "__main__":
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
        unparsecode = []
        unparsetree = pickle.load(open('unparsetree.pkl', 'rb'))
        for i in tqdm(range(len(unparsetree))):
            root = parseTree(unparsetree[i]['tree'])
            # printnode(root, 0)
            mergeIdentifier(root)
            code = stringfy(root, True)
            code = normalize(code)
            unparsecode.append({'id': unparsetree[i]['id'], 'code': code})
            with open('pythoncode/{}.py'.format(unparsetree[i]['id']), 'w') as f:
                f.write(code)
        with open('unparsecode.pkl', 'wb') as f:
            pickle.dump(unparsecode, f)

    else:
        datas = []
        with open(rfile, "r") as f:
            for i in f.readlines():
                datas.append(json.loads(i))

        with open(wfile, "w") as f:
            for i in tqdm(range(len(datas))):
                if datas[i]['parseroot'] == "error":
                    datas[i]['parsecode'] = "error"
                    f.write(json.dumps(datas[i]) + '\n')
                else:
                    root = parseTree(datas[i]['parseroot'])
                    mergeIdentifier(root)
                    code = stringfy(root, True)
                    code = normalize(code)
                    datas[i]['parsecode'] = code
                    f.write(json.dumps(datas[i]) + '\n')