"""

"""
import os
import yaml
import collections
import subprocess
import re

import creator_utils_lib as creator

minute="minute"
hour="hour"
day="day"

class Task:
    yaml_tag = None

    def __init__(self, **kwargs):
            self.name = kwargs.get("name", "New Task")
            self.enabled = kwargs.get("enabled", True)
            self.frequency = kwargs.get("frequency", 15)
            self.frequency_unit = kwargs.get("frequency_unit", "minutes")
            self.source_ids = kwargs.get("source_ids", [])
            self.notif_agent_ids = kwargs.get("notif_agent_ids", [])
            self.include = kwargs.get("include", [])
            self.exclude = kwargs.get("exclude", [])

    def set_frequency(freq, unit):
        self.frequency = freq
        self.frequency_unit = unit

    def yaml(self):
        return yaml.dump(self.__dict)

    @staticmethod
    def load(data):
        values = data
        #print(values)

        if "exclude" in values:
            exclude = values["exclude"]
        else:
            exclude = []


        return Task(**data)

    def matches_freq(self, time, unit):
        return time == self.frequency and unit[:1] == self.frequency_unit[:1]

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

def list_tasks_in_file(file):
    list_tasks(load_tasks(file))

def list_tasks(tasks):
    i = 0
    for t in tasks:
        print (f"[{i}]")
        print_task(t)
        i = i+1

def save(tasks, file, preserve_comments=True):
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
        logging.error(f"tasklib.delete_task_from_file: Invalid index: {index}")
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

def task_creator(cur_tasks, sources, file, edit_task=None):
    t = {}
    if edit_task:
        e = edit_task
        old_task_name = e.name
        t["name"] = e.name
        t["freq"] = e.frequency
        t["frequ"] = e.frequency_unit
        t["sources"] = e.source_ids
        if len(e.include):
            t["include"] = ",".join(e.include)
        else:
            t["include"] = ""

        if len(e.exclude):
            t["exclude"] = ",".join(e.exclude)
        else:
            t["exclude"] = ""


    while True:
        t["name"] = creator.prompt_string("Name", default=t.get("name", None))
        t["freq"] = creator.prompt_num("Frequency", default=t.get("freq", 15))
        t["frequ"] = creator.prompt_options("Frequency Unit", ["minutes", "hours"], default=t.get("frequ", "minutes"))
        t["sources"] = create_task_add_sources(sources, default=t.get("sources", None))
        t["include"] = creator.prompt_string("Include [list seperated by commas]", allow_empty=True, default=t.get("include", None))
        t["exclude"] = creator.prompt_string("exclude [list seperated by commas]", allow_empty=True, default=t.get("exclude", None))

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

        """
        if edit_task is None:
            confirm_msg = "Create this task"
        else:
            confirm_msg = f"Save changes to task '{old_task_name}'"

        confirm = creator.prompt_options(confirm_msg, ["y", "n", "quit"])
        """

        confirm = creator.prompt_options("Choose an option", ["save", "edit", "quit"])

        if confirm == "save":
            break
        elif confirm == "edit":
            continue
        elif confirm == "quit":
            return

    if t["include"] != "":
        t["include"] = t["include"].split(",")

    if t["exclude"] != "":
        t["exclude"] = t["exclude"].split(",")

    if edit_task is None:
        task = Task(
            name=t["name"],
            frequency=t["freq"],
            frequency_unit=t["frequ"],
            source_ids=t["sources"],
            include=t["include"],
            exclude=t["exclude"]
        )
        cur_tasks.append(task)
    else:
        e = edit_task
        e.name = t["name"]
        e.frequency = t["freq"]
        e.frequency_unit = t["frequ"]
        e.source_ids = t["sources"]
        e.include = t["include"].split(",")
        e.exclude = t["include"].split(",")

    save(cur_tasks, file)

def create_task_add_sources(sources_dict, default=None):
    default_str = ""
    if default is not None:
        first = True
        for s in default:
            if first:
                default_str = f"[{sources_dict[s].name}"
                first = False
            else:
                default_str = f"{default_str}, {sources_dict[s].name}"

        default_str = f" {default_str}]"

    add_sources = []

    if len(sources_dict) == 0:
        log.error_print(f"No sources found. Please create a source first")
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

                confirm = creator.yes_no("Add another?", "y")
                if confirm == "n":
                    break

    result = []
    for s in add_sources:
        result.append(s.id)

    return result

def create_task(cur_tasks, sources, file, edit_task=None):
    creator.print_title("Add Task")
    task_creator(cur_tasks, sources, file, edit_task=edit_task)

def edit_task(cur_tasks, sources, file):
    creator.print_title("Edit Task")
    task = creator.prompt_complex_list("Choose a task", cur_tasks, "name", extra_options=["d"], extra_options_desc=["done"])
    if task == "d":
        return
    else:
        create_task(cur_tasks, sources, file, task)

def delete_task(tasks_list, file):
    creator.print_title("Delete Task")
    while True:
        for i in range(len(tasks_list)):
            print(f"{i} - {tasks_list[i].name}")

        print("s - save")
        print("q - quit without saving")
        tnum_str = creator.prompt_string("Delete task")
        if tnum_str == "s":
            save(tasks_list, file)
            return
        elif tnum_str == "q":
            return

        if re.match("[0-9]+$", tnum_str):
            tnum = int(tnum_str)
            if tnum >= 0 and tnum < len(tasks_list):
                if creator.yes_no(f"Are you sure you want to delete {tasks_list[tnum].name}") == "y":
                    del tasks_list[tnum]

