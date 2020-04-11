#!/usr/bin/env python3
# see main.py -h for help

import yaml
import sys
import os
import importlib
import json
import inspect
import argparse

from lib.core import settings
from lib import core
from lib.utils import cron

def main():
    parser = argparse.ArgumentParser()
    notify_group = parser.add_mutually_exclusive_group()
    notify_group.add_argument("-s", "--skip-notification", action="store_true", default=False)
    if settings.get("recent_ads") == 0:
        recent_ads_help = "Only notify only most recent \# of ads. Default is infinite (0)"
    else:
        recent_ads_help = f"Only notify only most recent \# of ads. Default is {settings.get('recent_ads')}"

    notify_group.add_argument("--notify-recent", type=int, default=settings.get("recent_ads"), help=f"Only notify only most recent \# of ads. Default is {settings.get('recent_ads')}")    
    parser.add_argument("--force-tasks", action="store_true", help="Force tasks to run even if they are disabled")
    parser.add_argument("--force-notification-agents", action="store_true", help="Force notification agents to be used even when disabled")

    main_args = parser.add_mutually_exclusive_group()
    main_args.add_argument("-c", "--cron-job", nargs=2, metavar=('INTEGER','minutes|hours'))
    main_args.add_argument("-r", "--refresh-cron", action="store_true", help="Refresh cron with current task frequencies")
    main_args.add_argument("-p", "--prime-all-tasks", action="store_true", help="Prime all tasks. If tasks file was edited manually, prime all the ads to prevent large notification dump")
    main_subparsers = parser.add_subparsers(dest="cmd")

    task_sub = main_subparsers.add_parser("task")
    task_subparsers = task_sub.add_subparsers(dest="task_cmd")
    task_subparsers.required = True
    task_add = task_subparsers.add_parser("add", help="Add a new task")
    task_delete = task_subparsers.add_parser("delete", help="Delete an existing task")
    task_edit = task_subparsers.add_parser("edit", help="Edit an existing task")

    source_sub = main_subparsers.add_parser("source")
    source_subparsers = source_sub.add_subparsers(dest="source_cmd")
    source_subparsers.required = True
    source_add = source_subparsers.add_parser("add", help="Add a new source")
    source_delete = source_subparsers.add_parser("delete", help="Delete an existing source")
    source_edit = source_subparsers.add_parser("edit", help="Edit an existing source")

    notif_agent_sub = main_subparsers.add_parser("notification-agent")
    notif_agent_subparsers = notif_agent_sub.add_subparsers(dest="notif_agent_cmd")
    notif_agent_subparsers.required = True
    notif_agent_add = notif_agent_subparsers.add_parser("add", help="Add a new notif_agent")
    notif_agent_add = notif_agent_subparsers.add_parser("delete", help="Delete a new notif_agent")
    notif_agent_add = notif_agent_subparsers.add_parser("edit", help="Edit a new notif_agent")

    args = parser.parse_args()

    if args.prime_all_tasks:
        prime_all_tasks(args)

    if args.refresh_cron:
        refresh_cron()

    if args.cron_job:
        core.cron(
            args.cron_job[0],
            args.cron_job[1],
            notify=not args.skip_notification,
            force_tasks=args.force_tasks,
            force_agents=args.force_notification_agents,
            recent_ads=args.notify_recent)

    if args.cmd == "task":
        task_cmd(args)
    elif args.cmd == "source":
        source_cmd(args)
    elif args.cmd == "notification-agent":
        notif_agent_cmd(args)

def task_cmd(args):
    if (args.task_cmd == "add"):
        core.task.create_task(core.tasks, core.sources, core.agents, core.tasks_file)
        return

    elif (args.task_cmd == "delete"):
        core.task.delete_task(core.tasks, core.tasks_file)
        return

    elif (args.task_cmd == "edit"):
        core.task.edit_task(core.tasks, core.sources, core.agents, core.tasks_file)
        return

    else:
        log.error_print(f"Unknown task command: {args.task_cmd}")

def task_list_cmd(args):
    core.task.list_tasks(core.tasks)

def notif_agent_cmd(args):
    if args.notif_agent_cmd == "add":
        core.notif_agent.create_notif_agent(core.agents, core.notif_agent_modules, core.notif_agents_file)
    elif args.notif_agent_cmd == "edit":
        core.notif_agent.edit_notif_agent(core.agents, core.notif_agent_modules, core.notif_agents_file)
    elif args.notif_agent_cmd == "delete":
        core.notif_agent.delete_notif_agent(core.agents, core.notif_agents_file, core.tasks, core.tasks_file)

def source_cmd(args):
    if args.source_cmd == "add":
        core.source.create_source(core.sources, core.scrapers, core.sources_file)
    elif args.source_cmd == "delete":
        core.source.delete_source(core.sources, core.sources_file, core.tasks, core.tasks_file)
    elif args.source_cmd == "edit":
        core.source.edit_source(core.sources, core.scrapers, core.sources_file)

def refresh_cron():
    cron.clear()
    for id in core.tasks:
        t = core.tasks[id]
        if cron.exists(t.frequency, t.frequency_unit):
            continue

        cron.add(t.frequency, t.frequency_unit)

def dry_run(task):
    core.run_task(task, notify=False, force_tasks=True, save_ads=False)

def prime_task(task, recent_ads = settings.get("recent_ads")):
    if recent_ads > 0:
        notify = True
    else:
        notify = False

    core.run_task(task, notify=notify, recent_ads=recent_ads)

def prime_all_tasks(args):
    for task in core.tasks:
        core.run_task(task, notify=not args.skip_notification, recent_ads=args.notify_recent)

    save_ads()

if __name__ == "__main__":
    main()

