class Node:
    def __init__(self, name, d, type='init'):
        self.name = name
        self.id = d
        self.child = []
        self.father = None
    def printTree(self, r):
      s = r.name + "🚀"
      if len(r.child) == 0:
        s += "^🚀"
        return s
      for c in r.child:
        s += self.printTree(c)
      s += "^🚀"
      return s
    
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
