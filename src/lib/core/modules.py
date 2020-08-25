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

    if not list_of_sources:
        for l in get_sources_list():
            module = models.Modules(category='source',
                                    name=l[1],
                                    module_id=l[0])
            session.add(module)
            session.commit()
    else:
        for l in get_sources_list():

            # this is important otherwise Line 40 doesn't work.
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

def get_notifagents_list():


    return notifagents_list

def generate_form(module_id):
    for m in get_sources_list():
        if m[0] == module_id:
            module_name = m[1].lower()

    form = []


    for subdir, dirs, files in walk(f'modules/sources/{module_name}'):
        if path.exists(path.join(subdir,'module_data.json')):
            with open(path.join(subdir,'module_data.json')) as f:
                data = json.load(f)
                for d in data['form']:
                    try:
                        if d['field']:
                            response_field = d['field']
                    except:
                        response_field = ""
                        
                    try:
                        if d['id']:
                            response_id = " id=\"" + d['id'] + "\""
                    except:
                        response_id = ""
                        
                    try:
                        if d['name']:
                            response_name = " name=\"" + d['name'] + "\""
                            label_name = "<label class=\"form-control-label\" for=\"" + d['id'] + "\">" + d['name'] + "</label>"
                    except:
                        response_name = ""
                        label_name = ""

                    try:
                        if d['required'] == True:
                            response_required = " required"
                        else:
                            response_required = ""
                    except:
                        response_required = ""
                    
                    try:
                        if d['type']:
                            response_type = " type=\"" + d['type'] + "\""
                    except:
                        response_type = ""
                        
                    try:
                        if d['value']:
                            response_value = " value=\"" + d['value'] + "\""
                    except:
                        response_value = ""
                        
                    try:
                        if d['message']:
                            response_message = d['message']
                    except:
                        response_message = ""
                        
                    try:
                        if d['cssClass']:
                            response_css_class = " class=\"" + d['cssClass'] + "\""
                    except:
                        response_css_class = ""

                    form.append(f"{label_name}<{response_field}{response_id}{response_name}{response_required}{response_type}{response_value}{response_css_class}>{response_message}</{response_field}>")
    return form