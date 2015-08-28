__author__ = 'xb'

import sys

from clint.textui import colored, prompt, puts

from onedrive_d.common import logger_factory
from onedrive_d.common import netman

logger = logger_factory.get_logger('PrefMain')
network_monitor = netman.NetworkMonitor()


def bye():
    puts(colored.green('Bye.'))
    sys.exit(0)


def prompt_task():
    title = 'onedrive-d Preference Wizard'
    puts(colored.green('=' * len(title)))
    puts(colored.green(title))
    puts(colored.green('=' * len(title)))
    option_descriptions = [
        'Connect a new OneDrive Personal Account',  # 0
        'Connect a new OneDrive for Business Account',  # 1
        'View / Edit / Delete connected OneDrive accounts',  # 2
        'Add a new remote Drive',  # 3
        'View / Edit / Delete existing Drives',  # 4
        'Edit user configurations',  # 5
        'Edit default ignore list',  # 6
        'Exit wizard'  # 7
    ]
    options = [{'selector': str(i), 'prompt': option_descriptions[i], 'return': i}
               for i in range(0, len(option_descriptions))]
    task = prompt.options('Please select a task by typing the index number followed by [ENTER]:', options)
    print(task)
    if task == len(option_descriptions) - 1:
        bye()


def main():
    network_monitor.start()
    prompt_task()


if __name__ == '__main__':
    main()
