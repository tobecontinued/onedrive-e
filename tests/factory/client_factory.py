from onedrived.api import clients


def get_sample_personal_client():
    return clients.PersonalClient('dummy_client_id', 'dummy_secret')
