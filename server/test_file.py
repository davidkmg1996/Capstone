from file import File

import pytest
from collections import deque

@pytest.fixture
def root():
    # /
    root = File("root", True, None)

    # /A
    root.children["A"] = File("A", True, root)
    # /A/A
    root.children["A"].children["A"] = File("A", True, root.children["A"])
    # /A/B
    root.children["A"].children["B"] = File("B", False, root.children["A"])
    # /A/C
    root.children["A"].children["C"] = File("C", True, root.children["A"])


    # /B
    root.children["B"] = File("B", True, root)
    # /B/A
    root.children["B"].children["A"] = File("A", True, root.children["B"])
    # /B/B
    root.children["B"].children["B"] = File("B", True, root.children["B"])
    # /B/C
    root.children["B"].children["C"] = File("C", False, root.children["B"])

    # /C
    root.children["C"] = File("C", True, root)
    # /C/A
    root.children["C"].children["A"] = File("A", False, root.children["C"])
    # /C/B
    root.children["C"].children["B"] = File("B", True, root.children["C"])
    # /C/C
    root.children["C"].children["C"] = File("C", True, root.children["C"])

    root.children["D"] = File("D", True, root)

    root.children["E"] = File("E", False, root)

    root.children["F"] = File("F", False, root)

    return root


# Looks for a file and then returns that file
def traverse(file, path):
    if len(path):
        return traverse(file.children[path.popleft()], path)
    return file

@pytest.fixture
def move_file(root):
    def _move_file(to_move, new_parent):
        file = traverse(root, to_move)
        new_folder = traverse(root, new_parent)
        current_parent = file.parent
        file.move(new_folder)
        return (file, new_folder, current_parent)
    
    return _move_file

@pytest.mark.parametrize("to_move, new_parent", [
    (("A", "A"), ("B", "B")), # Folder at depth > 1 moving to folder
    (("C", "A"), ("B")), # Non-folder at depth > 1moving to folder
    (("B"), ("D")), # Folder at depth 1 moving to folder 
    (("E"), ("D")) # Non-older at depth 1 moving to folder 
    ])
def test_file_move_to_folder(to_move, new_parent, move_file):
    file, new_folder, current_parent = move_file(deque(to_move), deque(new_parent))
    assert file.parent != current_parent
    assert file.parent == new_folder


@pytest.mark.parametrize("to_move, new_parent", [
    (("A", "A"), ("B", "C")), # Folder at depth > 1 moving to non-folder
    (("C", "A"), ("B", "C")), # Non-folder at depth > 1 moving to non-folder
    (("B"), ("E")), # Folder at depth 1 moving to non-folder
    (("E", "F")) # Non-folder at depth 1 moving to non-folder
])
def test_file_move_to_nonfolder(to_move, new_parent, move_file):
    file, new_folder, current_parent = move_file(deque(to_move), deque(new_parent))
    assert file.parent == current_parent
    assert file.parent != new_folder


@pytest.mark.parametrize("path", [
    ("A", "B"),
    ("C")
    ])
def test_traverse(root, path):
    file = traverse(root, deque(path))
    parent = traverse(root, deque(path[0:len(path) - 1]))
    assert file.parent == parent