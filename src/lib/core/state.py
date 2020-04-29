import json

from lib.core.config import Config

class State():
    _ads = None
    _tasks = None
    _sources = None
    _notif_agents = None
    _source_modules = None
    _notif_agent_modules = None

    def load():
        State.refresh_all()

    def refresh_all():
        State.refresh_ads()
        State.refresh_tasks()
        State.refresh_sources()
        State.refresh_notif_agents()
        State.refresh_source_modules()
        State.refresh_notif_agent_modules()

    def refresh_ads():
        import lib.core.ad as ad
        State._ads = ad.load()

    def refresh_tasks():
        import lib.core.task as task
        State._tasks = hooks.load_core_tasks()

    def refresh_sources():
        import lib.core.source as source
        State._sources = hooks.load_core_sources()

    def refresh_notif_agents():
        import lib.core.notif_agent as notif_agent
        State._notif_agents = hooks.load_core_notif_agents()

    def refresh_source_modules():
        import lib.core.source as source
        State._source_modules = source.load_modules(Config.CURRENT_DIRECTORY, Config.SOURCE_MODULES_DIR)

    def refresh_notif_agent_modules():
        import lib.core.notif_agent as notif_agent
        State._notif_agent_modules = notif_agent.load_modules(Config.CURRENT_DIRECTORY, Config.NOTIF_AGENT_MODULES_DIR)

    def get_ads():
        return State._ads

    def get_tasks():
        return State._tasks

    def set_tasks(tasks):
        ids = []
        for id in tasks:
            if id in ids:
                raise ValueError(f"Duplicate id detected while setting tasks: {id}")

        ids.append(id)

        State._tasks = tasks

    def save_tasks():
        hooks.save_to_db(State._tasks)

    def get_sources():
        return State._sources

    def get_source_modules():
        return State._source_modules

    def set_sources(sources):
        ids = []
        for id in sources:
            if id in ids:
                raise ValueError(f"Duplicate id detected while setting sources: {id}")

            ids.append(id)

        State._sources = sources

    def save_sources():
        hooks.save_to_db(State._sources)

    def get_notif_agents():
        return State._notif_agents


    def get_notif_agent_modules():
        return State._notif_agent_modules

    def set_notif_agents(notif_agents):
        ids = []
        for id in notif_agents:
            if id in ids:
                raise ValueError(f"Duplicate id detected while setting notif_agents: {id}")

            ids.append(id)

        State._notif_agents = notif_agents

    def save_notif_agents():
        hooks.save_to_db(State._notif_agents)

import lib.core.hooks as hooks
State.load()
