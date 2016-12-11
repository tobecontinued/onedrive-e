from onedrivee.common.user_config import UserConfig


def save_user_config(path, user_conf):
    with open(path, 'w') as f:
        f.write(user_conf.dump())


def load_user_config(path):
    with open(path, 'r') as f:
        return UserConfig.load(f.read())
