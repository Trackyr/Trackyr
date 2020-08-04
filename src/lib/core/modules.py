from os import path, walk
import json

def get_sources_list():
    source_list = []

    for subdir, dirs, files in walk('modules/sources'):
        if path.exists(path.join(subdir,'module_data.json')):
            with open(path.join(subdir,'module_data.json')) as f:
                data = json.load(f)
                source_list.append((data['id'], data['name']))
      
    return source_list
    