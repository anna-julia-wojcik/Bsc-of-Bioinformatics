from zad1 import RegBinTree, RegBinNode, Leaf

# Example from the task description:
#
#          A(B)
#         /    \
#       B(W)   C(W)
#      /   \   /  \
#    D(B) E(W) F(B) G(B)

D = Leaf('B')
E = Leaf('W')
F = Leaf('B')
G = Leaf('B')
B = RegBinNode('W', D, E)
C = RegBinNode('W', F, G)
A = RegBinNode('B', B, C)
tree = RegBinTree(A)

print("Tree:")
print(tree)

# Test compute_alt_path_lengths
tree.compute_alt_path_lengths()

print("After compute_alt_path_lengths:")
print(tree)

assert D.alt_length == 0, f"D.alt_length = {D.alt_length}, expected 0"
assert E.alt_length == 0, f"E.alt_length = {E.alt_length}, expected 0"
assert F.alt_length == 0, f"F.alt_length = {F.alt_length}, expected 0"
assert G.alt_length == 0, f"G.alt_length = {G.alt_length}, expected 0"
assert B.alt_length == 1, f"B.alt_length = {B.alt_length}, expected 1"
assert C.alt_length == 1, f"C.alt_length = {C.alt_length}, expected 1"
assert A.alt_length == 2, f"A.alt_length = {A.alt_length}, expected 2"
print("compute_alt_path_lengths: OK!\n")

# Test find_longest_alt_path
path = tree.find_longest_alt_path()
path_colors = [v.color for v in path]

print(f"Longest alternating path from root: {path_colors}")
print(f"Length (edges): {len(path) - 1}")

assert len(path) == 3, f"Expected path of length 2 (3 vertices), got {len(path) - 1} ({len(path)} vertices)"
assert path[0] is A, "Path should start at root A(B)"
assert path[1] is B, "Second vertex should be B(W)"
assert path[2] is D, "Third vertex should be D(B)"
print("find_longest_alt_path: OK!")

# ── Test 1: tree consisting of a single leaf ─────────────────────────────────
print("Test 1: tree with a single leaf")

A = Leaf('B')
tree = RegBinTree(A)
tree.compute_alt_path_lengths()

assert A.alt_length == 0, f"A.alt_length = {A.alt_length}, expected 0"

path = tree.find_longest_alt_path()
assert len(path) == 1, f"Expected 1 vertex, got {len(path)}"
assert path[0] is A, "Path should contain only leaf A"
print("Test 1: OK!\n")

# ── Test 2: tree with root and two leaves of the same color ──────────────────
print("Test 2: root and two leaves of the same color")
#
#   A(B)
#  /    \
# B(B)  C(B)

B = Leaf('B')
C = Leaf('B')
A = RegBinNode('B', B, C)
tree = RegBinTree(A)
tree.compute_alt_path_lengths()

assert B.alt_length == 0
assert C.alt_length == 0
assert A.alt_length == 0, f"A.alt_length = {A.alt_length}, expected 0"

path = tree.find_longest_alt_path()
assert len(path) == 1, f"Expected 1 vertex, got {len(path)}"
assert path[0] is A
print("Test 2: OK!\n")

# ── Test 3: right branch longer than left ────────────────────────────────────
print("Test 3: right branch longer")
#
#      A(B)
#     /    \
#   B(B)   C(W)
#          /  \
#        D(B) E(B)

B = Leaf('B')
D = Leaf('B')
E = Leaf('B')
C = RegBinNode('W', D, E)
A = RegBinNode('B', B, C)
tree = RegBinTree(A)
tree.compute_alt_path_lengths()

assert B.alt_length == 0
assert D.alt_length == 0
assert E.alt_length == 0
assert C.alt_length == 1, f"C.alt_length = {C.alt_length}, expected 1"
assert A.alt_length == 2, f"A.alt_length = {A.alt_length}, expected 2"

path = tree.find_longest_alt_path()
assert len(path) == 3, f"Expected 3 vertices, got {len(path)}"
assert path[0] is A
assert path[1] is C
assert path[2] is D or path[2] is E  # left child preferred on tie
print("Test 3: OK!\n")

# ── Test 4: long alternating path going left ─────────────────────────────────
print("Test 4: long alternating path going left")
#
#         A(B)
#        /
#       B(W)
#      /
#     C(B)
#    /
#   D(W)

D = Leaf('W')
C = RegBinNode('B', D, Leaf('B'))
B = RegBinNode('W', C, Leaf('W'))
A = RegBinNode('B', B, Leaf('B'))
tree = RegBinTree(A)
tree.compute_alt_path_lengths()

assert D.alt_length == 0
assert C.alt_length == 1, f"C.alt_length = {C.alt_length}, expected 1"
assert B.alt_length == 2, f"B.alt_length = {B.alt_length}, expected 2"
assert A.alt_length == 3, f"A.alt_length = {A.alt_length}, expected 3"

path = tree.find_longest_alt_path()
assert len(path) == 4, f"Expected 4 vertices, got {len(path)}"
assert path[0] is A
assert path[1] is B
assert path[2] is C
assert path[3] is D
print("Test 4: OK!\n")

# ── Test 5: tie between left and right — left child preferred ─────────────────
print("Test 5: tie between alt_length of left and right child")
#
#        A(B)
#       /    \
#     B(W)   C(W)
#     /       \
#   D(B)      E(B)

D = Leaf('B')
E = Leaf('B')
B = RegBinNode('W', D, Leaf('W'))
C = RegBinNode('W', Leaf('W'), E)
A = RegBinNode('B', B, C)
tree = RegBinTree(A)
tree.compute_alt_path_lengths()

assert B.alt_length == 1
assert C.alt_length == 1
assert A.alt_length == 2

path = tree.find_longest_alt_path()
assert len(path) == 3, f"Expected 3 vertices, got {len(path)}"
assert path[0] is A
assert path[1] is B  # left child preferred on tie
assert path[2] is D
print("Test 5: OK!\n")

# ── Test 6: all nodes perfectly alternating ───────────────────────────────────
print("Test 6: perfect alternation")
#
#        A(B)
#       /    \
#     B(W)   C(W)
#    /   \
#  D(B)  E(B)

D = Leaf('B')
E = Leaf('B')
B = RegBinNode('W', D, E)
C = Leaf('W')
A = RegBinNode('B', B, C)
tree = RegBinTree(A)
tree.compute_alt_path_lengths()

assert D.alt_length == 0
assert E.alt_length == 0
assert B.alt_length == 1
assert C.alt_length == 0
assert A.alt_length == 2

path = tree.find_longest_alt_path()
assert len(path) == 3, f"Expected 3 vertices, got {len(path)}"
assert path[0] is A
assert path[1] is B
assert path[2] is D
print("Test 6: OK!\n")

# ── Test 7: mixed alternation ─────────────────────────────────────────────────
print("Test 7: Wera")
#          A(B)
#         /    \
#       B(B)   C(W)
#      /   \   /  \
#    D(W) E(W) F(B) G(B)

D = Leaf('W')
E = Leaf('W')
F = Leaf('B')
G = Leaf('B')
B = RegBinNode('B', D, E)
C = RegBinNode('W', F, G)
A = RegBinNode('B', B, C)
t11 = RegBinTree(A)

t11.compute_alt_path_lengths()

# Leaves
assert D.alt_length == 0, f"D.alt_length = {D.alt_length}, expected 0"
assert E.alt_length == 0, f"E.alt_length = {E.alt_length}, expected 0"
assert F.alt_length == 0, f"F.alt_length = {F.alt_length}, expected 0"
assert G.alt_length == 0, f"G.alt_length = {G.alt_length}, expected 0"

# Internal nodes
assert B.alt_length == 1, f"B.alt_length = {B.alt_length}, expected 1"  # D(W) and E(W) != B(B)
assert C.alt_length == 1, f"C.alt_length = {C.alt_length}, expected 1"  # F(B) and G(B) != C(W)
assert A.alt_length == 2, f"A.alt_length = {A.alt_length}, expected 2"  # B(B)==A(B) rejected, C(W)!=A(B) → 1+1=2

print("compute_alt_path_lengths: OK!")

# Path: A(B) → C(W) → F(B)  [left child preferred on tie between F/G]
path = t11.find_longest_alt_path()
path_colors = [v.color for v in path]

print(f"Longest alternating path: {path_colors}")
print(f"Length (edges): {len(path) - 1}")

assert len(path) == 3, f"Expected 3 vertices, got {len(path)}"
assert path[0] is A, "Path should start at A(B)"
assert path[1] is C, "Second vertex should be C(W)"
assert path[2] is F, "Third vertex should be F(B) (left child preferred)"

print("find_longest_alt_path: OK!")

# ── Test 8: single leaf ───────────────────────────────────────────────────────
A = Leaf('B')
tree = RegBinTree(A)
tree.compute_alt_path_lengths()

assert A.alt_length == 0, f"A.alt_length = {A.alt_length}, expected 0"

path = tree.find_longest_alt_path()
assert len(path) == 1, f"Expected 1 vertex, got {len(path)}"
assert path[0] is A, "Path should contain only leaf A"

print("Single leaf test: OK!")

# ── Test 9: single leaf ───────────────────────────────────────────────────────
B = Leaf('B')
C = Leaf('B')
A = RegBinNode('B', B, C)
t2 = RegBinTree(A)

B = Leaf('B')
C = Leaf('B')
A = RegBinNode('B', B, C)
t2 = RegBinTree(A)
t2.compute_alt_path_lengths()

assert B.alt_length == 0, f"B.alt_length = {B.alt_length}, expected 0"
assert C.alt_length == 0, f"C.alt_length = {C.alt_length}, expected 0"
assert A.alt_length == 0, f"A.alt_length = {A.alt_length}, expected 0"

print("compute_alt_path_lengths: OK!")

path = t2.find_longest_alt_path()
assert len(path) == 0, f"Expected 1 vertex, got {len(path)}"
assert path[0] is [], "Path should contain only root A"

print("find_longest_alt_path: OK!")

print("All tests passed successfully!")
