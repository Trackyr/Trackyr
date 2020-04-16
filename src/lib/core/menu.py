import lib.utils.creator as prompts
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
            task.task_creator(
                task.Task(),
                core.get_tasks(),
                core.get_sources(),
                core.get_notif_agents(),
                core.TASKS_FILE
            )

        elif option == "edit":
            task.edit_task(core.get_tasks(), core.get_sources(), core.get_notif_agents(), core.TASKS_FILE)

        elif option == "delete":
            task.delete_task(core.get_tasks(), core.TASKS_FILE)

        elif option == "list":
            task.list_tasks(core.get_tasks())

        elif option == "test":
            test_task()

        elif option == "prime":
            prime_task()

        elif option == "back to menu":
            return

        else:
            print(f"'{option}' not implemented.")

def test_task():
    t = simple_cmd("Choose a Task to Test", "Test Task", core.get_tasks(), core.TASKS_FILE, task.Task)
    if task is not None:
        core.run_task(
            t,
            save_ads=False,
            notify=False,
            ignore_old_ads=True
        )

def prime_task():
    t = simple_cmd("Choose a Task to Prime", "Prime Task", core.get_tasks(), core.TASKS_FILE, task.Task)
    if task is not None:
        core.run_task(
            t,
            save_ads=True,
            notify=False,
        )

def simple_cmd(msg, title, dict, file, obj):
    while True:
        option = prompts.choose_from_dict(
            get_msg(msg),
            get_title(title),
            dict,
            file,
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
            source.source_creator(
                source.Source(),
                core.get_sources(),
                core.get_source_modules(),
                core.SOURCES_FILE
            )

        elif option == "edit":
            source.edit_source(
                core.get_sources(),
                core.get_source_modules(),
                core.SOURCES_FILE
            )

        elif option == "delete":
            source.delete_source(
                core.get_sources(),
                core.get_source_modules(),
                core.get_tasks(),
                core.NOTIF_AGENTS_FILE
            )

        elif option == "list":
            source.list_sources(core.get_sources())

        elif option == "test":
            test_source()

        else:
            print(f"'{option}' not implemented.")

def test_source():
    src = simple_cmd("Choose a Source to Test", "Test Source", core.get_sources(), core.SOURCES_FILE, core.Source)
    if source is not None:
        source.test_source(src, core.get_source_modules())

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
                core.get_notif_agents(),
                core.get_notif_agent_modules(), 
                core.NOTIF_AGENTS_FILE
            )

        elif option == "edit":
            notif_agent.edit_notif_agent(
                core.get_notif_agents(),
                core.get_notif_agent_modules(), 
                core.NOTIF_AGENTS_FILE
            )

        elif option == "delete":
            notif_agent.delete_notif_agent(
                core.get_notif_agents(),
                core.NOTIF_AGENTS_FILE,
                core.get_tasks(),
                core.TASKS_FILE
            )

        elif option == "list":
            notif_agent.list_notif_agents(core.get_notif_agents())

        elif option == "test":
            test_notif_agent()

        elif option == "back to menu":
            return

        else:
            print(f"'{option}' not implemented.")


def test_notif_agent():
    nagent = simple_cmd("Choose a Notification Agent to Test", "Test Notification Agent", core.get_notif_agents(), core.NOTIF_AGENTS_FILE, core.NotifAgent)
    if notif_agent is not None:
        notif_agent.test_notif_agent(nagent, core.get_notif_agent_modules())

def get_title(title):
    return f"{title}\n---------------------"

def get_msg(msg):
    return f"---------------------\n{msg}"

