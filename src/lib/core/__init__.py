from .task import Task
from .notif_agent import NotifAgent
from .source import Source

import yaml
import sys
import os
import json
import imp

current_directory = os.path.dirname(os.path.abspath(__file__ + "/../.."))

from . import settings
settings_file = current_directory + "/settings.yaml"

from lib.utils import logger as log
log.load(current_directory + "/logs/", settings.get("log_rotation_files"))
log.set_level(settings.get("log_mode"))

from . import hooks
from lib.utils import collection_tools as ct

ads_file = f"{current_directory}/ads.json"
if not os.path.exists(ads_file):
    with open(ads_file, "w") as stream:
        stream.write("{}")

with open(ads_file, "r") as stream:
    ads = yaml.safe_load(stream)

for key in ads:
    log.debug(f"Total old ads from {key}: {len(ads[key])}")

tasks_file = f"{current_directory}/tasks.yaml"
sources_file = f"{current_directory}/sources.yaml"
source_modules_dir = "modules/sources"
notif_agents_file = f"notification_agents.yaml"
notif_agent_modules_dir = "modules/notif_agents"

scrapers = source.load_modules(current_directory, source_modules_dir)
notif_agent_modules = notif_agent.load_modules(current_directory, notif_agent_modules_dir)

log.debug(f"Loading data using data mode: {settings.get('data_mode')}")

if settings.get("data_mode") == settings.DATA_MODE_YAML:
    tasks = task.load_tasks(tasks_file)
    sources = source.load_sources(sources_file)
    agents = notif_agent.load_agents(current_directory, notif_agents_file, notif_agent_modules_dir)

elif settings.get("data_mode") == settings.DATA_MODE_DB:
    tasks = hooks.load_core_tasks()
    sources = hooks.load_core_sources()
    agents = hooks.load_core_notif_agents()

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


    task_notif_agents = notif_agent.get_notif_agents_by_ids(agents, task.notif_agent_ids)
    if notify == True and force_agents == False:
        notif_agent.notif_agents_enabled_check(task_notif_agents)

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

    if save_ads:
        save_all_ads()

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
        log.debug(f"Total old ads: {len(old_ads)}")
    else:
        log.debug(f"No old ads found for module: {source.module}")
        print(ads)


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
            ads_to_send = ct.get_last_items(recent_ads, new_ads)
            log.debug(f"Recent ads set to: {recent_ads} got: {len(ads_to_send)}")
            log.info_print(f"Total ads to notify about: {len(ads_to_send)}")

        if len(notif_agents) == 0:
            log.warning_print("No notification agents set... nothing to notify")

        else:
            if len(notif_agents) > 1:
                log.info_print(f"Notifying agents: {notif_agent.get_names(notif_agents)}")

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
        log.debug(f"Total all-time processed ads: {len(scraper.old_ad_ids)}")
    else:
        log.info_print(f"Saving ads disabled. Skipping...")

    print()

# This was run as a cronjob so find all tasks that match the schedule
# -c {cron_time} {cron_unit}
# cron_time: integer
# cron_unit: string [ minute | hour ]
def cron(cron_time, cron_unit, notify=True, force_tasks=False, force_agents=False, recent_ads=settings.get("recent_ads")): 
    log.add_handler("CRON_HANDLER")

    log.info_print(f"Running cronjob for schedule: {cron_time} {cron_unit}")

    # Scrape each url given in tasks file
    for t in tasks:
        task = tasks[t]
        freq = task.frequency
        freq_unit = task.frequency_unit

        # skip tasks that dont correspond with the cron schedule
        if int(freq) != int(cron_time) or freq_unit[:1] != cron_unit[:1]:
            continue

        run_task(task,
            notify=notify,
            force_tasks=force_tasks,
            force_agents=force_agents,
            recent_ads=recent_ads
        )

    save_all_ads()

def save_all_ads():
     with open(ads_file, "w") as stream:
        json.dump(ads, stream)
