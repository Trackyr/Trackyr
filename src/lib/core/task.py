import os
import collections
import subprocess
import re
import uuid

import lib.core.settings as settings
import lib.utils.logger as log

import lib.utils.cron as cron
import lib.core.hooks as hooks
import lib.utils.creator as creator
import lib.core as core

import yaml
# don't output yaml class tags
def noop(self, *args, **kw):
    pass

yaml.emitter.Emitter.process_tag = noop


class Task:
    def __init__(self,
            id = None,
            name = "New Task",
            enabled = True,
            frequency = 15,
            frequency_unit = "minutes",
            source_ids = None,
            notif_agent_ids = None,
            include = None,
            exclude = None
        ):

        if id is None:
            id = creator.create_simple_id(core.get_tasks())

        self.id = id
        self.name = name
        self.enabled = enabled
        self.frequency = frequency
        self.frequency_unit = frequency_unit
        self.source_ids = source_ids
        self.notif_agent_ids = notif_agent_ids
        self.include = include
        self.exclude = exclude

    def __repr__(self):
        source_names = []
        sources = core.get_sources()
        for id in self.source_ids:
            source_names.append(f"'{sources[id].name}'")

        notif_agent_names = []
        notif_agents = core.get_notif_agents()
        for id in self.notif_agent_ids:
            notif_agent_names.append(f"'{notif_agents[id].name}'")

        return f"""
name: {self.name}
frequency: {self.frequency} {self.frequency_unit}
sources: {','.join(source_names)}
notification agents: {','.join(notif_agent_names)}
include: {','.join(self.include)}
exclude: {','.join(self.exclude)}
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

def validate(task, sources, notif_agents, stay_alive = True):
    for s in task.source_ids:
        if not s in sources:
            if stay_alive:
                task.source_ids.remove(s)
                log.warning_print(f"Source not found: '{s}'. Removing from task '{task.id} - {task.name}'")
            else:
                raise ValueError(f"Error validating task '{task.id} - {task.name}': Source '{s}' not found")

    for n in task.notif_agent_ids:
        if not n in notif_agents:
            if stay_alive:
                task.notif_agent_ids.remove(s)
                log.warning_print(f"Notification agent not found: '{s}'. Removing from task '{task.id} - {task.name}'")
            else:
                raise ValueError(f"Error validating task '{task.id} - {task.name}': Notification Agent '{s}' not found")

def prime(task, notify=True, recent_ads = 3):
    if recent_ads > 0:
        notify = True
    else:
        notify = False

    core.run_task(task, notify=notify, recent_ads=recent_ads)

def prime_all(tasks, notify=True, recent_ads=3):
    for id in tasks:
        prime(tasks[id], notify=notify, recent_ads=recent_ads)

# save file depending on the data mode
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
    for t in tasks:
        print(tasks[t])

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

def task_creator(task, cur_tasks, sources, notif_agents, file):
    t = task

    while True:
        while True:
            t.name = creator.prompt_string("Name", default=t.name)
            t.frequency = creator.prompt_num("Frequency", default=t.frequency)
            t.frequency_unit = creator.prompt_options("Frequency Unit", ["minutes", "hours"], default=t.frequency_unit)
            t.source_ids = create_task_add_sources(sources, default=t.source_ids)
            if t.source_ids == None:
                return
            t.include = creator.prompt_string("Include [list seperated by commas]", allow_empty=True, default=t.include)
            t.exclude = creator.prompt_string("Exclude [list seperated by commas]", allow_empty=True, default=t.exclude)
            t.notif_agent_ids = create_task_add_notif_agents(notif_agents, default=t.notif_agent_ids)
            if t.notif_agent_ids == None:
                return

            print()
            print(f"Name: {t.name}")
            print(f"Frequency: {t.frequency} {t.frequency_unit}")
            print(f"Sources")
            print(f"----------------------------")
            print(sources)
            for source_id in t.source_ids:
                print(f"{sources[source_id].name}")
            print("-----------------------------")
            print(f"Include: {t.include}")
            print(f"Exclude: {t.exclude}")

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
                        core.run_task(task, notify=False, save_ads=False)

                    continue
                else:
                    break

            if confirm == "save":
                break
            elif confirm == "edit":
                continue

        cur_tasks[task.id] = task
        save(cur_tasks, file)

        if creator.yes_no("Prime this task?", "y") == "y":
            recent = int(creator.prompt_num("How many of the latest ads do you want notified?", default="3"))
            if recent == 0:
                notify=False
            else:
                notify=True

            prime(task, notify=notify, recent_ads=recent)

        if not cron.exists(task.frequency, task.frequency_unit):
            if creator.yes_no(f"Add cronjob for '{task.frequency} {task.frequency_unit}'", "y") == "y":
                cron.clear()
                for task_id in cur_tasks:
                    add_task = cur_tasks[task_id]
                    cron.add(add_task.frequency, add_task.frequency_unit)

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
    task_creator(Task(), cur_tasks, sources, notif_agents, file)

def edit_task(cur_tasks, sources, notif_agents, file):
    creator.print_title("Edit Task")
    task = creator.prompt_complex_dict("Choose a task", cur_tasks, "name", extra_options=["d"], extra_options_desc=["done"])
    if task == "d":
        return
    else:
        task_creator(task, cur_tasks, sources, notif_agents, file)

def choose_task(
        msg,
        title,
        tasks,
        file,
        options_dict = None,
        confirm_msg = None
    ):

    creator.print_title(title)

    while True:
        tasks_list = list(tasks.values())

        for i in range(len(tasks_list)):
            print(f"{i} - {tasks_list[i].name}")

        if options_dict is not None:
            for o in options_dict:
                print(f"{o} - {options_dict[o]}")

        tnum_str = creator.prompt_string(msg)

        if options_dict is not None:
            for o in options_dict:
                if re.match(tnum_str, o):
                    return o

        if not re.match("[0-9]+$", tnum_str):
            continue

        tnum = int(tnum_str)
        if tnum < 0 and tnum >= len(tasks):
            continue

        task = tasks_list[tnum]

        if confirm_msg is not None:
            if creator.yes_no(format_task_string(confirm_msg, task)) == "n":
                continue

        return tasks_list[tnum]


def format_task_string(string, task):
    while True:
        m = re.findall("([{][^}]*[}])", string)
        if m is None or len(m) == 0:
            break

        attr = re.search("[^{][^}]*", m[0]).group(0)
        string = re.sub(m[0], getattr(task, attr), string)

    return string

def delete_task(tasks, file):
    option = choose_task(
                "Choose an option",
                "Delete Task",
                tasks,
                file,
                options_dict = {"s":"save","q":"quit"},
                confirm_msg = "Are you sure you want to delete {name}"
    )

    if option == "s":
        save(tasks, file)
        return

    elif option == "q":
        return

    elif isinstance(option, Task):
        do_delete_task(option, tasks)

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

