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
import settings_lib as settings
settings_file = current_directory + "/settings.yaml"
settings.load(settings_file)

import notification_agent_lib as agentlib
import scraper_lib as scraperlib
import task_lib as tasklib
import source_lib as sourcelib
import cron_lib as cronlib
import creator_utils_lib as creator

import reflection_lib as refl
import logger_lib as log

def notif_agents_enabled_check(notif_agents):
    if len(agentlib.get_enabled(notif_agents)) == 0:
        log.warning_print("There are no enabled agents... no notifications will be sent")

def refresh_cron():
    cronlib.clear()
    for t in tasks:
        if cronlib.exists(t.frequency, t.frequency_unit):
            continue

        cronlib.add(t.frequency, t.frequency_unit)

def prime_all_tasks(args):
    for task in tasks:
        run_task(task, notify=not args.skip_notification, recent_ads=args.notify_recent)

    save_ads()

# force - run task regardless if it is enabled or not
# recent_ads - only show the latest N ads, set to 0 to disable
def run_task(task, sources, ads, source_modules, notif_agents, notif_agent_modules, notify=True, force_tasks=False, force_agents=False, recent_ads=0):
    exclude_words = task.exclude

    log.info_print(f"Task: {task.name}")

    if task.enabled == False:
        if force_tasks == False:
            log.info_print("Task disabled. Skipping...")
            print()
            return
        else:
            log.info_print("Task disabled but forcing task to run...")


    task_notif_agents = agentlib.get_notif_agents_by_ids(notif_agents, task.notif_agent_ids)
    print (f"notif agents: {task_notif_agents}")
    if notify == True and force_agents == False:
        notif_agents_enabled_check(task_notif_agents)

    for source_id in task.source_ids:
        scrape_source(
            sources[source_id],
            task_notif_agents,
            source_modules,
            notif_agent_modules,
            include=task.include,
            exclude=task.exclude,
            notify=notify,
            force_tasks=force_tasks,
            force_agents=force_agents,
            recent_ads=recent_ads
        )

def scrape_source(source, ads, notif_agents, source_modules, notif_agent_modules, include=[], exclude=[], notify=True, force_tasks=False, force_agents=False, recent_ads=0):
    log.info_print(f"Source: {source.name}")
    log.info_print(f"Module: {source.module}")
    log.info_print(f"Module Properties: {source.module_properties}")

    if len(include):
        print(f"Including: {include}")

    if len(exclude):
        print(f"Excluding: {exclude}")

    source_module = source_modules[source.module]
    old_ads = []
    if source.module in ads:
        old_ads = ads[source.module]

    new_ads, ad_title = source_module.scrape_for_ads(old_ads, exclude=exclude, **source.module_properties)

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
                log.info_print(f"Notifying agents: {agentlib.get_names(notif_agents)}")

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

    ads[source.module] = source_module.old_ad_ids
    log.debug_print(f"Total all-time processed ads: {len(source_module.old_ad_ids)}")

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
def cron_job(cron_args, notify=True, force_tasks=False, force_agents=False, recent_ads=settings.get("recent_ads")):
    log.add_handler(log.CRON_HANDLER)

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


