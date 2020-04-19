#!/usr/bin/env python3.7
# see 'main.py -h' for help
# or 'main.py task|source|notification-agent -h'

import argparse

import lib.core as core
import lib.core.settings as settings
import lib.core.cron as cron
import lib.utils.cron as cronutils

import lib.core.menu as menu

def main():
    parser = argparse.ArgumentParser()
    notify_group = parser.add_mutually_exclusive_group()
    notify_group.add_argument("-s", "--skip-notification", action="store_true", default=False)

    notify_group.add_argument(
        "--notify-recent",
        type=int,
        help="Limit notification to only most recent \# of ads. 0 sets no limit"
    )

    parser.add_argument("--force-tasks", action="store_true", help="Force tasks to run even if they are disabled")
    parser.add_argument("--force-notification-agents", action="store_true", help="Force notification agents to be used even when disabled")

    main_args = parser.add_mutually_exclusive_group()
    main_args.add_argument("-c", "--cron-job", nargs="+", metavar=('INTEGER','minutes|hours'))
    main_args.add_argument("-r", "--refresh-cron", action="store_true", help="Refresh cron with current task frequencies")
    main_args.add_argument("-p", "--prime-all-tasks", action="store_true", help="Prime all tasks. If tasks file was edited manually, prime all the ads to prevent large notification dump")
    main_subparsers = parser.add_subparsers(dest="cmd")

    menu_sub = main_subparsers.add_parser("menu", help="Convenient menu for setup")

    task_sub = main_subparsers.add_parser("task")
    task_subparsers = task_sub.add_subparsers(dest="task_cmd")
    task_subparsers.required = True
    task_add = task_subparsers.add_parser("add", help="Add a new task")
    task_delete = task_subparsers.add_parser("delete", help="Delete an existing task")
    task_edit = task_subparsers.add_parser("edit", help="Edit an existing task")
    task_list = task_subparsers.add_parser("list", help="List all tasks")

    source_sub = main_subparsers.add_parser("source")
    source_subparsers = source_sub.add_subparsers(dest="source_cmd")
    source_subparsers.required = True
    source_add = source_subparsers.add_parser("add", help="Add a new source")
    source_delete = source_subparsers.add_parser("delete", help="Delete an existing source")
    source_edit = source_subparsers.add_parser("edit", help="Edit an existing source")
    source_edit = source_subparsers.add_parser("list", help="List all sources")

    notif_agent_sub = main_subparsers.add_parser("notification-agent")
    notif_agent_subparsers = notif_agent_sub.add_subparsers(dest="notif_agent_cmd")
    notif_agent_subparsers.required = True
    notif_agent_add = notif_agent_subparsers.add_parser("add", help="Add a new notif_agent")
    notif_agent_delete = notif_agent_subparsers.add_parser("delete", help="Delete a new notif_agent")
    notif_agent_edit = notif_agent_subparsers.add_parser("edit", help="Edit a new notif_agent")
    notif_agent_list = source_subparsers.add_parser("list", help="List all notification agents")

    args = parser.parse_args()

    notify_recent = settings.get("recent_ads")
    if args.notify_recent is not None:
        notify_recent = args.notify_recent

    if args.cron_job:
        if args.cron_job[0] == "path":
            cron.print_path()
        else:
            cron.run(
                args.cron_job[0],
                args.cron_job[1],
                notify=not args.skip_notification,
                force_tasks=args.force_tasks,
                force_agents=args.force_notification_agents,
                recent_ads=notify_recent
            )

    elif args.cmd == "task":
        task_cmd(args)

    elif args.cmd == "source":
        source_cmd(args)

    elif args.cmd == "notification-agent":
        notif_agent_cmd(args)

    elif args.cmd == "menu":
        menu.start()

    elif args.prime_all_tasks:
        task.prime_all(recent_ads=notify_recent)

    elif args.refresh_cron:
        task.refresh_cron()

    else:
        parser.print_help()

def task_cmd(args):
    if args.task_cmd == "add":
        core.task.create_task(core.get_tasks(), core.get_sources(), core.get_notif_agents(), core.TASKS_FILE)

    elif args.task_cmd == "delete":
        core.task.delete_task(core.get_tasks(), core.TASKS_FILE)

    elif args.task_cmd == "edit":
        core.task.edit_task(core.get_tasks(), core.get_sources(), core.get_notif_agents(), core.TASKS_FILE)

    elif args.task_cmd == "list":
        core.task.list_tasks(core.get_tasks())

    else:
        raise ValueError(f"Unknown task command: {args.task_cmd}")


def source_cmd(args):
    if args.source_cmd == "add":
        core.source.create_source(core.get_sources(), core.get_source_modules(), core.SOURCES_FILE)

    elif args.source_cmd == "delete":
        core.source.delete_source(core.get_sources(), core.SOURCES_FILE, core.get_tasks(), core.TASKS_FILE)

    elif args.source_cmd == "edit":
        core.source.edit_source(core.get_sources(), core.get_source_modules(), core.SOURCES_FILE)

    elif args.source_cmd == "list":
        core.source.list(core.get_sources())

    else:
        raise ValueError(f"Unknown source command: {args.source_cmd}")


def notif_agent_cmd(args):
    if args.notif_agent_cmd == "add":
        core.notif_agent.create_notif_agent(core.get_notif_agents(), core.get_notif_agent_modules(), core.NOTIF_AGENTS_FILE)

    elif args.notif_agent_cmd == "edit":
        core.notif_agent.edit_notif_agent(core.get_notif_agents(), core.get_notif_agent_modules(), core.NOTIF_AGENTS_FILE)

    elif args.notif_agent_cmd == "delete":
        core.notif_agent.delete_notif_agent(core.get_notif_agents(), core.NOTIF_AGENTS_FILE, core.get_tasks(), core.TASKS_FILE)

    elif args.notif_agent_cmd == "list":
        core.notif_agent.list(core.notif_agents)

    else:
        raise ValueError(f"Unknown notification-agent command: {args.notif_agent_cmd}")

def refresh_cron():
    cronutils.clear()
    tasks = core.get_tasks()
    for id in tasks:
        t = tasks[id]
        if croutilsn.exists(t.frequency, t.frequency_unit):
            continue

        cronutils.add(t.frequency, t.frequency_unit)

if __name__ == "__main__":
    main()

