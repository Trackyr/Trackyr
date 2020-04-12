#!/usr/bin/env python3

import sys
import os
from importlib import util, machinery
import inspect
import uuid
import re

import yaml
# don't output yaml class tags
def noop(self, *args, **kw):
    pass

yaml.emitter.Emitter.process_tag = noop


from lib.core import settings
from lib.core import hooks
import lib.utils.reflection as refl
import lib.utils.logger as log

from lib.utils import creator

class NotifAgent:
    enabled = True

    def __init__(self,
                id = creator.create_simple_id(core.notif_agents),
                name = "New Notification Agent",
                module = None,
                module_properties = None
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

# looks for sub diretories inside "{directory}"
# and inspects its contents for a "agent.py" file and grabs the class inside that file
# RETURNS: a dictionary {module_name : module_instance}
def load_modules(directory, modules_dir):
    result = {}
    filename = "agent.py"

    subdirs = refl.get_directories(f"{directory}/{modules_dir}")
    modules = {}

    for module_name in subdirs:
        path = f"{directory}/{modules_dir}/{module_name}/{filename}"
        if not os.path.exists(path):
            continue

        namespace = refl.path_to_namespace(f"{modules_dir}/{module_name}/{filename}")
        finder = machinery.PathFinder()
        spec = util.find_spec(f"{namespace}")
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)

        module_class_name, module_class = refl.get_class(module, namespace)
        result[module_name] = module_class()

    return result

def load_agents(directory, agents_file, modules_dir):
    result = {}

    if not os.path.exists(agents_file):
        open(agents_file, "w+")

    with open(f"{directory}/{agents_file}", "r") as stream:
        config = yaml.safe_load(stream)

    if config is None:
        return {}

    for c in config:
        agent = NotifAgent(
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
    result = []
    for id in ids:
        result.append(notif_agents[id])

    return result

def get_names(notif_agents):
    names = []
    for a in notif_agents:
        names.append(a.name)

    return names

def get_enabled(agents):
    result = []
    for a in agents:
        if a.enabled:
            result.append(a)

    return result

# save agents depending on data mode
def save(*args, **kwargs):
    if (settings.get("data_mode") == settings.DATA_MODE_DB):
        save_db(args[0], **kwargs)
    elif (settings.get("data_mode") == settings.DATA_MODE_YAML):
        save_yaml(args[0], args[1], **kwargs)

def save_db(notif_agents):
    hooks.save_to_db(notif_agentss)

def save_yaml(notif_agents, file, preserve_comments=False):
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
        n["id"] = creator.create_simple_id(list(cur_notif_agents))
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
        print ("-----------------------------")

        set_props = {}
        for p in props:
            set_props[p] = n[f"prop_{p}"]

        if edit_notif_agent is None:
            save_notif_agent = NotifAgent(
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

        confirm = creator.prompt_options("Choose an option", ["save","edit","test","quit"])
        if confirm == "save":
            break
        elif confirm == "edit":
            continue
        elif confirm == "test":
            test_notif_agent(save_notif_agent, modules)
            continue
        elif confirm == "quit":
            return

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
    default_str = ""

    if default is None and len(modules) == 1:
        default = list(modules)[0]

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

def test_notif_agent(notif_agent, modules):
    module = modules[notif_agent.module]
    module.send(
        title = f"Testing '{notif_agent.name}'",
        message = "This is a test message",
        **notif_agent.module_properties
    )

def notif_agents_enabled_check(notif_agents):
    if len(get_enabled(notif_agents)) == 0:
        log.warning_print("There are no enabled agents... no notifications will be sent")
