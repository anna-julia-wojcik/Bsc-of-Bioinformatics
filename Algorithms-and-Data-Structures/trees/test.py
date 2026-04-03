from zad1 import RegBinTree, RegBinNode, Leaf

# Przykład z treści zadania:
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

print("Drzewo:")
print(tree)

# Test compute_alt_path_lengths
tree.compute_alt_path_lengths()

print("Po compute_alt_path_lengths:")
print(tree)

assert D.alt_length == 0, f"D.alt_length = {D.alt_length}, oczekiwano 0"
assert E.alt_length == 0, f"E.alt_length = {E.alt_length}, oczekiwano 0"
assert F.alt_length == 0, f"F.alt_length = {F.alt_length}, oczekiwano 0"
assert G.alt_length == 0, f"G.alt_length = {G.alt_length}, oczekiwano 0"
assert B.alt_length == 1, f"B.alt_length = {B.alt_length}, oczekiwano 1"
assert C.alt_length == 1, f"C.alt_length = {C.alt_length}, oczekiwano 1"
assert A.alt_length == 2, f"A.alt_length = {A.alt_length}, oczekiwano 2"
print("compute_alt_path_lengths: OK!\n")

# Test find_longest_alt_path
path = tree.find_longest_alt_path()
path_colors = [v.color for v in path]

print(f"Najdłuższa naprzemienna ścieżka od korzenia: {path_colors}")
print(f"Długość (krawędzie): {len(path) - 1}")

assert len(path) == 3, f"Oczekiwano ścieżki długości 2 (3 wierzchołki), dostano {len(path) - 1} ({len(path)} wierzchołków)"
assert path[0] is A, "Ścieżka powinna zaczynać się od korzenia A(B)"
assert path[1] is B, "Drugi wierzchołek powinien to B(W)"
assert path[2] is D, "Trzeci wierzchołek powinien to D(B)"
print("find_longest_alt_path: OK!")

# ── Test 1: drzewo z samego liścia ──────────────────────────────────────────
print("Test 1: drzewo z samego liścia")

A = Leaf('B')
tree = RegBinTree(A)
tree.compute_alt_path_lengths()

assert A.alt_length == 0, f"A.alt_length = {A.alt_length}, oczekiwano 0"

path = tree.find_longest_alt_path()
assert len(path) == 1, f"Oczekiwano 1 wierzchołka, dostano {len(path)}"
assert path[0] is A, "Ścieżka powinna zawierać tylko liść A"
print("Test 1: OK!\n")

# ── Test 2: drzewo z korzeniem i dwoma liśćmi, brak naprzemienności ─────────
print("Test 2: korzeń i dwa liście tego samego koloru")
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
assert A.alt_length == 0, f"A.alt_length = {A.alt_length}, oczekiwano 0"

path = tree.find_longest_alt_path()
assert len(path) == 1, f"Oczekiwano 1 wierzchołka, dostano {len(path)}"
assert path[0] is A
print("Test 2: OK!\n")

# ── Test 3: prawa gałąź dłuższa niż lewa ────────────────────────────────────
print("Test 3: prawa gałąź dłuższa")
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
assert C.alt_length == 1, f"C.alt_length = {C.alt_length}, oczekiwano 1"
assert A.alt_length == 2, f"A.alt_length = {A.alt_length}, oczekiwano 2"

path = tree.find_longest_alt_path()
assert len(path) == 3, f"Oczekiwano 3 wierzchołków, dostano {len(path)}"
assert path[0] is A
assert path[1] is C
assert path[2] is D or path[2] is E  # lewe dziecko preferred przy równości
print("Test 3: OK!\n")

# ── Test 4: długa naprzemienna ścieżka po lewej stronie ─────────────────────
print("Test 4: długa naprzemienna ścieżka w lewo")
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
assert C.alt_length == 1, f"C.alt_length = {C.alt_length}, oczekiwano 1"
assert B.alt_length == 2, f"B.alt_length = {B.alt_length}, oczekiwano 2"
assert A.alt_length == 3, f"A.alt_length = {A.alt_length}, oczekiwano 3"

path = tree.find_longest_alt_path()
assert len(path) == 4, f"Oczekiwano 4 wierzchołków, dostano {len(path)}"
assert path[0] is A
assert path[1] is B
assert path[2] is C
assert path[3] is D
print("Test 4: OK!\n")

# ── Test 5: remis między lewą a prawą — preferujemy lewe dziecko ────────────
print("Test 5: remis alt_length lewego i prawego dziecka")
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
assert len(path) == 3, f"Oczekiwano 3 wierzchołków, dostano {len(path)}"
assert path[0] is A
assert path[1] is B  # lewe dziecko preferowane przy równości
assert path[2] is D
print("Test 5: OK!\n")

# ── Test 6: wszystkie węzły naprzemienne ────────────────────────────────────
print("Test 6: idealna naprzemienność")
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
assert len(path) == 3, f"Oczekiwano 3 wierzchołków, dostano {len(path)}"
assert path[0] is A
assert path[1] is B
assert path[2] is D
print("Test 6: OK!\n")

# ── Test 7: wszystkie węzły naprzemienne ────────────────────────────────────
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

# Liście
assert D.alt_length == 0, f"D.alt_length = {D.alt_length}, oczekiwano 0"
assert E.alt_length == 0, f"E.alt_length = {E.alt_length}, oczekiwano 0"
assert F.alt_length == 0, f"F.alt_length = {F.alt_length}, oczekiwano 0"
assert G.alt_length == 0, f"G.alt_length = {G.alt_length}, oczekiwano 0"

# Węzły wewnętrzne
assert B.alt_length == 1, f"B.alt_length = {B.alt_length}, oczekiwano 1"  # D(W) i E(W) != B(B)
assert C.alt_length == 1, f"C.alt_length = {C.alt_length}, oczekiwano 1"  # F(B) i G(B) != C(W)
assert A.alt_length == 2, f"A.alt_length = {A.alt_length}, oczekiwano 2"  # B(B)==A(B) odpada, C(W)!=A(B) → 1+1=2

print("compute_alt_path_lengths: OK!")

# Ścieżka: A(B) → C(W) → F(B)  [lewe dziecko preferowane przy remisie F/G]
path = t11.find_longest_alt_path()
path_colors = [v.color for v in path]

print(f"Najdłuższa naprzemienna ścieżka: {path_colors}")
print(f"Długość (krawędzie): {len(path) - 1}")

assert len(path) == 3, f"Oczekiwano 3 wierzchołków, dostano {len(path)}"
assert path[0] is A, "Ścieżka powinna zaczynać się od A(B)"
assert path[1] is C, "Drugi wierzchołek powinien być C(W)"
assert path[2] is F, "Trzeci wierzchołek powinien być F(B) (lewe dziecko preferowane)"

print("find_longest_alt_path: OK!")

# ── Test 8: pojedynczy liść ────────────────────────────────────
A = Leaf('B')
tree = RegBinTree(A)
tree.compute_alt_path_lengths()

assert A.alt_length == 0, f"A.alt_length = {A.alt_length}, oczekiwano 0"

path = tree.find_longest_alt_path()
assert len(path) == 1, f"Oczekiwano 1 wierzchołka, dostano {len(path)}"
assert path[0] is A, "Ścieżka powinna zawierać tylko liść A"

print("Test pojedynczego liścia: OK!")

# ── Test 9: pojedynczy liść ────────────────────────────────────
B = Leaf('B')
C = Leaf('B')
A = RegBinNode('B', B, C)
t2 = RegBinTree(A)

B = Leaf('B')
C = Leaf('B')
A = RegBinNode('B', B, C)
t2 = RegBinTree(A)
t2.compute_alt_path_lengths()

assert B.alt_length == 0, f"B.alt_length = {B.alt_length}, oczekiwano 0"
assert C.alt_length == 0, f"C.alt_length = {C.alt_length}, oczekiwano 0"
assert A.alt_length == 0, f"A.alt_length = {A.alt_length}, oczekiwano 0"

print("compute_alt_path_lengths: OK!")

path = t2.find_longest_alt_path()
assert len(path) == 0, f"Oczekiwano 1 wierzchołka, dostano {len(path)}"
assert path[0] is [], "Ścieżka powinna zawierać tylko korzeń A"

print("find_longest_alt_path: OK!")

print("Wszystkie testy przeszły pomyślnie!")