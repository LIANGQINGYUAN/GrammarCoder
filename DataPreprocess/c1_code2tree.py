from tree_sitter import Language, Parser
import tree_sitter_python as tspython
from tqdm import tqdm
from utils import Node
import traceback
import json
import pickle
import sys
sys.setrecursionlimit(1000000)

PYTHON_LANGUAGE = Language(tspython.language())
parser_python = Parser(PYTHON_LANGUAGE)


def addter(root):
    if len(root.child) == 0:
        root.name += "_ter"
        return
    else:
        for x in root.child:
            addter(x)
        return
def addlang(root):
    if len(root.child) == 0:
        return
    else:
        root.name += "_py"
        for x in root.child:
            addlang(x)
        return
    
def revisitTree(root, newroot, codestr, cursor):

    if root.type == 'string' or root.type == 'comment' or root.type == 'line_continuation' or root.type == 'concatenated_string':
        s = cursor.node.start_byte
        e = cursor.node.end_byte

        if root.type == 'string' or root.type == 'concatenated_string':
            newroot.name = 'string_literal'
        elif root.type == 'comment':
            newroot.name = 'comment'
        elif root.type == 'line_continuation':
            newroot.name = 'line_continuation'    

        ans = codestr[s:e]
        ans = ans.decode('utf-8')

        if root.type != ans:
            tnode = Node(ans, 0)
            newroot.child.append(tnode)
        return
    

    if " " in root.type:
        newroot.name = root.type.replace(" ", "_")
    else:
        newroot.name = root.type
    
    if newroot.name == 'str_':
        exit(0)
    child = []
    haschild = cursor.goto_first_child()

    for x in root.children:
        field_name = cursor.field_name

        tmp = None
        if field_name is not None:
            tnode = Node(field_name, 0)
            tmp = Node('init', 0)
            tnode.child.append(tmp)
            child.append(tnode)
        else:   
            if x.type == "comment" or (x.type == "block" and len(x.children) == 0) or x.type == "line_continuation":    
                pass
            else:      
                tmp = Node('init', 0)
                child.append(tmp)
        if tmp is not None:
            revisitTree(x, tmp, codestr, cursor)
        cursor.goto_next_sibling()
    newroot.child = child
    if haschild:
        cursor.goto_parent()
    else:
        s = cursor.node.start_byte
        e = cursor.node.end_byte

        ans = codestr[s:e]            
        ans = ans.decode('utf-8')
        if root.type != ans:
            tnode = Node(ans, 0)
            newroot.child.append(tnode)

            if root.type == 'block':
                # assert("wrongway")
                newroot.name = 'comment'
        #assert(0)

def parserTree(input_file, output_file, codetag = 'code'):
    with open(input_file, "r") as f:
        datas = [json.loads(line) for line in tqdm(f)]

    with open(output_file, 'w+') as file:
        for item in tqdm(datas):
            try:
                if not item[codetag]:
                    continue
            
                line = item[codetag].replace("🚀", "").replace('\r', '').replace("\'\u0000\'", "empstr")
            
                lines = line.split("\n")
                pres = [len(line) < 1000 for line in lines]
                if not all(pres):
                    continue
                bline = line.encode('utf-8')
                candidates = parser_python.parse(bline).root_node
                cursor = candidates.walk()
                sroot = Node('init', 0)
                revisitTree(candidates, sroot, bline, cursor)
                if 'module🚀ERROR🚀' in sroot.printTree(sroot):
                    continue
            
                root = [sroot]#getMethod(sroot)
                addter(root[0])
                addlang(root[0])
            

                tstr = root[0].printTree(root[0])
                if 'ERROR_py' in tstr:
                    continue
                item['root'] = tstr
                file.write(json.dumps(item)+'\n')
            except:
                traceback.print_exc()
                try:
                    print(codes[i])
                    print(sroot.printTree(sroot))
                except:
                    pass
                assert(0)
                pass

if __name__ == "__main__":
    debug = False
    if debug:
        inputfile = "xxx.jsonl"
        outputfile = "xxx.jsonl"
        parserTree(inputfile, outputfile)
    else:
        import multiprocessing

        begin_index = 0
        end_index = 100


        for i in range(begin_index, end_index):
            inputfile = f"./original/input_{i}.jsonl"
            outputfile = f"./c1_data/output_{i}.jsonl"
            t = multiprocessing.Process(target=parserTree, args=(inputfile, outputfile))
            t.start()
