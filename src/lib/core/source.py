import os
import sys
import collections
import subprocess
import re
import uuid

import yaml
# don't output yaml class tags
def noop(self, *args, **kw):
    pass

yaml.emitter.Emitter.process_tag = noop

from importlib import util, machinery
import inspect

import lib.core.settings as settings
import lib.core.hooks as hooks
import lib.core as core

import lib.utils.creator as creator
import lib.utils.reflection as refl

class BaseSourceModule():
    def get_properties():
        pass

    def set_properties(props):
        valid_props = get_properties()
        for p in props:
            if not p in valid_props:
                raise ValueError(f"Invalid module property '{p}'")

class Source:
    def __init__(self,
                id = None,
                name = "New Source",
                module = None,
                module_properties = None
        ):

        if id is None:
            id =  creator.create_simple_id(core.get_sources())

        self.id = id
        self.name = name
        self.module = module
        self.module_properties = module_properties

    def __repr__(self):
        return f"""
id: {self.id}
name:{self.name}
module: {self.module}
module_properties: {self.module_properties}
"""

def load_sources(file):
    if not os.path.exists(file):
        open(file, "w+")

    with open(file, "r") as stream:
        sources_yaml = yaml.safe_load(stream)

    sources = {}
    if sources_yaml is not None:
        for s in sources_yaml:
            source = Source.load(s)
            sources[source.id] = source

    return sources

# looks for sub directories inside "module_dir/"
# and inspects its contents for a "scraper.py" file and grabs the class inside that file
# PARAMS: directory - the working directory
#         module_dir - the sub directory in directory where the modules can be found
# RETURNS: a dictionary {module_name : module_instance} 
def load_modules(directory, module_dir):
    result = {}
    filename = "scraper.py"

    subdirs = refl.get_directories(f"{directory}/{module_dir}")
    for module_name in subdirs:
        path = f"{directory}/{module_dir}/{module_name}/{filename}"
        if not os.path.exists(path):
            continue

        namespace = refl.path_to_namespace(f"{module_dir}/{module_name}/{filename}")
        finder = machinery.PathFinder()
        spec = util.find_spec(f"{namespace}")
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)

        module_class_name, module_class = refl.get_class(module, namespace)
        result[module_name] = module_class()

    return result


def save(*args, **kwargs):
    if (settings.get("data_mode") == settings.DATA_MODE_DB):
        save_db(args[0], **kwargs)
    elif (settings.get("data_mode") == settings.DATA_MODE_YAML):
        save_yaml(args[0], args[1], **kwargs)

def save_db(sources):
    hooks.save_to_db(sources)

def save_yaml(sources, file, preserve_comments=True):
    if isinstance(sources, dict):
        old_sources = sources
        sources = []
        for s in old_sources:
            sources.append(old_sources[s])

    elif isinstance(sources, list) == False:
        raise ValueError(f"sources must by list or dict, not: {type(sources)}")


    if preserve_comments:
        # preserve comments in file
        with open(file, "r") as stream:
            filestream = stream.read()

        match = re.findall("([#][^\n]*[\n]|[#][\n])", filestream)

    with open(file, "w") as stream:
        if preserve_comments and match:
            for m in match:
                stream.write(m)

        yaml.dump(sources, stream, default_flow_style=False, sort_keys=False)

def list_sources_in_file(file):
    list_sources(load_sources(file))

def list_sources(sources):
    for t in sources:
        print(sources[t])

def append_source_to_file(source, file):
    sources = load_sources(file)
    sources.append(source)
    save_sources(sources, file)

def delete_source_from_file(index, file):
    sources = load_sources(file)
    if index < 0 or index >= len(sources):
        logging.error(f"sourcelib.delete_source_from_file: Invalid index: {index}")
        return

    del(sources[index])
    save_sources(sources, file)

def source_creator(source, cur_sources, modules, file):
    s = source

    while True:
        name = s.name
        s.name = creator.prompt_string("Name", default=name)

        s.module = create_source_choose_module(modules, s.module)

        module = modules[s.module]
        props = module.get_properties()
        print("Module Properties")
        for p in props:
            default = None 
            if s.module_properties is not None:
                default = s.module_properties.get(p, None)

            if s.module_properties is None:
                s.module_properties = {}

            s.module_properties[p] = creator.prompt_string(f"{p}", default=default)

        print()
        print(f"Id: {s.id}")
        print(f"Name: {s.name}")
        print(f"Module: {s.module}")
        print ("-----------------------------")
        for p in s.module_properties:
            print(f"{p}: {s.module_properties[p]}")
        print ("-----------------------------")

        while True:
            confirm = creator.prompt_options("Choose an option", ["save","edit","test","quit"])
            if confirm == "test":
                test_source(source, modules)
                continue

            else:
                break

        if confirm == "save":
            break
        elif confirm == "edit":
            continue
        elif confirm == "quit":
            return

    cur_sources[source.id] = source

    save(cur_sources, file)

def create_source_choose_module(scrapers, default=None):
    default_str = ""

    if default is None and len(scrapers) == 1:
        default = list(scrapers)[0]

    if default is not None:
        default_str = f" [{default}]"

    while True:
        scrapers_list = []
        i = 0
        for s in scrapers:
            scrapers_list.append(s)
            print(f"{i} - {s}")
            i = i + 1

        choices = "0"
        if len(scrapers_list) > 1:
            choices = f"0-{len(scrapers_list) - 1}"

        scraper_index_str = input(f"Module [Choose from {choices}]:{default_str} ")

        if default is not None and scraper_index_str == "":
            return default

        if len(scrapers_list) == 0 and scraper_index_str == "":
            scraper_index = 0
            break

        if re.match("[0-9]+$", scraper_index_str):
            scraper_index = int(scraper_index_str)
            if scraper_index >= 0 and scraper_index < len(scrapers_list):
                return scrapers_list[scraper_index]

def create_source(cur_sources, scrapers, file):
    creator.print_title("Add Source")
    source_creator(Source(), cur_sources, scrapers, file)


def edit_source(cur_sources, scrapers, file):
    creator.print_title("Edit Source")
    source = creator.prompt_complex_dict("Choose a source", cur_sources, "name", extra_options=["d"], extra_options_desc=["done"])
    if source == "d":
        return
    else:
        source_creator(source, cur_sources, scrapers, file)

def delete_source(sources_dict, sources_file, tasks_dict, tasks_file):
    creator.print_title("Delete Source")
    changes_made = False

    while True:
        sources_list = []
        for s in sources_dict:
            sources_list.append(sources_dict[s])

        for i in range(len(sources_list)):
            print(f"{i} - {sources_list[i].name}")

        print ("s - save and quit")
        print ("q - quit without saving")

        tnum_str = creator.prompt_string("Delete source")
        if tnum_str == "s":
            save(sources_dict, sources_file)
            core.task.save(tasks_dict, tasks_file)
            return

        elif tnum_str == "q":
            if changes_made and creator.yes_no("Quit without saving","n") == "y":
                return

            elif not changes_made:
                return

        if re.match("[0-9]+$", tnum_str):
            tnum = int(tnum_str)
            if tnum >= 0 and tnum < len(sources_list):
                if creator.yes_no(f"Delete {sources_list[tnum].name}", "y") == "y":
                    used_by = get_tasks_using_source(sources_dict[sources_list[tnum].id], tasks_dict)
                    if len(used_by) > 0:
                        task_names = []
                        for u in used_by:
                            task_names.append(f"'{u.name}'")

                        print(f"Cannot delete source. It is being used by task(s): {','.join(task_names)}")
                        print("Delete those tasks or remove this notification agent from them first before deleting.")

                    else:
                        do_delete_source(sources_list[tnum].id, sources_dict, tasks_dict)
                        changes_made = True

def get_tasks_using_source(source, tasks):
    used_by = []

    for id in tasks:
        if source.id in tasks[id].source_ids:
            used_by.append(tasks[id])

    return used_by

def do_delete_source(*args, **kwargs):
    if settings.get("data_mode") == settings.DATA_MODE_DB:
        do_delete_source_db(*args, **kwargs)

    elif settings.get("data_mode") == settings.DATA_MODE_YAML:
        do_delete_source_yaml(*args, **kwargs)

def do_delete_source_db(id, sources, tasks):
    for task_id in tasks:
        task = tasks[task_id]
        if id in task.source_ids:
            task.source_ids.remove(id)

    hooks.delete_source_model(sources[id])

    del sources[id]

def do_delete_source_yaml(id, sources, tasks):
    for task_id in tasks:
        task = tasks[task_id]
        if id in task.source_ids:
            task.source_ids.remove(id)

    del sources[id]

def test_source(source, modules):
    include = []
    exclude = []

    if creator.yes_no("Would you like to add inlcudes/excludes", "n") == "y":
        include = creator.prompt_string("Include", allow_empty=True)
        exclude = creator.prompt_string("Exclude", allow_empty=True)

    module = modules[source.module]

    core.scrape_source(
            source,
            [],
            include=include,
            exclude=exclude,
            notify=False,
            save_ads=False
        )

