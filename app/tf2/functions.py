class_array = ["scout", "soldier", "pyro", "demoman", "heavy", "engineer", "sniper", "medic", "spy"]


def sort_classes(classes):
    return sorted([(_class.class_name, _class.class_name.capitalize())
                            for key, _class in classes.items()], key=lambda c: class_array.index(c[0]))