"""
TODO add docstring
"""

import sys
import json
import requests


class MigrationFactory:
    """
    Migration Factory base class to take care of login functionality.
    """

    def __init__(self, username, password, login_host):
        __token = self.login(username, password, login_host).strip('\"')
        self.headers = {'Authorization': __token}

    def login(self, username, password, login_host):
        login_data = {'username': username, 'password': password}
        r = requests.post(login_host + '/prod/login',
                          data=json.dumps(login_data))
        if r.status_code == 200:
            print("Migration Factory : You have successfully logged in")
            print("")
            token = str(json.loads(r.text))
            return token
        if r.status_code == 502:
            print("ERROR: Incorrect username or password....")
            sys.exit(1)
        else:
            print(r.text)
            sys.exit(2)


class MigrationFactoryUser(MigrationFactory):
    """
    Migration Factory User class to take care of user functionality.

    TODO add comments
    """
    def __init__(self, username, password, login_host, user_host,
                 stage='prod'):
        super().__init__(username, password, login_host)
        self.user_host = user_host
        self.stage = stage

    def get_wave_ids(self):
        user_endpoint = self.user_host + f'/{self.stage}/user/waves'

        r = requests.get(url=user_endpoint, headers=self.headers)

        return [wave['wave_id'] for wave in r.json()]

    def get_app_ids(self):
        user_endpoint = self.user_host + f'/{self.stage}/user/apps'

        r = requests.get(url=user_endpoint, headers=self.headers)

        return [app['app_id'] for app in r.json()]

    def get_server_ids(self):
        user_endpoint = self.user_host + f'/{self.stage}/user/servers'

        r = requests.get(url=user_endpoint, headers=self.headers)

        return [server['server_id'] for server in r.json()]

    def delete_wave(self, wave_id):
        user_endpoint = self.user_host \
            + f'/{self.stage}/user/waves/{wave_id}'

        r = requests.delete(url=user_endpoint, headers=self.headers)

        return r

    def delete_app(self, app_id):
        user_endpoint = self.user_host \
            + f'/{self.stage}/user/apps/{app_id}'

        r = requests.delete(url=user_endpoint, headers=self.headers)

        return r

    def delete_server(self, server_id):
        user_endpoint = self.user_host \
            + f'/{self.stage}/user/servers/{server_id}'

        r = requests.delete(url=user_endpoint, headers=self.headers)

        return r

    def delete_waves(self):
        wave_ids = self.get_wave_ids()

        for wave_id in wave_ids:
            response = self.delete_wave(wave_id)
            if response.status_code == 200:
                print(f'Successfully deleted wave id: {wave_id}...')

    def delete_apps(self):
        app_ids = self.get_app_ids()

        for app_id in app_ids:
            response = self.delete_app(app_id)
            if response.status_code == 200:
                print(f'Successfully deleted app id: {app_id}...')

    def delete_servers(self):
        server_ids = self.get_server_ids()

        for server_id in server_ids:
            response = self.delete_server(server_id)
            if response.status_code == 200:
                print(f'Successfully deleted server id {server_id}...')
