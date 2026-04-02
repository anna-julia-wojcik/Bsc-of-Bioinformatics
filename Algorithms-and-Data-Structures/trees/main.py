# Helper function adding a space at the beginning of each line in a string.
def indent(s: str) -> str:
    return '\n'.join(' ' + line for line in s.splitlines())


class Leaf:
    # Fields below belong to the instance, not the class! (they are not static).
    # If there were no type hints, a variable declared here would be static.
    color: str  # 'B' (black) or 'W' (white)
    alt_length: int

    def __init__(self, color: str):
        self.color = color
        self.alt_length = -1

    # Simple helper function to print the (sub)tree; also present in RegBinNode.
    def __str__(self):
        return f'Leaf({self.color}) [alt_l: {self.alt_length}]\n'

    # Calculate the length of an alternating path down the tree, starting at this node.
    # For a leaf, the alternating path length is 0.
    def compute_alt_path_length(self):
        self.alt_length = 0
        return 0

    def find_longest_alt_path(self, nodes):
        # The longest path ends in a leaf, so we just add the leaf to the result list
        nodes.append(self)


class RegBinNode:
    # Fields below belong to the instance, not the class! (they are not static)
    color: str  # 'B' (black) or 'W' (white)
    left: Union['RegBinNode', Leaf]
    right: Union['RegBinNode', Leaf]
    alt_length: int

    def __init__(self,
                 color: str,
                 left: Union['RegBinNode', Leaf],
                 right: Union['RegBinNode', Leaf]):
        self.color = color
        self.left = left
        self.right = right
        self.alt_length = -1

    def __str__(self):
        return f'Node({self.color}) [alt_l: {self.alt_length}]\n{indent(str(self.left))}\n{indent(str(self.right))}'

    # Calculate the length of an alternating path down the tree, starting at this node.
    # Works recursively: first, alt_length is calculated for the children, then based on them,
    # the value for the current node is determined.
    # Only children with a different color than the current node are considered (alternating path).
    # If no child meets this condition, alt_length is 0.
    def compute_alt_path_length(self):
        left_child_alt_path_length = self.left.compute_alt_path_length()
        right_child_alt_path_length = self.right.compute_alt_path_length()
        left_length = 0
        right_length = 0
        
        if self.left.color != self.color:
            left_length = 1 + left_child_alt_path_length
        if self.right.color != self.color:
            right_length = 1 + right_child_alt_path_length
            
        self.alt_length = max(left_length, right_length)
        return max(left_length, right_length)

    def find_longest_alt_path(self, nodes):
        # Add the node to the result list
        nodes.append(self)

        # If the parent doesn't have an alternating path originating from it, stop checking its children
        if self.alt_length > 0:
            if (self.left.color != self.color and
                    (self.left.alt_length >= self.right.alt_length or self.right.color == self.color)):
                # If the left child has a longer/equal alternating path originating from it than the right one, 
                # go down the 'left path' - recursively call the function for the left child to check its children, etc.
                self.left.find_longest_alt_path(nodes)
            else:
                # If the right child has a longer alternating path than the left one - call the function for the right child
                self.right.find_longest_alt_path(nodes)


class RegBinTree:
    # The 'root' field belongs to the instance, not the class! (it is not static)
    root: RegBinNode | Leaf | None

    def __init__(self, node: RegBinNode | Leaf | None = None):
        self.root = node

    def compute_alt_path_lengths(self):
        self.root.compute_alt_path_length()

    def find_longest_alt_path(self) -> list:
        """
        Call the function returning the longest alternating path originating from the root. 
        We assume that the 'alt_length' attributes in the tree nodes are populated and contain valid (comparable) values.
        In the case of multiple paths of the maximum length, only the one with the most left children is returned.

        Returns:
            list: list of nodes (RegBinNode or Leaf)
        """
        nodes = []
        # If any path can be routed from the root, call the function on the root
        if self.root.alt_length != 0:
            self.root.find_longest_alt_path(nodes)

        return nodes

    def __str__(self):
        return '(Empty tree)' if self.root is None else str(self.root)