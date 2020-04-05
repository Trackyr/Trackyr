import source_lib as sourcelib
import scraper_lib as scraper
import task_lib as tasklib

import uuid
import re
import logger_lib as log

def prompt_num(msg, force_positive=True, default=None):
    default_str = ""

    if default is not None:
        default_str = f" [{default}]"

    while True:
        num_str = input(f"{msg}:{default_str} ")
        if num_str == "":
            if default is not None:
                return default

        if re.match("[0-9]+$", num_str):
            num = int(num_str)
            return num

def prompt_range(msg, min, max, default=None, extra_options=None, allow_abbrev=True):
    default_str = ""

    if default is not None:
        default_str = f" [{default}]"

    range_str = ""
    range_num = None

    if min >= 0:
        if max == min:
            range_str = [min]
            range_num = min
        elif max > min:
            range_str = f" [{min}-{max}]"

    while True:
        num_str = input(f"{msg}{range_str}: {default_str}")
        if num_str == "":
            if default is not None:
                return default

        if extra_options is not None and allow_abbrev:
            found = None
            ambiguous = False
            for num_str in extra_options:
                if check in o:
                    if found is not None:
                        print(f"{check} is too ambiguous, try a longer abbreviation")
                        ambiguous = True
                        break

                    found = o

            if not ambiguous:
                return found

        if re.match("[0-9]+$", num_str):
            num = int(num_str)
            if num >= min and num <= max:
                return num

def prompt_options(msg, options, default=None, print_options=True, case_sens=False, allow_abbrev=True):
    default_str = ""

    if default is not None:
        default_str = f" [{default}]"

    if case_sens == False:
        for i in range(len(options)):
            options[i] = options[i].lower()

    choices = "/".join(options)

    result = None
    while True:
        result = input(f"{msg} [{choices}]:{default_str} ")
        check = result

        if result == "":
            if default is not None:
                return default
            else:
                continue

        if not case_sens:
            check = check.lower()

        if allow_abbrev:
            found = None
            ambiguous = False
            for o in options:
                if re.match(check, o):
                    if found is not None:
                        print(f"{check} is too ambiguous, try a longer abbreviation")
                        ambiguous = True
                        break

                    found = o

            if not ambiguous:
                return found
        else:
            if check in options:
                return result

    return result

def yes_no(msg, default=None, ending="?"):
    default_str = ""
    if default is not None:
        default_str = f" [{default}]"

    result = None
    while result != "y" and result != "n":
        result = input(f"{msg} [y/n]{ending}{default_str} ")
        if default != None and result == "":
            return default

    return result

def prompt_id(id_list, max_tries=10000, default=None):
    while True:
        simple_default = "n"

        if default is not None:
            if isinstance(default, int):
                simple_default = "y"
            else:
                simple_default = "n"

        simple_id = yes_no("Use simple id?", f"{simple_default}")

        if default is not None and simple_id == simple_default:
            id = default
            break

        if simple_id == "y":
            i = 0
            while i < max_tries:
                if not i in id_list:
                    break;
                i = i + 1

            if i >= max_tries:
                raise ValueError(f"For some reason max tries of {max_tries} was reached...")

            id = i
            break

        elif simple_id == "n":
            id = str(uuid.uuid4())
            break

    print (f"Id: {id}")
    return id

def get_id_list(dict_source):
    ids = []
    for s in dict_source:
        ids.append(dict_source[s].id)

    return ids

def prompt_string(msg, allow_empty=False, default=None):
    while True:
        default_str = ""
        if default is not None:
            default_str = f" [{default}]"

        result = input(f"{msg}:{default_str} ")
        if result == "":
            if default is not None:
                if allow_empty and default != "":
                    if yes_no("Set empty instead of default", default="n") == "y":
                        return ""
                    else:
                        return default
                else:
                    return default
            elif allow_empty:
                return result
        else:
            return result

def empty_list_to_empty_string(l):
    if l is None:
        return None

    if len(l) == 0:
        return ""

    return l

def prompt_complex_dict(msg, dict, display_attr, default=None, extra_options=None, extra_options_desc=None):
    l = list(dict.values())

    while True:
        for i in range(len(l)):
            attr = getattr(l[i], display_attr)
            print(f"{i} - {attr}")

        if extra_options is not None and extra_options_desc is not None:
            for i in range(len(extra_options)):
                print(f"{extra_options[i]} - {extra_options_desc[i]}")

        s = prompt_string(msg, default=default)

        for o in extra_options:
            if re.match(s.lower(), o.lower()):
                return o

        if re.match("[0-9]+$", s):
            index = int(s)
            if index >= 0 and index < len(l):
                return l[index]

def prompt_complex_list(msg, list, display_attr, default=None, extra_options=None, extra_options_desc=None):
    l = list

    while True:
        for i in range(len(l)):
            attr = getattr(l[i], display_attr)
            print(f"{i} - {attr}")

        if extra_options is not None and extra_options_desc is not None:
            for i in range(len(extra_options)):
                print(f"{extra_options[i]} - {extra_options_desc[i]}")

        s = prompt_string(msg, default=default)

        for o in extra_options:
            if re.match(s.lower(), o.lower()):
                return o

        if re.match("[0-9]+$", s):
            index = int(s)
            if index >= 0 and index < len(l):
                return l[index]

def print_title(title):
    print("--------------------------------")
    print(title)
    print("================================")

