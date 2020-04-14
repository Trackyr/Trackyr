import yaml
import sys
import os
import json
import imp

current_directory = os.path.dirname(os.path.abspath(__file__ + "/../.."))

import lib.core.settings as settings
settings_file = current_directory + "/settings.yaml"

import lib.utils.logger as log
log.load(current_directory + "/logs/", settings.get("log_rotation_files"))
log.set_level(settings.get("log_mode"))

import lib.core as core
import lib.core.task as task
import lib.core.source as source
import lib.core.notif_agent as notif_agent

import lib.core.ad as ad

import lib.core.hooks as hooks
import lib.utils.collection_tools as ct

_ads_file = f"{current_directory}/ads.json"
_tasks_file = f"{current_directory}/tasks.yaml"
_sources_file = f"{current_directory}/sources.yaml"
_source_modules_dir = "modules/sources"
_notif_agents_file = f"notification_agents.yaml"
_notif_agent_modules_dir = "modules/notif_agents"

_ads = ad.load(_ads_file)
_source_modules = source.load_modules(current_directory, source_modules_dir)
_notif_agent_modules = notif_agent.load_modules(current_directory, __notif_agent_modules_dir)

log.debug(f"Loading data using data mode: {settings.get('data_mode')}")

if settings.get("data_mode") == settings.DATA_MODE_YAML:
    _tasks = task.load_tasks(_tasks_file)
    _sources = source.load_sources(_sources_file)
    _notif_agents = notif_agent.load_agents(current_directory, notif_agents_file, __notif_agent_modules_dir)

elif settings.get("data_mode") == settings.DATA_MODE_DB:
    _tasks = hooks.load_core_tasks()
    _sources = hooks.load_core_sources()
    _notif_agents = hooks.load_core_notif_agents()

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

    task_notif_agents = notif_agent.get_notif_agents_by_ids(_notif_agents, task.notif_agent_ids)

    if notify == True and force_agents == False:
        notif_agent.notif_agents_enabled_check(task_notif_agents)

    for source_id in task.source_ids:
        scrape_source(
            _sources[source_id],
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
        ad.save_ads(_ads, _ads_file)

def scrape_source(source, notif_agents, include=[], exclude=[], notify=True, force_tasks=False, force_agents=False, recent_ads=0, save_ads=True):
    log.info_print(f"Source: {source.name}")
    log.info_print(f"Module: {source.module}")
    log.info_print(f"Module Properties: {source.module_properties}")

    if len(include):
        print(f"Including: {include}")

    if len(exclude):
        print(f"Excluding: {exclude}")

    scraper = _source_modules[source.module]

    old_ads = []
    if source.module in ads:
        old_ads = _ads[source.module]
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

                    _notif_agent_modules[agent.module].send_ads(ads_to_send, ad_title, **agent.module_properties)

                else:
                    log.info_print(f"Skipping... Notification agent disabled: {agent.name}")

                i = i + 1

    elif not notify and num_ads:
        log.info_print("Skipping notification")

    if save_ads:
        _ads[source.module] = scraper.old_ad_ids
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
    for t in _tasks:
        task = _tasks[t]
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

    ad.save_ads(_ads, _ads_file)

def get_tasks():
    return _tasks

def set_tasks(tasks):
    ids = []
    for id in tasks:
        if id in ids:
            raise ValueError(f"Duplicate id detected while setting tasks: {id}")

    ids.append(id)

    _tasks = tasks

def get_sources():
    return _sources

def set_sources(sources):
    ids = []
    for id in sources:
        if id in ids:
            raise ValueError(f"Duplicate id detected while setting sources: {id}")

        ids.append(id)

    _sources = sources

def get_notif_agents():
    return _notif_agents

def set_notif_agents(notif_agents):
    ids = []
    for id in notif_agents:
        if id in ids:
            raise ValueError(f"Duplicate id detected while setting notif_agents: {id}")

        ids.append(id)

    _notif_agents = notif_agents


from lib.core.task import Task
from lib.core.notif_agent import NotifAgent
from lib.core.source import Source


