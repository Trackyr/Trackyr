from lib import core

from copy import deepcopy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

#,from database import metadata, Job
from trackyr.config import Config

from trackyr import models
#from trackyr.models import Task
#from trackyr.models import Source
#from trackyr.models import NotificationAgent

#import lib.core as core

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
session = Session(engine)

def to_core_task(task_model):
    t = deepcopy(task_model)

    if isinstance(t.source, str):
        t.source = [t.source]

    if isinstance(t.notification_agent, str):
        t.notification_agent = [t.notification_agent]

    return core.Task(
            name = t.name,
            id = t.id,
            frequency = t.frequency,
            frequency_unit = "minutes",
            source_ids = t.source,
            notif_agent_ids = t.notification_agent,
            include = t.must_contain.split(","),
            exclude = t.exclude
        )

def to_core_notif_agent(notif_agent_model):
    n = deepcopy(notif_agent_model)
    n.module_properties = {
        "webhook": n.webhook_url,
        "botname": n.username
    }

    return core.NotifAgent(
                id = n.id,
                name = n.name,
                module = n.module,
                module_properties = n.module_properties,
            )

def to_core_source(source_model):
    s = deepcopy(source_model)

    s.module_properties = {
        "url": s.website
    }

    return core.Source(
                id = s.id,
                name = s.name,
                module = s.module,
                module_properties = s.module_properties
            )

def to_task_model(core_task):
    pass

def to_source_model(core_source):
    pass

def to_notif_agent_model(core_notif_agent):
    pass

def load_core_tasks():
    task_models = session.query(models.Task).all()
    tasks = []

    for task_model in task_models:
        tasks.append(
            to_core_task(task_model)
        )

    return tasks

def load_core_sources():
    source_models = session.query(models.Source).all()
    sources = []

    for source_model in source_models:
        sources.append(
            to_core_source(source_model)
        )

    return sources

def load_core_notif_agents():
    notif_agent_models = session.query(models.NotificationAgent).all()
    notif_agents = []

    for notif_agent_model in notif_agent_models:
        notif_agents.append(
            to_core_notif_agent(notif_agent_model)
        )

    return notif_agents


