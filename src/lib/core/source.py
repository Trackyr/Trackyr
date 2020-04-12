#!usr/bin/env python3
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

from . import settings, hooks
from lib import core
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
                id = creator.create_simple_id(core.sources),
                name = "New Source",
                module = "",
                module_properties = {}
        ):

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
    i = 0
    for t in sources:
        print (f"[{i}]")
        print_source(t)
        i = i+1

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

def print_source(source):
        print(f"""
Name: {source.name}
Source: {source.source}
Frequency: {source.frequency} {source.frequency_unit}
Url: {source.url}
Include: {source.include}
Exclude: {source.exclude}
""")

def source_creator(cur_sources, modules, file, edit_source=None):
    s = {}
    if edit_source is not None:
        e = edit_source
        s["id"] = e.id
        s["name"] = e.name
        s["module"] = e.module
        for p in e.module_properties:
            s[f"prop_{p}"] = e.module_properties[p]

    while True:
        s["id"] = creator.create_simple_id(list(cur_sources))
        s["name"] = creator.prompt_string("Name", default=s.get("name", None))
        s["module"] = create_source_choose_module(modules, s.get("module", None))
        module = modules[s["module"]]
        props = module.get_properties()
        print("Module Properties")
        for p in props:
            s[f"prop_{p}"] = creator.prompt_string(f"{p}", default=s.get(f"prop_{p}", None))

        print()
        print(f"Id: {s['id']}")
        print(f"Name: {s['name']}")
        print(f"Module: {s['module']}")
        print ("-----------------------------")
        for p in props:
            val = s[f"prop_{p}"]
            print(f"{p}: {val}")
        print ("-----------------------------")

        set_props = {}
        for p in props:
            set_props[p] = s[f"prop_{p}"]

        if edit_source is None:
            source = Source(
                id=s["id"],
                name=s["name"],
                module=s["module"],
                module_properties=set_props
            )

        else:
            edit_source.id = s["id"]
            edit_source.name = s["name"]
            edit_source.module = s["module"]
            edit_source.module_properties = set_props
            source = edit_source

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

    cur_sources[s["id"]] = source
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

def create_source(cur_sources, scrapers, file, edit_source=None):
    creator.print_title("Add Source")
    source_creator(cur_sources, scrapers, file, edit_source=edit_source)


def edit_source(cur_sources, scrapers, file):
    creator.print_title("Edit Source")
    source = creator.prompt_complex_dict("Choose a source", cur_sources, "name", extra_options=["d"], extra_options_desc=["done"])
    if source == "d":
        return
    else:
        create_source(cur_sources, scrapers, file, edit_source=source)

def delete_source(sources_dict, sources_file, tasks_list, tasks_file):
    creator.print_title("Delete Source")
    save = False
    changes_made = False

    while True:
        sources_list = []
        for s in sources_dict:
            sources_list.append(sources_dict[s])

        for i in range(len(sources_list)):
            print(f"{i} - {sources_list[i].name} [id: {sources_list[i].id}]")

        print ("s - save and quit")
        print ("q - quit without saving")

        tnum_str = creator.prompt_string("Delete source")
        if tnum_str == "s":
            save = True
            break
        elif tnum_str == "q":
            if changes_made and creator.yes_no("Quit without saving","n") == "y":
                return
            elif not changes_made:
                return

        if re.match("[0-9]+$", tnum_str):
            tnum = int(tnum_str)
            if tnum >= 0 and tnum < len(sources_list):
                if creator.yes_no(f"Delete {sources_list[tnum].name}", "y") == "y":
                    do_delete_source(sources_list[tnum].id, sources_dict, tasks_list)
                    changes_made = True

    if save:
        save(sources_list, sources_file)
        tasklib.save(tasks_list, tasks_file)

def do_delete_source(id, sources_dict, tasks_list):
    for t in tasks_list:
        if id in t.source_ids:
            t.source_ids.remove(id)

    del sources_dict[id]

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

