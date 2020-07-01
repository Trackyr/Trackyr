import os
import subprocess
import re
from importlib import util, machinery

import lib.core.settings as settings
import lib.utils.logger as log

import lib.core as core

import lib.utils.creator as creator
import lib.utils.reflection as refl

import lib.utils.collection_tools as ct

class BaseSourceModule():
    def get_properties():
        pass

    def set_properties(props):
        valid_props = get_properties()
        for p in props:
            if not p in valid_props:
                raise ValueError(f"Invalid module property '{p}'")


class ScrapeSummary():
    def __init__(self, **kwargs):
        keys = [
            "new_ads",
            "latest_ads",
            "total_new_ads"
        ]

        for key in kwargs:
            if not key in keys:
                raise ValueError(f"Invalid keyword for ScrapeSummary: '{key}'")

            val = kwargs[key]
            setattr(self, key, val)

class Source:
    def __init__(self,
                id = None,
                name = "New Source",
                module = None,
                module_properties = None
        ):

        from lib.core.state import State

        if id is None:
            id =  creator.create_simple_id(State.get_sources())

        self.id = id
        self.name = name
        self.module = module
        self.module_properties = module_properties

    def __repr__(self):
        return f"""id: {self.id}
name: {self.name}
module: {self.module}
module_properties: {self.module_properties}"""

# looks for sub directories inside "module_dir/"
# and inspects its contents for a "module.py" file and grabs the class inside that file
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


def save():
    from lib.core.state import State
    State.save_sources()

def list_sources(pause_after = 0):
    from lib.core.state import State
    sources = State.get_sources()

    i = 0
    for id in sources:
        print(sources[id])
        i = i + 1
        if pause_after > 0 and i == pause_after:
            i = 0
            if input(":") == "q":
                break

def source_creator(source):
    from lib.core.state import State

    s = source
    sources = State.get_sources()
    modules = State.get_source_modules()

    while True:
        name = s.name
        s.name = creator.prompt_string("Name", default=name)

        s.module = create_source_choose_module(s.module)

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

    sources[source.id] = source

    save()

def create_source_choose_module(default=None):
    from lib.core.state import State

    modules = State.get_source_modules()

    default_str = ""

    if default is None and len(modules) == 1:
        default = list(modules)[0]

    if default is not None:
        default_str = f" [{default}]"

    while True:
        modules_list = []
        i = 0
        for s in modules:
            modules_list.append(s)
            print(f"{i} - {s}")
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

def create_source():
    creator.print_title("Add Source")
    source_creator(Source())


def edit_source():
    from lib.core.state import State

    sources = State.get_sources()
    modules = State.get_source_modules()

    creator.print_title("Edit Source")
    source = creator.prompt_complex_dict("Choose a source", sources, "name", extra_options=["d"], extra_options_desc=["done"])
    if source == "d":
        return
    else:
        source_creator(source)

def delete_source():
    from lib.core.state import State

    sources_dict = State.get_sources()
    tasks_dict = State.get_tasks()

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
                        do_delete_source(sources_list[tnum].id)
                        changes_made = True

def get_tasks_using_source(source, tasks = None):
    if tasks is None:
        from lib.core.state import State
        tasks = State.get_tasks()

    used_by = []

    for id in tasks:
        if source.id in tasks[id].source_ids:
            used_by.append(tasks[id])

    return used_by

def do_delete_source(id):
    import lib.core.hooks as hooks
    from lib.core.state import State

    tasks = State.get_tasks()
    sources = State.get_sources()

    for task_id in tasks:
        task = tasks[task_id]
        if id in task.source_ids:
            task.source_ids.remove(id)

    hooks.delete_source_model(sources[id])

    del sources[id]

def test_source(source):
    from lib.core.state import State
    modules = State.get_source_modules()

    include = []
    exclude = []

    if creator.yes_no("Would you like to add inlcudes/excludes", "n") == "y":
        include = creator.prompt_string("Include", allow_empty=True)
        exclude = creator.prompt_string("Exclude", allow_empty=True)

    module = modules[source.module]

    return scrape(
            source,
            None,
            include=include,
            exclude=exclude,
            notify=False,
            save_ads=False
        )

def test_webui_source(source):
    from lib.core.state import State
    modules = State.get_source_modules()

    module = modules[source.module]

    return scrape(
            source,
            None,
            include="",
            exclude="",
            colour_flag="",
            notify=False,
            save_ads=False
        )

def scrape(
        source,
        notif_agents_list,
        include=[],
        exclude=[],
        colour_flag="",
        notify=True,
        force_tasks=False,
        force_agents=False,
        recent_ads=0,
        save_ads=True,
        ignore_old_ads=False
    ):

    from lib.core.state import State
    import lib.core.notif_agent as notif_agent

    ads = State.get_ads()
    source_modules = State.get_source_modules()
    notif_agent_modules = State.get_notif_agent_modules()

    log.info_print(f"Source: {source.name}")
    log.info_print(f"Module: {source.module}")
    log.info_print(f"Module Properties: {source.module_properties}")

    if len(include):
        print(f"Including: {include}")

    if len(exclude):
        print(f"Excluding: {exclude}")

    module = source_modules[source.module]

    old_ads = []
    if ignore_old_ads == False:
        if source.module in ads:
            old_ads = ads[source.module]
            log.debug(f"Total old ads: {len(old_ads)}")

        else:
            log.debug(f"No old ads found for module: {source.module}")

    else:
        log.info_print("Ignoring old ads...")

    new_ads, ad_title = module.scrape_for_ads(old_ads, exclude=exclude, **source.module_properties)

    info_string = f"Found {len(new_ads)} new ads" \
        if len(new_ads) != 1 else "Found 1 new ad"

    log.info_print(info_string)

    num_ads = len(new_ads)

    if notify and num_ads:
        ads_to_send = new_ads

        if recent_ads > 0:
            # only notify the most recent notify_recent new_ads
            ads_to_send = ct.get_most_recent_items(recent_ads, new_ads)
            log.debug(f"Recent ads set to: {recent_ads} got: {len(ads_to_send)}")
            log.info_print(f"Total ads to notify about: {len(ads_to_send)}")

        if len(notif_agents_list) == 0:
            log.warning_print("No notification agents set... nothing to notify")

        else:
            if len(notif_agents_list) > 1:
                log.info_print(f"Notifying agents: {notif_agent.get_names(notif_agents_list)}")

            for agent in notif_agents_list:
                if agent.enabled or force_agents == True:
                    if agent.enabled == False and force_agents == True:
                        log.info_print("Notification agent was disabled but forcing...")

                    notif_agent_modules[agent.module].send_ads(ads_to_send, ad_title, colour_flag, **agent.module_properties)

                else:
                    log.info_print(f"Skipping... Notification agent disabled: {agent.name}")

    elif not notify and num_ads:
        log.info_print("Skipping notification")

    if save_ads:
        ads[source.module] = module.old_ad_ids
        log.debug(f"Total all-time processed ads: {len(module.old_ad_ids)}")
    else:
        log.info_print(f"Saving ads disabled. Skipping...")

    print()

    return ScrapeSummary(
        new_ads = new_ads,
        latest_ads = list(new_ads)[-3:],
        total_new_ads = len(new_ads)
    )