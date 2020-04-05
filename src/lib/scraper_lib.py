#!/usr/bin/env python3

import yaml
import sys
import os
import importlib
#import json
import inspect

import reflection_lib as refl


class BaseScraper():
    def get_properties():
        pass

    def set_properties(props):
        valid_props = get_properties()
        for p in props:
            if not p in valid_props:
                raise ValueError(f"Invalid module property '{p}'")

# looks for sub diretories inside "scrapers/"
# and inspects its contents for a "scraper.py" file and grabs the class inside that file
# PARAMS: scraper_ads - json of all the previously scraped files
# RETURNS: a dictionary {scraper_name : scraper_instance} 
def get_scrapers(directory, scraper_dir):
    result = {}
    filename = "scraper.py"

    subdirs = refl.get_directories(f"{directory}/{scraper_dir}")
    for subdir in subdirs:
        scraper_name = subdir
        path = f"{directory}/{scraper_dir}/{subdir}/{filename}"
        if not os.path.exists(path):
            continue

        namespace = refl.path_to_namespace(f"{scraper_dir}/{subdir}/{filename}")
        finder = importlib.machinery.PathFinder()
        spec = importlib.util.find_spec(f"{namespace}")
        #spec = importlib.machinery.find_spec(f"{path}")
        module = importlib.util.module_from_spec(spec)
#        sys.modules[module_name] = module
        spec.loader.exec_module(module)

#        module = refl.get_module(namespace)
        module_class_name, module_class = refl.get_class(module, namespace)
        result[subdir] = module_class()

    return result
