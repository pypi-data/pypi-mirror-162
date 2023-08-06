import inspect

"""
Return constructor arguments and their types as a dictionary.
self is not included.
"""


def get_constructor_arguments(class_name):
    parameters = inspect.signature(class_name.__init__).parameters
    arguments = [p for p in parameters if p != "self"]
    return {a: parameters[a].annotation for a in arguments}
