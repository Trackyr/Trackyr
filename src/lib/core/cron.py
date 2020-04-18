import lib.utils.logger as log

from lib.core.state import State
import lib.core.task as task
import lib.core.source as source


# This was run as a cronjob so find all tasks that match the schedule
# -c {cron_time} {cron_unit}
# cron_time: integer
# cron_unit: string [ minute | hour ]
def run(
        cron_time,
        cron_unit,
        notify=True,
        force_tasks=False,
        force_agents=False,
        recent_ads=3
    ):

    tasks = State.get_tasks()

    log.add_handler("CRON_HANDLER")

    log.info_print(f"Running cronjob for schedule: {cron_time} {cron_unit}")

    # Scrape each url given in tasks file
    for id in tasks:
        t = tasks[id]
        freq = t.frequency
        freq_unit = t.frequency_unit

        # skip tasks that dont correspond with the cron schedule
        if int(freq) != int(cron_time) or freq_unit[:1] != cron_unit[:1]:
            continue

        task.run(
            t,
            notify=notify,
            force_tasks=force_tasks,
            force_agents=force_agents,
            recent_ads=recent_ads
        )

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

def get_source_modules():
    return _source_modules

def set_sources(sources):
    ids = []
    for id in sources:
        if id in ids:
            raise ValueError(f"Duplicate id detected while setting sources: {id}")

        ids.append(id)

    _sources = sources

def get_notif_agents():
    return _notif_agents


def get_notif_agent_modules():
    return _notif_agent_modules

def set_notif_agents(notif_agents):
    ids = []
    for id in notif_agents:
        if id in ids:
            raise ValueError(f"Duplicate id detected while setting notif_agents: {id}")

        ids.append(id)

    _notif_agents = notif_agents


