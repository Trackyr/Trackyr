import os
import re
from importlib import util, machinery

import lib.core.settings as settings
import lib.core as core

from lib.core.config import Config

import lib.utils.reflection as refl
import lib.utils.logger as log
import lib.utils.creator as creator

class NotifAgent:
    enabled = True

    def __init__(self,
                id = None,
                name = "New Notification Agent",
                module = None,
                module_properties = None
        ):

        if id is None:
            from lib.core.state import State
            id = creator.create_simple_id(State.get_tasks()),

        self.id = id
        self.name = name
        self.module = module
        self.module_properties = module_properties

    def __repr__(self):
        return f"""id: {self.id}
name: {self.name}
module: {self.module}
module_properties: {self.module_properties}"""

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

def get_notif_agents_by_ids(ids):
    from lib.core.state import State

    notif_agents = State.get_notif_agents()

    result = []
    for id in ids:
        result.append(notif_agents[id])

    return result

def get_names(notif_agents):
    names = []
    for a in notif_agents:
        names.append(a.name)

    return names

def get_enabled(notif_agents):
    result = []
    for n in notif_agents:
        if n.enabled:
            result.append(n)

    return result

def list_notif_agents(pause_after = 0):
    from lib.core.state import State

    notif_agents = State.get_notif_agents()

    i = 0
    for id in notif_agents:
        print(notif_agents[id])
        i = i + 1
        if pause_after > 0 and i == pause_after:
            i = 0
            if input(":") == "q":
                break

# save agents depending on data mode
def save(notif_agents):
    from lib.core.state import State

    State.save_notif_agents()

def notif_agent_creator(notif_agent):
    from lib.core.state import State

    n = notif_agent

    cur_notif_agents = State.get_notif_agents()
    modules = State.get_notif_agent_modules()

    while True:
        n.name = creator.prompt_string("Name", default=n.name)
        n.module = create_notif_agent_choose_module(n.module)

        module = modules[n.module]
        props = module.get_properties()

        print("Module Properties")

        for p in props:
            default = None
            if n.module_properties is not None:
                default = n.module_properties.get(p, None)
            else:
                n.module_properties = {}

            while True:
                n.module_properties[p] = creator.prompt_string(f"{p}", default=default)
                is_valid, error_msg = module.is_property_valid(
                                            p,
                                            n.module_properties[p])

                if is_valid:
                    break
                else:
                    print (error_msg)
                    default = None
        print()
        print(f"Id: {n.id}")
        print(f"Name: {n.name}")
        print(f"Module: {n.module}")
        print ("-----------------------------")
        for p in props:
            print(f"{p}: {n.module_properties[p]}")
        print ("-----------------------------")

        while True:
            confirm = creator.prompt_options("Choose an option", ["save","edit","test","quit"])
            if confirm == "test":
                test_notif_agent(notif_agent)
                continue
            else:
                break

        if confirm == "save":
            break
        elif confirm == "edit":
            continue
        elif confirm == "quit":
            return

    cur_notif_agents[n.id] = notif_agent

    State.save_notif_agents()

def create_notif_agent():
    creator.print_title("Add Notification Agent")
    notif_agent_creator(NotifAgent())

def edit_notif_agent():
    creator.print_title("Edit Notification Agent")
    notif_agent = creator.prompt_complex_dict("Choose a notification agent", State.get_notif_agents(), "name", extra_options=["d"], extra_options_desc=["done"])
    if notif_agent == "d":
        return
    else:
        notif_agent_creator(notif_agent)

def delete_notif_agent():
    notif_agents_dict = State.get_notif_agents()

    creator.print_title("Delete Notification Agent")
    changes_made = False

    while True:
        notif_agents_list = []
        for n in notif_agents_dict:
            notif_agents_list.append(notif_agents_dict[n])

        for i in range(len(notif_agents_list)):
            print(f"{i} - {notif_agents_list[i].name}")

        print ("s - save and quit")
        print ("q - quit without saving")

        tnum_str = creator.prompt_string("Delete notif_agent")
        if tnum_str == "s":
            State.save_notif_agents()
            State.save_tasks()
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
                    used_by = get_tasks_using_notif_agent(notif_agents_dict[notif_agents_list[tnum].id])
                    if used_by is not None and len(used_by) > 0:
                        task_names = []
                        for u in used_by:
                            task_names.append(f"'{u.name}'")

                        print(f"Cannot delete notification agent '{notif_agents_list[tnum].name}'. It is being used by: {','.join(task_names)}")
                        print("Delete tasks using this notification agent or remove this notification agent from those tasks first before deleting.")

                    else:
                        do_delete_notif_agent(notif_agents_list[tnum].id)
                        changes_made = True

def get_tasks_using_notif_agent(notif_agent):
    result = []
    tasks = State.get_tasks()

    for id in tasks:
        if notif_agent.id in tasks[id].notif_agent_ids:
            result.append(tasks[id])

    return result

def do_delete_notif_agent(id):
    from lib.core.state import State
    import lib.core.hooks as hooks

    tasks_dict = State.get_tasks()
    notif_agents_dict = State.get_notif_agents()

    for task_id in tasks_dict:
        t = tasks_dict[task_id]

        if id in t.notif_agent_ids:
            t.notif_agent_ids.remove(id)

    hooks.delete_notif_agent_model(notif_agents_dict[id])
    del notif_agents_dict[id]

def do_delete_notif_agent_yaml(id):
    from lib.core.state import State

    tasks_dict = State.get_tasks()
    notif_agents_dict = State.get_notif_agents()

    for task_id in tasks_dict:
        t = tasks_dict[task_id]

        if id in t.notif_agent_ids:
            t.notif_agent_ids.remove(id)

    del notif_agents_dict[id]

def create_notif_agent_choose_module(default=None):
    from lib.core.state import State

    modules = State.get_notif_agent_modules()

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

def test_notif_agent(notif_agent):
    from lib.core.state import State

    notif_agents = State.get_notif_agents()
    modules = State.get_notif_agent_modules()

    log.debug_print(f"Testing notification agent: '{notif_agent.name}'")
    module = modules[notif_agent.module]
    module.send(
        title = f"Testing '{notif_agent.name}'",
        message = "This is a test message",
        **notif_agent.module_properties
    )

    print("Done!")

def notif_agents_enabled_check(notif_agents):
    if len(get_enabled(notif_agents)) == 0:
        log.warning_print("There are no enabled agents... no notifications will be sent")