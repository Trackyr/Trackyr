import lib.utils.creator as prompts
import lib.core as core
import lib.core.task as task
import lib.core.source as source
import lib.core.notif_agent as notif_agent

def start():
    while True:
        option = prompts.prompt_options(
            msg("Choose a Category"),
            ["tasks","sources","notification agents","quit"],
            print_options = False,
            menu_style = True,
            menu_title = title("Categories")
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
            msg("Choose a Task Option"),
            ["back to menu", "new","edit","delete","list","test","prime"],
            print_options = False,
            menu_style = True,
            menu_title = title("Tasks")
        )

        if option == "new":
            task.task_creator(core.get_tasks(), core.get_sources(), core.get_notif_agents(), core.TASKS_FILE)

        elif option == "edit":
            task.edit_task(core.get_tasks(), core.get_sources(), core.get_notif_agents(), core.TASKS_FILE)

        elif option == "delete":
            task.delete_task(core.get_tasks(), core.TASKS_FILE)

        elif option == "back to menu":
            return

        else:
            print(f"'{option}' not implemented.")

def sources():
    while True:
        option = prompts.prompt_options(
            msg("Choose a Source Option"),
            ["back to menu", "new","edit","delete","list","test"],
            print_options = False,
            menu_style = True,
            menu_title = title("Sources")
        )

        if option == "back to menu":
            return

        elif option == "new":
            source.source_creator(
                Source(),
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


        else:
            print(f"'{option}' not implemented.")

def notif_agents():
    while True:
        option = prompts.prompt_options(
            msg("Choose a Notification Agent Option"),
            ["back to menu", "new","edit","delete","list","test"],
            print_options = False,
            menu_style = True,
            menu_title = title("Notification Agents")
        )

        if option == "new":
            notif_agent.notif_agent_creator(
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

        elif option == "back to menu":
            return

        else:
            print(f"'{option}' not implemented.")


def title(title):
    return f"{title}\n---------------------"

def msg(msg):
    return f"---------------------\n{msg}"
