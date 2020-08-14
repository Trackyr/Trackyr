from os import path, walk
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from trackyr.config import Config
from trackyr import models

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
session = Session(engine)

def get_sources_list():
    source_list = []
    for subdir, dirs, files in walk('modules/sources'):
        if path.exists(path.join(subdir,'module_data.json')):
            with open(path.join(subdir,'module_data.json')) as f:
                data = json.load(f)
                source_list.append((data['id'], data['name']))

    return source_list

def generate_sources_in_db():             
    list_of_sources = session.query(models.Modules).filter_by(category='source').all()
    log.info_print(f"list_of_sources: {list_of_sources}")
    if not list_of_sources:
        for l in get_sources_list():
            module = models.Modules(category='source',
                                    name=l[1],
                                    module_id=l[0])
            session.add(module)
            session.commit()
            log.info_print(f"Added {module}")
    else:
        for l in get_sources_list():

            # this is important otherwise Line 43 doesn't work.
            for los in list_of_sources:
                pass
            
            if any(los.name == l[1] for los in list_of_sources):
                pass
            else:
                module = models.Modules(category='source',
                                        name=l[1],
                                        module_id=l[0])
                session.add(module)
                session.commit()