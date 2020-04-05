#!/usr/bin/env python3

import sys
import os
import importlib
import inspect

import notification_agent_lib as agentlib

# gets a class from a dynamically loaded module
# namespace ensures it gets the class from the module and not an imported module
# RETURNS: class_name_string, class
def get_class(module, namespace):
    classes = inspect.getmembers(module, inspect.isclass)
    module_class = None

    for c in classes:
        if namespace in str(c[1]):
            return c[0], c[1]

# converts a path to a namespace with dot notation
# ie: path/to/file.py -> path.to.file
# RETURNS: namespace_string
def path_to_namespace(path):
    return path.replace("/", ".").replace(".py", "")

# gets a module from a given path
# PARAMS: path - the relative path to the module (path/to/module.py)
# RETURNS: module
def get_module(path):
    namespace = path_to_namespace(path)
    return importlib.import_module(namespace)

# gets a list of directories in a subdirectory
# PARAMS: subdir - the subdirectory to get the list of directories in
# RETURNS: dir_list
def get_directories(subdir):
    dirs = os.listdir(subdir)
    result = []

    for dir in dirs:
        if dir[:1] == "." or dir[:] == "__":
            continue

        result.append(dir)

    return result
