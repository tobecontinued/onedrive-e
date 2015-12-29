__author__ = 'xb'

import os
import sys

from clint.textui import colored, columns, indent, prompt, puts, validators

from onedrive_d import OS_USER_NAME, OS_USER_HOME, mkdir, get_content
from onedrive_d.api import accounts, clients
from onedrive_d.cli import CONFIG_DIR, get_current_user_config
from onedrive_d.common import drive_config, netman
from onedrive_d.store import account_db, drives_db
from onedrive_d.vendor.utils import pretty_print_bytes

try:
    if not os.path.exists(CONFIG_DIR):
        mkdir(CONFIG_DIR)
        default_ignore_list_data = get_content('default_ignore_list.txt', is_text=True)
        with open(CONFIG_DIR + '/odignore.txt', 'w') as f:
            f.write(default_ignore_list_data)
        print(colored.green('Created path "' + CONFIG_DIR + '".'))
    user_conf = get_current_user_config()
    network_monitor = netman.NetworkMonitor()
    personal_client = clients.PersonalClient(proxies=user_conf.proxies, net_monitor=network_monitor)
    business_client = None
    account_store = account_db.AccountStorage(
        CONFIG_DIR + '/accounts.db', personal_client=personal_client, business_client=business_client)
    drive_store = drives_db.DriveStorage(CONFIG_DIR + '/drives.db', account_store)
except Exception as e:
    print(colored.red('Fatal error: ' + str(e)))
    sys.exit(1)


def add_personal_account():
    puts(colored.green('Link with an OneDrive Personal account:'))
    puts(colored.cyan(
        'Please use your browser to visit the following URL, sign in with your OneDrive account and '
        'authorize onedrive-d, then copy the callback URL back here. The callback URL is the URL at '
        'which the authorization page goes blank and usually starts with ' +
        clients.PersonalClient.DEFAULT_REDIRECT_URI + '.'))
    puts()
    puts(colored.yellow('Please visit this URL: '))
    puts(personal_client.get_auth_uri())
    while True:
        try:
            url = prompt.query(str(colored.yellow('\nPlease paste the callback URL or hit [Ctrl+C] to abort:')))
            account = accounts.get_personal_account(personal_client, uri=url)
            profile = account.profile
            account_store.add_account(account)
            puts(colored.green('Success: added account {} ({}).'.format(profile.user_id, profile.name)))
            return
        except KeyboardInterrupt:
            puts(colored.red('Aborted.'))
            return
        except Exception as e:
            puts(colored.red('Error: ' + str(e)))


def add_business_account():
    puts(colored.yellow('OneDrive for Business is not yet supported.'))


def prompt_delete_account(account_list):
    while True:
        id_to_delete = prompt.query('Type the index of the account to delete: ',
                                    validators=[validators.IntegerValidator(),
                                                validators.OptionValidator(range(len(account_list)))])
        account_to_delete = account_list[id_to_delete]
        if account_to_delete is None:
            puts(colored.red('Error: The account has been deleted.'))
        else:
            account_store.delete_account(account_to_delete)
            account_list[id_to_delete] = None


def list_existing_accounts():
    col = 30
    all_accounts = account_store.get_all_accounts()
    if len(all_accounts) == 0:
        puts(colored.red('There is no linked account yet.'))
        return
    puts(colored.green('You have linked the following account(s) to onedrive-d:\n'))
    puts(columns(
        [(colored.red('Index')), 20],
        [(colored.magenta('Account ID')), col],
        [(colored.cyan('Account Type')), col],
        [(colored.green('Name')), None]))
    account_list = []
    for id, account in all_accounts.items():
        puts(columns(
            [str(len(account_list)), 20],
            [account.profile.user_id, col],
            [account.TYPE, col],
            [account.profile.name, None]))
        account_list.append(account)
    puts(colored.yellow('\nTo delete an account, type the index and hit [Enter]. Otherwise hit [Ctrl+C] to break.'))
    puts(colored.yellow('Note: all the Drives belong to the account will also be deleted.'))
    puts()
    try:
        prompt_delete_account(account_list)
    except KeyboardInterrupt:
        puts(colored.green('Aborted.'))


def prompt_drive_config(drive):
    if hasattr(drive, 'config'):
        drive_config_data = drive.config.data
    else:
        drive_config_data = drive_config.DriveConfig.DEFAULT_VALUES
    if drive_config_data['local_root'] is None or drive_config_data['local_root'] == '':
        drive_config_data['local_root'] = OS_USER_HOME + '/OneDrive/' + drive.drive_id
    puts(colored.green('You selected Drive "%s"...' % drive.drive_id))

    puts()
    with indent(4, quote=' >'):
        puts('When specifying local root, pick a directory not used by or under any other Drive.')
        puts('When specifying HTTPS download / upload sizes, note that files larger than those sizes will be handled '
             'as chunks.')
    puts()

    while True:
        local_root = prompt.query('Which local directory do you want to sync with this Drive?',
                                  default=drive_config_data['local_root'])
        try:
            if not os.path.exists(local_root):
                puts(colored.yellow('Directory "%s" does not exist. Try creating it...' % local_root))
                mkdir(local_root)
                puts(colored.green('Successfully created directory "%s".' % local_root))
            elif os.path.isfile(local_root):
                raise ValueError('Path "%s" is a file.' % local_root)
            if os.path.isdir(local_root):
                drive_config_data['local_root'] = local_root
                break
            raise ValueError('Invalid path "%s"' % local_root)
        except Exception as e:
            puts(colored.red('Error: ' + str(e)))
    drive_config_data['max_get_size_bytes'] = prompt.query('Maximum size, in KB, for a single download request?',
                                                           default=str(drive_config_data['max_get_size_bytes'] >> 10),
                                                           validators=[validators.IntegerValidator()]) * 1024
    drive_config_data['max_put_size_bytes'] = prompt.query('Maximum size, in KB, for a single upload request?',
                                                           default=str(drive_config_data['max_put_size_bytes'] >> 10),
                                                           validators=[validators.IntegerValidator()]) * 1024
    try:
        while not prompt.yn('Do you have ignore list files specific to this Drive to add?', default='n'):
            ignore_file_path = prompt.query('Path to the ignore list file (hit [Ctrl+C] to skip): ',
                                            validators=[validators.FileValidator()])
            drive_config_data['ignore_files'].add(ignore_file_path)
            puts(colored.green('Recorded ignore list file: "{}"' % ignore_file_path))
    except KeyboardInterrupt:
        pass
    drive_conf = drive_config.DriveConfig.load(drive_config_data)
    drive.config = drive_conf
    drive_store.add_record(drive)


def prompt_add_drive(drive_list):
    while True:
        puts()
        id_to_add = prompt.query('Type the index of the Drive to add: ',
                                 validators=[validators.IntegerValidator(),
                                             validators.OptionValidator(range(len(drive_list)))])
        drive_to_add = drive_list[id_to_add]
        if drive_to_add is None:
            puts(colored.red('Error: The Drive has been added.'))
        else:
            prompt_drive_config(drive_to_add)
            drive_list[id_to_add] = None
            puts(colored.green('Successfully added Drive.'))
            puts()


def add_new_drive():
    puts(colored.green('Here are all the Drives belong to the accounts you have linked and not yet added:\n'))
    drive_list = []
    for key, account in account_store.get_all_accounts().items():
        account_id, account_type = key
        puts(colored.magenta('{} Account "{}" ({})'.format(account_type.upper(), account_id, account.profile.name)))
        drive_root = drive_store.get_drive_root(account_id, account_type)
        all_drives = drive_root.get_all_drives()
        saved_drives = drive_store.get_all_drives()
        with indent(4):
            puts(columns(
                [(colored.green('Index')), 10],
                [(colored.cyan('Drive ID')), 20],
                [(colored.cyan('Type')), 10],
                [(colored.cyan('Default?')), 10],
                [(colored.cyan('State')), 10],
                [(colored.yellow('Total')), 10],
                [(colored.yellow('Used')), 10],
                [(colored.yellow('Free')), 10]))
            for id, drive in all_drives.items():
                if drive_store.get_key(id, drive.root.account.profile.user_id, drive.root.account.TYPE) in saved_drives:
                    continue
                quota = drive.quota
                puts(columns(
                    [str(len(drive_list)), 10],
                    [id, 20],
                    [drive.type, 10],
                    ['Yes' if drive.is_default else '', 10],
                    [quota.state, 10],
                    [pretty_print_bytes(quota.total), 10],
                    [pretty_print_bytes(quota.used), 10],
                    [pretty_print_bytes(quota.remaining), 10]))
                drive_list.append(drive)
    if len(drive_list) == 0:
        puts()
        puts(colored.red('It seems there is no more Drive to add.'))
    else:
        try:
            prompt_add_drive(drive_list)
        except KeyboardInterrupt:
            puts(colored.green('Aborted.'))


def prompt_edit_drive(drive_list):
    try:
        while True:
            puts()
            target_id = prompt.query('Please enter command: ', validators=[validators.RegexValidator('-?[0-9]+')])
            try:
                if target_id[0] == '-':
                    target_id = int(target_id[1:])
                    drive = drive_list[target_id]
                    if drive is None:
                        raise ValueError('the Drive has been deleted.')
                    drive_store.delete_record(drive)
                    drive_list[target_id] = None
                    puts(colored.green('Successfully deleted Drive "%s"' % drive.drive_id))
                else:
                    target_id = int(target_id)
                    drive = drive_list[target_id]
                    if drive is None:
                        raise ValueError('the Drive has been deleted.')
                    prompt_drive_config(drive)
                    drive_store.add_record(drive)
                    puts(colored.green('Successfully edited Drive "%s"' % drive.drive_id))
            except ValueError as e:
                puts(colored.red('Error: ' + str(e)))
    except KeyboardInterrupt:
        puts(colored.green('Aborted.'))


def list_existing_drives():
    puts(colored.green('List registered Drives for editing / deleting...\n'))

    with indent(4, quote=' >'):
        puts('To edit a Drive, type the index of the Drive in the table.')
        puts('To delete a Drive, type a minus sign followed by the index of the Drive.')
        puts('To abort and return to main menu, hit [Ctrl+C].')
        puts('For example, type "1" to edit the Drive indexed 1, and type "-1" to delete it.')
    puts()

    account_store.get_all_accounts()
    drive_list = []
    for key, drive in drive_store.get_all_drives().items():
        drive_id, account_id, account_type = key
        with indent(4):
            puts(columns(
                [(colored.green('Index')), 8],
                [(colored.magenta('Drive ID')), 17],
                [(colored.magenta('Drive Type')), 12],
                [(colored.cyan('Account')), 20],
                [(colored.yellow('Local Root')), None]))
            profile = drive.root.account.profile
            puts(columns(
                [str(len(drive_list)), 8],
                [drive_id, 17],
                [drive.type, 12],
                ["{} ({})".format(account_id, profile.name), 20],
                [drive.config.local_root, None]))
        drive_list.append(drive)
    prompt_edit_drive(drive_list)


def print_existing_ignore_list_paths():
    puts()
    puts('Currently effective global ignore list files:')
    i = 0
    path_list = []
    if len(user_conf.default_drive_config.ignore_files) == 0:
        puts(colored.red('There is no ignore list file effective globally.'))
    else:
        for p in user_conf.default_drive_config.ignore_files:
            puts('  ' + colored.cyan('[%d]\t' % i) + p)
            path_list.append(p)
    puts()
    return path_list


def edit_default_ignore_list():
    puts(colored.green('Editing global ignore list files...\n'))

    default_path = CONFIG_DIR + '/odignore.txt'
    if os.path.isfile(default_path) and default_path not in user_conf.default_drive_config.ignore_files:
        puts(colored.yellow('Found default ignore list file "%s".' % default_path))
        if prompt.yn('Do you want to add this ignore list? '):
            user_conf.default_drive_config.ignore_files.add(default_path)

    with indent(4, quote=' >'):
        puts('To add a new ignore list file that is effective on all Drives, type the file path below.')
        puts('To remove an existing ignore list file, type a minus sign followed by the index of the path to delete.')
        puts('For example, type "-1" to delete the path indexed 1.')
        puts('To abort and return to main menu, hit [Ctrl+C].')

    try:
        while True:
            path_list = print_existing_ignore_list_paths()
            command = prompt.query('Please specify an absolute path or give a negated index: ')
            try:
                if len(command) > 0 and command[0] == '-':
                    index_to_delete = int(command[1:])
                    if index_to_delete < 0 or index_to_delete > len(path_list):
                        raise ValueError('Invalid path index "%d"' % index_to_delete)
                    path_to_delete = path_list[index_to_delete]
                    user_conf.default_drive_config.ignore_files.remove(path_to_delete)
                    puts(colored.green('Deleted path "%s" from list.' % path_to_delete))
                elif os.path.isfile(command):
                    user_conf.default_drive_config.ignore_files.add(command)
                    puts(colored.green('Added path "%s" to list.' % command))
                else:
                    raise ValueError('Path "%s" is not a file.' % command)
            except ValueError as e:
                puts(colored.red('Error: ' + str(e)))
    except KeyboardInterrupt:
        puts(colored.green('Aborted.'))


def prompt_new_proxy():
    try:
        new_proxy = prompt.query('New proxy: ', default='None')
        if new_proxy != 'None':
            if user_conf.proxies is None:
                user_conf.proxies = {'https': new_proxy}
            else:
                user_conf.proxies['https'] = new_proxy
            msg = 'Saved new proxy address "%s"' % new_proxy
        else:
            user_conf.proxies = None
            msg = 'Deleted current proxy.'
        puts(colored.green(msg))
    except KeyboardInterrupt:
        puts(colored.green('Aborted.'))


def edit_proxies():
    puts(colored.green('Editing HTTPS proxy...\n'))

    with indent(4, quote=' >'):
        puts('Please specify new proxy in the format of ' +
             colored.yellow('user') + colored.red(':pass') + colored.cyan('@') +
             colored.green('host') + colored.magenta(':port'))
        puts('For example, "me:123@proxy.com:8080", or "127.0.0.1:8888".')
        puts('Enter "None" to delete current proxy.')
        puts('Hit [Ctrl+C] to abort and return to main menu.')
    puts()

    if user_conf.proxies is None or 'https' not in user_conf.proxies:
        current_proxy_str = 'None'
    else:
        current_proxy_str = user_conf.proxies['https']
    puts(colored.cyan('Current proxy: ') + current_proxy_str)
    puts()
    prompt_new_proxy()


def edit_sync_params():
    puts(colored.green('Editing synchronization workload parameters...\n'))
    user_conf.num_consumers = prompt.query('Number of worker threads: ',
                                           default=str(user_conf.num_consumers),
                                           validators=[validators.IntegerValidator()])
    user_conf.deep_sync_interval_seconds = prompt.query('Number of seconds to wait before next full scan: ',
                                                        default=str(user_conf.deep_sync_interval_seconds),
                                                        validators=[validators.IntegerValidator()])
    puts()
    puts(colored.green('Workload parameters saved.'))


def bye():
    puts(colored.green('Bye.'))
    sys.exit(0)


def dispatch_task():
    puts('\n' + colored.blue('-' * 80) + '\n')
    puts(colored.green('Preference wizard supports the following tasks:\n', bold=True))
    option_descriptions = [
        'Connect a new OneDrive Personal Account',  # 0
        'Connect a new OneDrive for Business Account',  # 1
        'View / Delete connected OneDrive accounts',  # 2
        'Add a remote Drive to sync',  # 3
        'View / Edit / Delete existing Drives',  # 4
        'Edit global ignore list files',  # 5
        'Edit HTTPS proxies',  # 6
        'Configure synchronization workload (resync interval, etc.)',  # 7
        'Exit wizard'  # 8
    ]
    for i in range(0, len(option_descriptions)):
        puts('[{}] {}'.format(i, option_descriptions[i]))
    puts()
    task_id = prompt.query('Please enter the task index and hit [ENTER]: ',
                           validators=[
                               validators.IntegerValidator(),
                               validators.OptionValidator(range(len(option_descriptions)))])
    tasks = [
        add_personal_account,
        add_business_account,
        list_existing_accounts,
        add_new_drive,
        list_existing_drives,
        edit_default_ignore_list,
        edit_proxies,
        edit_sync_params,
        bye
    ]
    if task_id < len(option_descriptions) - 1:
        puts('\n' + colored.blue('-' * 80) + '\n')
    tasks[task_id]()


def print_system_info():
    puts(colored.green('\nSystem Information'))
    items = {
        'User name': OS_USER_NAME,
        'Configuration path': CONFIG_DIR,
    }
    for k, v in items.items():
        puts(columns([k, 30], [v, None]))


def prompt_task():
    title = '=' + ' ' * 10 + 'onedrive-d Preference Wizard' + ' ' * 10 + '='
    puts(colored.cyan('=' * len(title)))
    puts(colored.cyan(title))
    puts(colored.cyan('=' * len(title)))
    print_system_info()
    while True:
        dispatch_task()


def main():
    network_monitor.start()
    try:
        prompt_task()
    except (KeyboardInterrupt, EOFError):
        bye()


if __name__ == '__main__':
    main()
