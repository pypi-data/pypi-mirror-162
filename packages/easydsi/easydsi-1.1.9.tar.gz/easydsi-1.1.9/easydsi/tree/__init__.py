# Import the libraries
from binarytree import bst, Node, build

class Node():
    pass

class Tree():

    root = None

    def __init__(self, data):
        if not data:
            self.root = None
        else:
            self.root = build(data)

    def __str__(self):
        return str(self.root)

    def __repr__(self):
        return str(self.root)

    # Getting list of nodes
    def get_nodes(self):
        return list(self.root)
  
    # Getting inorder of nodes
    def inorder(self):
        return self.root.inorder
    
    # Get the size of tree
    def get_size(self):
        return self.root.size

    # Get the height of tree
    def get_height(self):
        return self.root.height
    
    # Get all properties at once
    def get_properties(self):
        return self.root.properties

class BinaryTree(Tree):
    def __init__(self, data):
        super().__init__(data)

def binary_tree(data = None):
    return BinaryTree(data)
