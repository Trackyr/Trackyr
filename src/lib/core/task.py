import os
import yaml
import collections
import subprocess
import re
import uuid

import lib.utils.creator as creator
from lib.utils import cron

import lib.utils.logger as log

from lib.core import hooks
from lib.core import settings

class Task:
    yaml_tag = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.name = kwargs.get("name", "New Task")
        self.enabled = kwargs.get("enabled", True)
        self.frequency = kwargs.get("frequency", 15)
        self.frequency_unit = kwargs.get("frequency_unit", "minutes")
        self.source_ids = kwargs.get("source_ids", [])
        self.notif_agent_ids = kwargs.get("notif_agent_ids", [])
        self.include = kwargs.get("include", [])
        self.exclude = kwargs.get("exclude", [])

    def __repr__(self):
        return f"""name:{self.name}
frequency: {self.frequency} {self.frequency_unit}
source_ids: {self.source_ids}
notif_agent_ids: {self.notif_agent_ids}
include: {self.include}
exclude: {self.exclude}
"""

    # freq: int
    # unit: "minutes" | "hours"
    def set_frequency(freq, unit):
        self.frequency = freq
        self.frequency_unit = unit

    # convenience method to see if this instance matches
    # the soecified frequency
    # freq: int
    # unit: "minutes" | "hours"
    def matches_freq(self, time, unit):
        return time == self.frequency and unit[:1] == self.frequency_unit[:1]

# load tasks from yaml file
def load_tasks(file):
    if not os.path.exists(file):
        open(file, "w+")

    with open(file, "r") as stream:
        tasks_yaml = yaml.safe_load(stream)

    tasks = []
    if tasks_yaml is not None:
        for t in tasks_yaml:
            tasks.append(Task.load(t))

    return tasks

def list_tasks(tasks):
    i = 0
    for t in tasks:
        print (f"[{i}]")
        print_task(t)
        i = i+1

def save(*args, **kwargs):
    if (settings.get("data_mode") == settings.DATA_MODE_DB):
        save_db(args[0], **kwargs)
    elif (settings.get("data_mode") == settings.DATA_MODE_YAML):
        save_yaml(args[0], args[1], **kwargs)

def save_db(tasks):
    hooks.save_to_db(tasks)

def save_yaml(tasks, file, preserve_comments=True):
    if preserve_comments:
        # preserve comments in file
        with open(file, "r") as stream:
            filestream = stream.read()

        match = re.findall("([#][^\n]*[\n]|[#][\n])", filestream)

    with open(file, "w") as stream:
        if preserve_comments and match:
            for m in match:
                stream.write(m)

        yaml.dump(tasks, stream, default_flow_style=False, sort_keys=False)

def append_task_to_file(task, file):
    tasks = load_tasks(file)
    tasks.append(task)
    save_tasks(tasks, file)

def delete_task_from_file(index, file):
    tasks = load_tasks(file)
    if index < 0 or index >= len(tasks):
        log.error_print(f"core.task.delete_task_from_file: Invalid index: {index}")
        return

    del(tasks[index])
    save_tasks(tasks, file)

def print_task(task):
        print(f"""Name: {task.name}
Source ids: {task.source_ids}
Frequency: {task.frequency} {task.frequency_unit}
Url: {task.url}
Include: {task.include}
Exclude: {task.exclude}
""")

# <-- don't output yaml class tags
def noop(self, *args, **kw):
    pass

yaml.emitter.Emitter.process_tag = noop
# --------------------------------------->

if __name__ == "__main__":
    t = load_tasks("tasks.yaml")
    save_tasks(t, "tasks.yaml", "tasks.yaml")

def task_creator(cur_tasks, sources, notif_agents, file, edit_task=None):
    from main import dry_run, prime_task

    while True:
        t = {}
        if edit_task:
            e = edit_task
            old_task_name = e.name
            t["id"] = e.id
            t["name"] = e.name
            t["freq"] = e.frequency
            t["frequ"] = e.frequency_unit
            t["sources"] = e.source_ids

            if len(e.include) == 0 or e.include[0] == "":
                t["include"] = ""
            else:
                t["include"] = ",".join(e.include)

            if len(e.exclude) == 0 or e.exclude[0] == "":
                t["exclude"] = ""
            else:
                t["exclude"] = ",".join(e.exclude)

            t["notif_agents"] = e.notif_agent_ids

        while True:
#            t["id"] = creator.prompt_id(creator.get_id_list(cur_tasks))
            t["id"] = creator.create_simple_id(list(cur_tasks))
            t["name"] = creator.prompt_string("Name", default=t.get("name", None))
            t["freq"] = creator.prompt_num("Frequency", default=t.get("freq", 15))
            t["frequ"] = creator.prompt_options("Frequency Unit", ["minutes", "hours"], default=t.get("frequ", "minutes"))
            t["sources"] = create_task_add_sources(sources, default=t.get("sources", None))
            t["include"] = creator.prompt_string("Include [list seperated by commas]", allow_empty=True, default=t.get("include", None))
            t["exclude"] = creator.prompt_string("Exclude [list seperated by commas]", allow_empty=True, default=t.get("exclude", None))
            t["notif_agents"] = create_task_add_notif_agents(notif_agents, default=t.get("notif_agents", None))

            print()
            print(f"Name: {t['name']}")
            print(f"Frequency: {t['freq']} {t['frequ']}")
            print(f"Sources")
            print(f"----------------------------")
            for s in t["sources"]:
                print(f"{sources[s].name}")
            print("-----------------------------")
            print(f"Include: {t['include']}")
            print(f"Exclude: {t['exclude']}")

            task = Task(
                id = t["id"],
                name = t["name"],
                frequency = t["freq"],
                frequency_unit = t["frequ"],
                source_ids = t["sources"],
                include = t["include"].split(","),
                exclude = t["exclude"].split(","),
                notif_agent_ids = t["notif_agents"]
            )

            while True:
                confirm = creator.prompt_options("Choose an option", ["save", "edit", "dryrun", "quit"])
                if confirm == "quit":
                    if creator.yes_no("Quit without saving?", "n") == "y":
                        return
                    else:
                        continue
                elif confirm == "dryrun":
                    if creator.yes_no("Execute dry run?", "y"):
                        log.debug_print("Executing dry run...")
                        dry_run(task)

                    continue
                else:
                    break

            if confirm == "save":
                break
            elif confirm == "edit":
                continue



        if edit_task is None:
            cur_tasks[task.id] = task
        else:
            e = edit_task
            e.id = t["id"]
            e.name = t["name"]
            e.frequency = t["freq"]
            e.frequency_unit = t["frequ"]
            e.source_ids = t["sources"]
            e.include = t["include"].split(",")
            e.exclude = t["exclude"].split(",")
            e.notif_agent_ids = t["notif_agents"]
            task = edit_task

        save(cur_tasks, file)

        """
        if creator.yes_no("Test this task with a dry run", "y") == "y":
            while True:
                dry_run(task)

                confirm = creator.yes_no("Do you want to go back and edit this task")
                if confirm == "y":
                    continue
                elif confirm == "n":
                    break
        """

        if creator.yes_no("Prime this task?", "y") == "y":
            recent = creator.prompt_num("How many of the latest ads do you want notified?", default="3")
            prime_task (task, recent_ads=int(recent))


        if not cron.exists(task.frequency, task.frequency_unit):
            if creator.yes_no(f"Add cronjob for '{task.frequency} {task.frequency_unit}'", "y"):
                cron.clear()
                for task_id in cur_tasks:
                    task = cur_tasks[task_id]
                    #if not cron.exists(t.frequency, task.frequency_unit):
                        #cron.add(task.frequency, task.frequency_unit)
                    cron.add(task.frequency, task.frequency_unit)
                    print (f"adding: {task}")
        else:
            print (f"Cronjob already exists for '{task.frequency} {task.frequency_unit}'... skipping")

        print ("Done!")
        return

def create_task_add_sources(sources_dict, default=None):
    default_str = ""
    if default is None and len(sources_dict) == 1:
        default = [list(sources_dict)[0]]

    if default is not None:
        first = True
        for s in default:
            if not s in sources_dict:
                continue

            if first:
                default_str = f"[{sources_dict[s].name}"
                first = False
            else:
                default_str = f"{default_str}, {sources_dict[s].name}"

        default_str = f" {default_str}]"

    add_sources = []

    if len(sources_dict) == 0:
        log.error_print(f"No sources found. Please add a source ")
        return

    sources_list = list(sources_dict.values())
    remaining_sources = sources_list.copy()
    while len(remaining_sources) > 0:
        i = 0
        for s in remaining_sources:
            print(f"{i} - {s.name}")
            i = i + 1

        choices = "0"
        if len(remaining_sources) > 1:
            choices = f"0-{len(remaining_sources) - 1}"

        if len(add_sources) > 0:
            print("r - reset")
            print("d - done")

        if default is None or len(add_sources) > 0:
            source_index_str = input(f"Source [{choices}]: ")
        else:
            source_index_str = input(f"Source [{choices}]:{default_str} ")

        if default is not None and source_index_str == "" and len(add_sources) == 0:
            return default

        if len(remaining_sources) == 0 and source_index_str == "":
            add_sources.append(remaining_sources[source_index])
            break

        if len(add_sources):
            if source_index_str == "d":
                break
            elif source_index_str == "r":
                print ("Resetting...")
                remaining_sources = sources_list.copy()
                add_sources = []

        if re.match("[0-9]+$", source_index_str):
            source_index = int(source_index_str)

            if source_index >= 0 and source_index < len(sources_list):
                add_sources.append(remaining_sources[source_index])
                del(remaining_sources[source_index])
                if len(remaining_sources) == 0:
                    break

                confirm = creator.yes_no("Add another?", "y")
                if confirm == "n":
                    break

    result = []
    for s in add_sources:
        result.append(s.id)

    return result

def create_task_add_notif_agents(notif_agents_dict, default=None):
    default_str = ""
    if default is None and len(notif_agents_dict) == 1:
        default = [list(notif_agents_dict)[0]]

    if default is not None:
        first = True
        for s in default:
            if not s in notif_agents_dict:
                continue

            if first:
                default_str = f"[{notif_agents_dict[s].name}"
                first = False
            else:
                default_str = f"{default_str}, {notif_agents_dict[s].name}"

        default_str = f" {default_str}]"

    add_notif_agents = []

    if len(notif_agents_dict) == 0:
        log.error_print(f"No notif_agents found. Please add a notif_agent ")
        return

    notif_agents_list = list(notif_agents_dict.values())
    remaining_notif_agents = notif_agents_list.copy()
    while len(remaining_notif_agents) > 0:
        i = 0
        for s in remaining_notif_agents:
            print(f"{i} - {s.name}")
            i = i + 1

        choices = "0"
        if len(remaining_notif_agents) > 1:
            choices = f"0-{len(remaining_notif_agents) - 1}"

        if len(add_notif_agents) > 0:
            print("r - reset")
            print("d - done")

        if default is None or len(add_notif_agents) > 0:
            notif_agent_index_str = input(f"notif_agent [{choices}]: ")
        else:
            notif_agent_index_str = input(f"notif_agent [{choices}]:{default_str} ")

        if default is not None and notif_agent_index_str == "" and len(add_notif_agents) == 0:
            return default

        if len(remaining_notif_agents) == 0 and notif_agent_index_str == "":
            add_notif_agents.append(remaining_notif_agents[notif_agent_index])
            break

        if len(add_notif_agents):
            if notif_agent_index_str == "d":
                break
            elif notif_agent_index_str == "r":
                print ("Resetting...")
                remaining_notif_agents = notif_agents_list.copy()
                add_notif_agents = []

        if re.match("[0-9]+$", notif_agent_index_str):
            notif_agent_index = int(notif_agent_index_str)

            if notif_agent_index >= 0 and notif_agent_index < len(notif_agents_list):
                add_notif_agents.append(remaining_notif_agents[notif_agent_index])
                del(remaining_notif_agents[notif_agent_index])
                if len(remaining_notif_agents) == 0:
                    break

                confirm = creator.yes_no("Add another?", "y")
                if confirm == "n":
                    break

    result = []
    for s in add_notif_agents:
        result.append(s.id)

    return result

def create_task(cur_tasks, sources, notif_agents, file):
    if len(sources) == 0:
        log.error_print("No sources found. Please add a source before creating a task")
        return

    if len(notif_agents) == 0:
        log.error_print("No notification agents found. Please add a notification agent before creating a task")
        return

    creator.print_title("Add Task")
    task_creator(cur_tasks, sources, notif_agents, file, edit_task=None)

def edit_task(cur_tasks, sources, notif_agents, file):
    creator.print_title("Edit Task")
    task = creator.prompt_complex_dict("Choose a task", cur_tasks, "name", extra_options=["d"], extra_options_desc=["done"])
    if task == "d":
        return
    else:
        task_creator(cur_tasks, sources, notif_agents, file, task)

def delete_task(tasks, file):
    creator.print_title("Delete Task")

    while True:
        tasks_list = list(tasks.values())

        for i in range(len(tasks_list)):
            print(f"{i} - {tasks_list[i].name}")

        print("s - save")
        print("q - quit without saving")
        tnum_str = creator.prompt_string("Delete task")
        if tnum_str == "s":
            save(tasks, file)
            return
        elif tnum_str == "q":
            return

        if re.match("[0-9]+$", tnum_str):
            tnum = int(tnum_str)
            if tnum >= 0 and tnum < len(tasks):
                if creator.yes_no(f"Are you sure you want to delete {tasks_list[tnum].name}") == "y":
                    do_delete_task(tasks_list[tnum].id, tasks)

def do_delete_task(*args, **kwargs):
    if (settings.get("data_mode") == settings.DATA_MODE_DB):
        do_delete_task_db(args[0], args[1])
    elif (settings.get("data_mode") == settings.DATA_MODE_YAML):
        do_delete_task_yaml(args[0], args[1])

def do_delete_task_db(id, tasks):
    hooks.delete_task_model(tasks[id])

    del tasks[id]

def do_delete_task_yaml(id, tasks):
    del tasks[id]

