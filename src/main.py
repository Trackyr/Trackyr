#!/usr/bin/env python3

# main.py -h for help
# main.py --cron-job help
# main.py task -h
# main.py task [add|delete|list] -h for more help!

import yaml
import sys
import os
import importlib
import json
import inspect
import argparse

current_directory = os.path.dirname(os.path.realpath(__file__))

# import settings file first so other modules can use settings
from lib.core import settings
from lib.utils import logger as log

if __name__ == "__main__":
    settings_file = current_directory + "/settings.yaml"
    settings.load(settings_file)
    log.load(current_directory + "/logs/", settings.get("log_rotation_files"))

import lib.core as core
print (core.task)

ads_file = f"{current_directory}/ads.json"
tasks_file = f"{current_directory}/tasks.yaml"
sources_file = f"{current_directory}/sources.yaml"
notif_agents_file = f"notification_agents.yaml"
notif_agent_modules_dir = "modules/notif_agents"
scrapers_dir = "scrapers"
scrapers = {}
sources = {}
agents = {}
ads = {}

if not os.path.exists(ads_file):
    with open(ads_file, "w") as stream:
        stream.write("{}")  

with open(ads_file, "r") as stream:
    ads = yaml.safe_load(stream)

tasks = core.task.load_tasks(tasks_file)
sources = core.source.load_sources(sources_file)
scrapers = core.source.load_modules(current_directory, "modules/sources")
agents = core.notif_agent.load_agents(current_directory, notif_agents_file, notif_agent_modules_dir)
notif_agent_modules = core.notif_agent.load_modules(current_directory, notif_agent_modules_dir)

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

    # task {name} {frequency} {frequency_unit}
    task_sub = main_subparsers.add_parser("task")
    task_subparsers = task_sub.add_subparsers(dest="task_cmd", required=True)
    task_add = task_subparsers.add_parser("add", help="Add a new task")
    task_delete = task_subparsers.add_parser("delete", help="Delete an existing task")
    task_edit = task_subparsers.add_parser("edit", help="Edit an existing task")

    source_sub = main_subparsers.add_parser("source")
    source_subparsers = source_sub.add_subparsers(dest="source_cmd", required=True)
    source_add = source_subparsers.add_parser("add", help="Add a new source")
    source_delete = source_subparsers.add_parser("delete", help="Delete an existing source")
    source_edit = source_subparsers.add_parser("edit", help="Edit an existing source")

    notif_agent_sub = main_subparsers.add_parser("notification-agent")
    notif_agent_subparsers = notif_agent_sub.add_subparsers(dest="notif_agent_cmd", required=True)
    notif_agent_add = notif_agent_subparsers.add_parser("add", help="Add a new notif_agent")
    notif_agent_add = notif_agent_subparsers.add_parser("delete", help="Delete a new notif_agent")
    notif_agent_add = notif_agent_subparsers.add_parser("edit", help="Edit a new notif_agent")

    args = parser.parse_args()

    if args.prime_all_tasks:
        prime_all_tasks(args)

    if args.refresh_cron:
        refresh_cron()

    if args.cron_job:
        cron_cmd(args.cron_job,
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

def notif_agent_cmd(args):
    if args.notif_agent_cmd == "add":
        core.notif_agent.create_notif_agent(agents, core.notif_agent.load_modules(current_directory, notif_agent_modules_dir), notif_agents_file)
    elif args.notif_agent_cmd == "edit":
        core.notif_agent.edit_notif_agent(agents, core.notif_agent.load_modules(current_directory, notif_agent_modules_dir), notif_agents_file)
    elif args.notif_agent_cmd == "delete":
        core.notif_agent.delete_notif_agent(agents, notif_agents_file, tasks, tasks_file)

def source_cmd(args):
    if args.source_cmd == "add":
        core.source.create_source(sources, scrapers, sources_file)
    elif args.source_cmd == "delete":
        core.source.delete_source(sources, sources_file, tasks, tasks_file)
    elif args.source_cmd == "edit":
        core.source.edit_source(sources, scrapers, sources_file)


def test_log():
    #log.addHandler(cron_loghandler)
    log.info("test")

def notif_agents_enabled_check(notif_agents):
    if len(core.notif_agent.get_enabled(notif_agents)) == 0:
        log.warning_print("There are no enabled agents... no notifications will be sent")

def refresh_cron():
    cronlib.clear()
    for t in tasks:
        if cronlib.exists(t.frequency, t.frequency_unit):
            continue

        cronlib.add(t.frequency, t.frequency_unit)

def dry_run(task):
    run_task(task, notify=False, force_tasks=True, save_ads=False)

def prime_task(task, recent_ads = settings.get("recent_ads")):
    if recent_ads > 0:
        notify = True
    else:
        notify = False

    run_task(task, notify=notify, recent_ads=recent_ads)

def prime_all_tasks(args):
    for task in tasks:
        run_task(task, notify=not args.skip_notification, recent_ads=args.notify_recent)

    save_ads()

def task_cmd(args):
    if (args.task_cmd == "add"):
        core.task.create_task(tasks, sources, agents, tasks_file)
        return

    if (args.task_cmd == "delete"):
        core.task.delete_task(tasks, tasks_file)
        return

    if (args.task_cmd == "edit"):
        core.task.edit_task(tasks, sources, agents, tasks_file)
        return

    cmds = {
        "add" : task_add_cmd,
        "delete" : task_delete_cmd,
        "list" : task_list_cmd
    }

    if args.task_cmd in cmds:
        cmds[args.task_cmd](args)
    else:
        log.error_print(f"Unknown task command: {args.task_cmd}")

def task_list_cmd(args):
    core.task.list_tasks(tasks)

def task_add_cmd(args):
    task = core.task.Task(\
        name = args.name,\
        frequency = args.frequency,\
        frequency_unit = args.frequency_unit,\
        source = args.source,\
        url = args.url,\
        include = args.include,\
        exclude = args.exclude\
    )

    if args.skip_confirm != True:
        core.task.print_task(task)
        confirm = input("Add this task? [Y/n] ").lower()
        if confirm == "n":
            print ("Canceled")
            return

    tasks.append(task)
    core.task.save_tasks(tasks, tasks_file)
    cronlib.add(args.frequency, args.frequency_unit)

    print ("Task added")

    prime = True
    if args.prime_ads == None:
        askprime = input("Would you like to prime ads now? [Y/n]")
        if askprime == "n":
            prime = False

    if prime:
        run_task(task, notify=not args.skip_notification, recent_ads=args.notify_recent)
        save_ads()

def task_delete_cmd(args):
    index = args.index

    if index < 0 or index >= len(tasks):
        log.error_print(f"task delete: index must be 0-{len(tasks)-1}")
        return

    if args.skip_confirm != True:
        core.task.print_task(tasks[index])
        confirm = input("Delete this task? [y/N] ").lower()
        if confirm != "y":
            print ("Canceled")
            return

    freq = tasks[index].frequency
    freq_unit = tasks[index].frequency_unit

    del(tasks[index])
    core.task.save_tasks(tasks, tasks_file)

    # clear cronjob if no remaining tasks share the frequency
    freq_found = False
    for task in tasks:
        if task.matches_freq(freq, freq_unit):
            freq_found = True

    if freq_found == False:
        cronlib.delete(freq, freq_unit)

    print(f"Deleted task [{index}]")

# force - run task regardless if it is enabled or not
# recent_ads - only show the latest N ads, set to 0 to disable
def run_task(task, notify=True, force_tasks=False, force_agents=False, recent_ads=0, save_ads=True):
    exclude_words = task.exclude

    log.info_print(f"Task: {task.name}")

    if task.enabled == False:
        if force_tasks == False:
            log.info_print("Task disabled. Skipping...")
            print()
            return
        else:
            log.info_print("Task disabled but forcing task to run...")


    task_notif_agents = core.notif_agent.get_notif_agents_by_ids(agents, task.notif_agent_ids)
    if notify == True and force_agents == False:
        notif_agents_enabled_check(task_notif_agents)

    for source_id in task.source_ids:
        scrape_source(
            sources[source_id],
            task_notif_agents,
            include=task.include,
            exclude=task.exclude,
            notify=notify,
            force_tasks=force_tasks,
            force_agents=force_agents,
            recent_ads=recent_ads,
            save_ads=save_ads
        )

def scrape_source(source, notif_agents, include=[], exclude=[], notify=True, force_tasks=False, force_agents=False, recent_ads=0, save_ads=True):
    log.info_print(f"Source: {source.name}")
    log.info_print(f"Module: {source.module}")
    log.info_print(f"Module Properties: {source.module_properties}")

    if len(include):
        print(f"Including: {include}")

    if len(exclude):
        print(f"Excluding: {exclude}")

    scraper = scrapers[source.module]
    old_ads = []
    if source.module in ads:
        old_ads = ads[source.module]

    new_ads, ad_title = scraper.scrape_for_ads(old_ads, exclude=exclude, **source.module_properties)

    info_string = f"Found {len(new_ads)} new ads" \
        if len(new_ads) != 1 else "Found 1 new ad"

    log.info_print(info_string)

    num_ads = len(new_ads)
    if notify and num_ads:
        i = 0

        ads_to_send = new_ads

        if recent_ads > 0:
            # only notify the last notify_recent new_ads
            ads_to_send = get_recent_ads(recent_ads, new_ads)
            log.info_print(f"Total ads to notify about: {len(ads_to_send)}")

        if len(notif_agents) == 0:
            log.warning_print("No notification agents set... nothing to notify")
        else:
            if len(notif_agents) > 1:
                log.info_print(f"Notifying agents: {core.notif_agent.get_names(notif_agents)}")

            for agent in notif_agents:
                if agent.enabled or force_agents == True:
                    if agent.enabled == False and force_agents == True:
                        log.info_print("Notification agent was disabled but forcing...")

                    notif_agent_modules[agent.module].send_ads(ads_to_send, ad_title, **agent.module_properties)

                else:
                    log.info_print(f"Skipping... Notification agent disabled: {agent.name}")

                i = i + 1

    elif not notify and num_ads:
        log.info_print("Skipping notification")

    if save_ads:
        ads[source.module] = scraper.old_ad_ids
        log.debug_print(f"Total all-time processed ads: {len(scraper.old_ad_ids)}")
    else:
        log.info_print(f"Saving ads disabled. Skipping...")
    print()

def get_recent_ads(recent, ads):
    i = 0

    result = {}

    for a in ads:
        if i >= len(ads) - recent:
            result[a] = ads[a]

        i = i + 1

    return result

# This was run as a cronjob so find all tasks that match the schedule
# -c {cron_time} {cron_unit}
# cron_time: integer
# cron_unit: string [ minute | hour ]
def cron_cmd(cron_args, notify=True, force_tasks=False, force_agents=False, recent_ads=settings.get("recent_ads")):
    log.add_handler("CRON_HANDLER")

    cron_time = cron_args[0]
    cron_unit = cron_args[1]

    log.info_print(f"Running cronjob for schedule: {cron_time} {cron_unit}")

    # Scrape each url given in tasks file
    for task in tasks:
        freq = task.frequency
        freq_unit = task.frequency_unit

        # skip tasks that dont correspond with the cron schedule
        if int(freq) != int(cron_time) or freq_unit[:1] != cron_unit[:1]:
            continue

        run_task(task,
            notify=notify,
            force_tasks=force_tasks,
            force_agents=force_agents,
            recent_ads=recent_ads)

    save_ads()

def save_ads():
    with open(ads_file, "w") as stream:
        json.dump(ads, stream)

if __name__ == "__main__":
    main()

