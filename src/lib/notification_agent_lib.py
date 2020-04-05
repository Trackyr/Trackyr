#!/usr/bin/env python3

import yaml
import sys
import os
import importlib
#import json
import inspect
import reflection_lib as refl
import logger_lib as log
import uuid
import re

import creator_utils_lib as creator

class notif_agent:
    enabled = True

    def __init__(self, id, name, module, module_properties):
        self.id = id
        self.name = name
        self.module = module
        self.module_properties = module_properties

# looks for sub diretories inside "{directory}"
# and inspects its contents for a "agent.py" file and grabs the class inside that file
# uses config files inside of  {directory}/{agent_dir}/config.yaml
# RETURNS: a dictionary {agent_name : agent_instance}
def get_modules(directory, agent_dir):
    result = {}
    filename = "agent.py"
    config_file = "config.yaml"

    subdirs = refl.get_directories(f"{directory}/{agent_dir}")
    modules = {}

    for subdir in subdirs:
        scraper_name = subdir
        path = f"{directory}/{agent_dir}/{subdir}/{filename}"
        if not os.path.exists(path):
            continue

        namespace = refl.path_to_namespace(f"{agent_dir}/{subdir}/{filename}")
        finder = importlib.machinery.PathFinder()
        spec = importlib.util.find_spec(f"{namespace}")
        #spec = importlib.machinery.find_spec(f"{path}")
        module = importlib.util.module_from_spec(spec)
#        sys.modules[module_name] = module
        spec.loader.exec_module(module)

#        namespace = refl.path_to_namespace(path)
#        module = refl.get_module(namespace)
        module_class_name, module_class = refl.get_class(module, namespace)
        result[subdir] = module_class()

    return result

def get_agents(directory, agents_file, modules_dir):
    modules = get_modules(directory, modules_dir)
    result = {}

    if not os.path.exists(agents_file):
        open(agents_file, "w+")

    with open(f"{directory}/{agents_file}", "r") as stream:
        config = yaml.safe_load(stream)

    if config is None:
        return {}

    for c in config:
        agent = notif_agent(
                    c.get("id", str(uuid.uuid4())),
                    c.get("name"),
                    c.get("module"),
                    c.get("module_properties")
                )

        agent.enabled = c.get("enabled", True)

        log.debug(f"Adding notification agent: {agent.id} {agent.name}")
        result[agent.id] = agent

    return result

def get_notif_agents_by_ids(notif_agents, ids):
    print (ids)
    result = []
    for id in ids:
        print (f"{id}: enabled: {notif_agents[id].enabled}")
        result.append(notif_agents[id])

    return result


def get_names(notif_agents):
    names = []
    for a in notif_agents:
        names.append(a.name)

    return names

def get_enabled(agents):
    print (agents)
    result = []
    for a in agents:
        if a.enabled:
            result.append(a)

    return result

# <-- don't output yaml class tags
def noop(self, *args, **kw):
    pass

yaml.emitter.Emitter.process_tag = noop

def save(notif_agents, file, preserve_comments=False):
    if isinstance(notif_agents, dict):
        old_notif_agents = notif_agents
        notif_agents = []
        for s in old_notif_agents:
            notif_agents.append(old_notif_agents[s])

    elif isinstance(notif_agents, list) == False:
        raise ValueError(f"notif_agents must by list or dict, not: {type(notif_agents)}")


    if preserve_comments:
        # preserve comments in file
        with open(file, "r") as stream:
            filestream = stream.read()

        match = re.findall("([#][^\n]*[\n]|[#][\n])", filestream)

    with open(file, "w") as stream:
        if preserve_comments and match:
            for m in match:
                stream.write(m)

        yaml.dump(notif_agents, stream, default_flow_style=False, sort_keys=False)

def notif_agent_creator(cur_notif_agents, modules, file, edit_notif_agent=None):
    n = {}
    if edit_notif_agent is not None:
        e = edit_notif_agent
        old_name = e.name
        n["id"] = e.id
        n["name"] = e.name
        n["module"] = e.module
        for p in e.module_properties:
            n[f"prop_{p}"] = e.module_properties[p]


    while True:
        n["id"] = creator.prompt_id(creator.get_id_list(cur_notif_agents), default = n.get("id", None))
        n["name"] = creator.prompt_string("Name", default=n.get("name", None))

        n["module"] = create_notif_agent_choose_module(modules, default=n.get("module", None))
        module = modules[n["module"]]
        props = module.get_properties()

        print("Module Properties")

        for p in props:
            default = n.get(f"prop_{p}", None)
            while True:
                n[f"prop_{p}"] = creator.prompt_string(f"{p}", default=default)
                is_valid, error_msg = module.is_property_valid(p, n[f"prop_{p}"])
                if is_valid:
                    break
                else:
                    print (error_msg)
                    default = None
        print()
        print(f"Id: {n['id']}")
        print(f"Name: {n['name']}")
        print(f"Module: {n['module']}")
        print ("-----------------------------")
        for p in props:
            val = n[f"prop_{p}"]
            print(f"{p}: {val}")
#        print("}")
        print ("-----------------------------")

        """
        if edit_notif_agent is None:
            confirm_msg = "Create this notif_agent?"
        else:
            confirm_msg = f"Apply changes to notification agent '{old_name}'"
        """

        confirm = creator.prompt_options("Choose an option", ["save","edit","quit"])
        if confirm == "save":
            break
        elif confirm == "edit":
            continue
        elif confirm == "quit":
            return

    set_props = {}
    for p in props:
        set_props[p] = n[f"prop_{p}"]

    if edit_notif_agent is None:
        save_notif_agent = notif_agent(
            id=n["id"],
            name=n["name"],
            module=n["module"],
            module_properties=set_props
        )
    else:
        edit_notif_agent.id = n["id"]
        edit_notif_agent.name = n["name"]
        edit_notif_agent.module = n["module"]
        edit_notif_agent.module_properties=set_props
        save_notif_agent = edit_notif_agent

    cur_notif_agents[n["id"]] = save_notif_agent
    save(cur_notif_agents, file)

def create_notif_agent(cur_notif_agents, modules, file, edit_notif_agent=None):
    creator.print_title("Add Notification Agent")
    notif_agent_creator(cur_notif_agents, modules, file, edit_notif_agent=edit_notif_agent)

def edit_notif_agent(cur_notif_agents, modules, file):
    creator.print_title("Edit Notification Agent")
    notif_agent = creator.prompt_complex_dict("Choose a notification agent", cur_notif_agents, "name", extra_options=["d"], extra_options_desc=["done"])
    if notif_agent == "d":
        return
    else:
        create_notif_agent(cur_notif_agents, modules, file, edit_notif_agent=notif_agent)

def delete_notif_agent(notif_agents_dict, notif_agents_file, tasks_list, tasks_file):
    creator.print_title("Delete Notification Agent")
    save = False
    changes_made = False

    while True:
        notif_agents_list = []
        for n in notif_agents_dict:
            notif_agents_list.append(notif_agents_dict[n])

        for i in range(len(notif_agents_list)):
            print(f"{i} - {notif_agents_list[i].name} [id: {notif_agents_list[i].id}]")

        print ("s - save and quit")
        print ("q - quit without saving")

        tnum_str = creator.prompt_string("Delete notif_agent")
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
            if tnum >= 0 and tnum < len(notif_agents_list):
                if creator.yes_no(f"Delete {notif_agents_list[tnum].name}", "y") == "y":
                    do_delete_notif_agent(notif_agents_list[tnum].id, notif_agents_dict, tasks_list)
                    changes_made = True

    if save:
        save(notif_agents_list, notif_agents_file)
        tasklib.save(tasks_list, tasks_file)

def do_delete_notif_agent(id, notif_agents_dict, tasks_list):
    for t in tasks_list:
        if id in t.notif_agent_ids:
            t.notif_agent_ids.remove(id)

    del notif_agents_dict[id]

def create_notif_agent_choose_module(modules, default=None):
    print (modules)
    default_str = ""
    if default is not None:
        default_str = f" [{default}]"

    while True:
        modules_list = []
        i = 0
        for m in modules:
            modules_list.append(m)
            print(f"{i} - {m}")
            i = i + 1

        choices = "0"
        if len(modules_list) > 1:
            choices = f"0-{len(modules_list) - 1}"

        module_index_str = input(f"Module [Choose from {choices}]:{default_str} ")

        if default is not None and module_index_str == "":
            return default

        if len(modules_list) == 0 and module_index_str == "":
            module_index = 0
            break

        if re.match("[0-9]+$", module_index_str):
            module_index = int(module_index_str)
            if module_index >= 0 and module_index < len(modules_list):
                return modules_list[module_index]


