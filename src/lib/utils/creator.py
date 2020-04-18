import uuid
import re
from copy import deepcopy

import lib.utils.logger as log
import lib.core as core

def choose_from_dict(
        msg,
        title,
        dict,
        options_dict = None,
        confirm_msg = None
    ):

    print(title)

    while True:
        dict_list = list(dict.values())

        for i in range(len(dict_list)):
            print(f"{i} - {dict_list[i].name}")

        if options_dict is not None:
            for o in options_dict:
                print(f"{o} - {options_dict[o]}")

        tnum_str = prompt_string(msg)

        if options_dict is not None:
            for o in options_dict:
                if re.match(tnum_str, o):
                    return o

        if not re.match("[0-9]+$", tnum_str):
            continue

        tnum = int(tnum_str)
        if tnum < 0 and tnum >= len(dict):
            continue

        obj = dict_list[tnum]

        if confirm_msg is not None:
            if creator.yes_no(format_string(confirm_msg, obj)) == "n":
                continue

        return obj

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

def format_string(string, obj):
    while True:
        m = re.findall("([{][^}]*[}])", string)
        if m is None or len(m) == 0:
            break

        attr = re.search("[^{][^}]*", m[0]).group(0)
        string = re.sub(m[0], getattr(obj, attr), string)

    return string

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

def prompt_options(
        msg,                        # the input message
        options,                    # the available options as list: ["option1", "option2", option3"]
        default=None,               # the default option to use when enter is pressed without anything being inputted
        enable_default=True,        # enable the use default entry
        print_options=True,         # print the options with the message: Some Message [option1/option2/option3]:]
        print_options_lower=False,  # print the options to lower if they are not case sensitive
        case_sens=False,            # are options case sensitive
        allow_abbrev=True,          # allow abbrevations as input for options: option = opt or opti or optio. fails if there are several options that match
        menu_style=False,           # do LORD style menu printing with vertical menus
        menu_title=None             # what to show at the top of the prompt before showing the options
    ):

    default_str = ""
    if enable_default and default is not None:
        default_str = f" [{default}]"

    options_str = deepcopy(options)
    if case_sens == False and print_options_lower:
        for i in range(len(options)):
            options_str[i] = options_str[i].lower()

    if print_options:
        choices = f" [{'/'.join(options_str)}]"
    else:
        choices = ""

    result = None
    while True:
        if menu_style:
            print()
            print(menu_title)
            for o in options:
                # option is a spacer
                if o is None or o == "":
                    print()
                    continue

                print(o)

        result = input(f"{msg}{choices}:{default_str} ")

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
                if o is None or o == "":
                    continue

                if not case_sens:
                    o = o.lower()

                if re.match(check, o):
                    if found is not None:
                        print(f"{check} is too ambiguous, try a longer abbreviation")
                        ambiguous = True
                        break

                    found = o

            if not ambiguous and found is not None:
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
        simple_default = "y"

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
            id = create_simple_id(id_list)
            break

        elif simple_id == "n":
            id = str(uuid.uuid4())
            break

    print (f"Id: {id}")
    return id

def create_simple_id(id_list, max_tries=10000):
    i = 0
    while i < max_tries:
        if not i in id_list:
            break;
        i = i + 1

    if i >= max_tries:
        raise ValueError(f"For some reason max tries of {max_tries} was reached...")

    return i

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

