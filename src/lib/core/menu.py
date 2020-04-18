import lib.utils.creator as prompts
from lib.core.state import State
import lib.core as core

import lib.core.task as task
import lib.core.source as source
import lib.core.notif_agent as notif_agent

def start():
    while True:
        option = prompts.prompt_options(
            get_msg("Choose a Category"),
            ["tasks","sources","notification agents",None,"quit"],
            print_options = False,
            menu_style = True,
            menu_title = get_title("Categories")
        )

        if option == "tasks":
            tasks()

        elif option == "sources":
            sources()

        elif option == "notification agents":
            notif_agents()

        elif option == "quit":
            return

        else:
            print(f"'{option}' not implemented.")

def tasks():
    while True:
        option = prompts.prompt_options(
            get_msg("Choose a Task Option"),
            ["new","edit","delete",None,"list","test","prime",None,"back to menu"],
            print_options = False,
            menu_style = True,
            menu_title = get_title("Tasks")
        )

        if option == "new":
            task.task_creator(task.Task())

        elif option == "edit":
            task.edit_task()

        elif option == "delete":
            task.delete_task()

        elif option == "list":
            task.list_tasks(pause_after = 1)

        elif option == "test":
            test_task()

        elif option == "prime":
            prime_task()

        elif option == "back to menu":
            return

        else:
            print(f"'{option}' not implemented.")

def test_task():
    option = simple_cmd("Choose a Task to Test", "Test Task", State.get_tasks(), task.Task)
    if option is not None:
        task.test(option)

def prime_task():
    option = simple_cmd("Choose a Task to Prime", "Prime Task", State.get_tasks(), task.Task)
    if option is not None:
        task.prime(option)

def simple_cmd(msg, title, dict, obj):
    while True:
        option = prompts.choose_from_dict(
            get_msg(msg),
            get_title(title),
            dict,
            options_dict = { "d" : "done" },
        )

        if option == "d":
            return None

        elif isinstance(option, obj):
            return option

def sources():
    while True:
        option = prompts.prompt_options(
            get_msg("Choose a Source Option"),
            ["new","edit","delete",None,"list","test",None,"back to menu"],
            print_options = False,
            menu_style = True,
            menu_title = get_title("Sources")
        )

        if option == "back to menu":
            return

        elif option == "new":
            source.source_creator(source.Source())

        elif option == "edit":
            source.edit_source()

        elif option == "delete":
            source.delete_source()

        elif option == "list":
            source.list_sources(pause_after = 1)

        elif option == "test":
            test_source()

        else:
            print(f"'{option}' not implemented.")

def test_source():
    option = simple_cmd("Choose a Source to Test", "Test Source", State.get_sources(), source.Source)
    if option is not None:
        source.test_source(option)

def notif_agents():
    while True:
        option = prompts.prompt_options(
            get_msg("Choose a Notification Agent Option"),
            ["new","edit","delete",None,"list","test",None,"back to menu"],
            print_options = False,
            menu_style = True,
            menu_title = get_title("Notification Agents")
        )

        if option == "new":
            notif_agent.notif_agent_creator(
                notif_agent.NotifAgent(),
            )

        elif option == "edit":
            notif_agent.edit_notif_agent(
            )

        elif option == "delete":
            notif_agent.delete_notif_agent(
            )

        elif option == "list":
            notif_agent.list_notif_agents(pause_after = 1)

        elif option == "test":
            test_notif_agent()

        elif option == "back to menu":
            return

        else:
            print(f"'{option}' not implemented.")


def test_notif_agent():
    option = simple_cmd("Choose a Notification Agent to Test", "Test Notification Agent", State.get_notif_agents(), core.NotifAgent)
    if option is not None:
        notif_agent.test_notif_agent(option)

def get_title(title):
    return f"{title}\n---------------------"

def get_msg(msg):
    return f"---------------------\n{msg}"
