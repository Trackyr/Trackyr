#!/usr/bin/env python3

# utility to add, delete cron entries

import os
import argparse
import lib.utils.logger as log
from crontab import CronTab

pyfile = "main.py"
path = os.path.dirname(os.path.abspath(__file__ + "/../..")) + "/" + pyfile

def print_path():
    print(path)

def get_cron_line(time, unit):
    cron_time = convert(time, unit)
    return f'{cron_time} {path} -c {time} {unit}'

def get_cron_command(time, unit):
    cron_command = convert(time, unit)
    return f'{path} -c {time} {unit}'

def exists(time, unit):
    cron = CronTab(user=True)
    cron_time = convert(time, unit)
    iter = cron.find_time(cron_time)
    for x in iter:
        return True

def clear():
    cron = CronTab(user=True)
    log.debug("Clearing crontab...")
    cron.remove_all()
    cron.write()

def add(time, unit):
    cron = CronTab(user=True)
    if exists(time, unit):
        log.debug(f"Skipping add cron. Cron entry: '{time}, {unit}' already exists")
        return

    cron_string = get_cron_line(time, unit)
    cron_time = convert(time, unit)
    job = cron.new(command=get_cron_command(time, unit))
    job.setall(cron_time)
    cron.write()
    log.debug(f"Added to cron: {cron_string}")

def delete(time, unit):
    cron = CronTab(user=True)
    if not exists(time, unit):
        print (f"Cannot delete. Cron entry: '{time}, {unit}' doesnt exist")
        return

    cron_time = convert(time, unit)
    cron_string = get_cron_line(time, unit)
    cron_string = cron_string.replace("*",  "[*]")
    iter = cron.find_time(cron_time)
    for job in iter:
        cron.remove(job)
    cron.write()
    log.debug(f"Deleted from cron: {cron_string}")

def convert(time, unit):
    if unit[:1] == "m":
        if time > 59 or time < 1:
            return None

        return f"*/{time} * * * *"

    if unit[:1] == "h":
        if time > 23 or time < 1:
            return None

        return f"0 */{time} * * *"

    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--add", nargs=2)
    parser.add_argument("-d", "--delete", nargs=2)
    parser.add_argument("-c", "--convert", nargs=2)
    parser.add_argument("-l", "--list", action="store_true")

    args = parser.parse_args()

    if args.add:
        add(int(args.add[0]), args.add[1])
    elif args.delete:
        delete(int(args.delete[0]), args.delete[1])

    if args.convert:
        print(convert(int(args.convert[0]), args.convert[1]))

    if args.list:
        os.system(f"crontab -l | grep -v '#' | grep {path}")


if __name__ == "__main__":
    main()
    print(path)
