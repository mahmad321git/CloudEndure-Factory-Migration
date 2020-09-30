from helper import json_helper
from helper import parameter_parsing_helper
from helper.migration_factory import MigrationFactoryUser

if __name__ == '__main__':
    # Reading configs.
    config = json_helper.parse('config\\config.json')

    # Parameter Store structure
    project_env = '/'.join(['', config['PROJECT'], config['ENV']])

    # Fetching login credentials from AWS Parameter Store.
    factory_username = '/'.join([project_env, 'factory', 'username'])
    factory_password = '/'.join([project_env, 'factory', 'password'])
    username = parameter_parsing_helper \
        .fetch_parameter(factory_username)
    password = parameter_parsing_helper \
        .fetch_parameter(factory_password)

    login_endpoint = '/'.join([project_env, 'endpoint', 'login'])
    user_endpoint = '/'.join([project_env, 'endpoint', 'user'])
    login_host = parameter_parsing_helper \
        .fetch_parameter(login_endpoint)
    user_host = parameter_parsing_helper \
        .fetch_parameter(user_endpoint)

    # Initiating Migration Factory User.
    mfu = MigrationFactoryUser(
        username, password, login_host, user_host)

    print('Deleting waves...')
    mfu.delete_waves()

    print('Deleting apps...')
    mfu.delete_apps()

    print('Deleting servers...')
    mfu.delete_servers()
