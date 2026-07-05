class File:
    def __init__(self, name, is_folder, parent):
       self.name = name
       self.is_folder = is_folder
       self.parent = parent
       self.children = {}

    def move(self, new_parent):
        if new_parent.is_folder:
            del self.parent.children[self.name]
            self.parent = new_parent
            self.parent.children[self.name] = self

        # Maybe throw an exception if trying to move a file to a non-folder

# # /
# root = File("root", True, None, {})

# # /A
# root.children["A"] = File("A", False, root, {})
# # /A/A
# root.children["A"].children["A"] = File("A", True, root.children["A"], {})
# # /A/B
# root.children["A"].children["B"] = File("B", True, root.children["A"], {})
# # /A/C
# root.children["A"].children["C"] = File("C", True, root.children["A"], {})


# # /B
# root.children["B"] = File("B", True, root, {})
# # /B/A
# root.children["B"].children["A"] = File("A", True, root.children["B"], {})
# # /B/B
# root.children["B"].children["B"] = File("B", True, root.children["B"], {})
# # /B/C
# root.children["B"].children["C"] = File("C", False, root.children["B"], {})

# # /C
# root.children["C"] = File("C", True, root, {})
# # /C/A
# root.children["C"].children["A"] = File("A", True, root.children["C"], {})
# # /C/B
# root.children["C"].children["B"] = File("B", True, root.children["C"], {})
# # /C/C
# root.children["C"].children["C"] = File("C", True, root.children["C"], {})

# root.children["A"].move(root.children["B"].children["C"])