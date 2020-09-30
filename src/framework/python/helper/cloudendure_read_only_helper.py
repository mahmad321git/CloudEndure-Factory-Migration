"""
TODO add docstring
"""
import json
import requests
from contextlib import suppress


class CloudEndure:
    """
    Base class to simplify CloudEndure API calls.

    To login, either provide CloudEndure API token or username and password.

    Args:
        ce_api_token (str): CloudEndure token.
        username     (str): CloudEndure username.
        password     (str): CloudEndure password.
    """

    def __init__(self, **args):
        self.set_ce_api_url()

        if 'ce_api_token' in args:
            self.api_login(args['ce_api_token'])
        elif 'username' in args and 'password' in args:
            self.user_login(args['username'], args['password'])
        else:
            print('Note: Use api_login or user_login to login.')

    def set_ce_api_url(self):
        self.HOST = 'https://console.cloudendure.com'
        self.headers = {'Content-Type': 'application/json'}
        self.session = {}
        self.endpoint = '/api/latest/{}'

    def api_login(self, ce_api_token):
        """
        TODO docstring

        Args:
            ce_api_token (str): CloudEndure API Token
        """
        login_data = {'userApiToken': ce_api_token}
        r = requests.post(self.HOST + self.endpoint.format('login'),
                          data=json.dumps(login_data), headers=self.headers)
        if r.status_code == 200:
            print("CloudEndure : You have successfully logged in")
            print("")
        if r.status_code != 200 and r.status_code != 307:
            if r.status_code == 401 or r.status_code == 403:
                print('ERROR: The CloudEndure login credentials provided cannot'
                      ' be authenticated....')
            elif r.status_code == 402:
                print('ERROR: There is no active license configured for this '
                      'CloudEndure account....')
            elif r.status_code == 429:
                print('ERROR: CloudEndure Authentication failure limit has been'
                      ' reached. The service will become available for'
                      ' additional requests after a timeout....')

        # check if need to use a different API entry point
        if r.history:
            endpoint = '/' + '/'.join(r.url.split('/')[3:-1]) + '/{}'
            r = requests.post(self.HOST + endpoint.format('login'),
                              data=json.dumps(login_data), headers=self.headers)

        self.session['session'] = r.cookies['session']

        with suppress(Exception):
            self.headers['X-XSRF-TOKEN'] = r.cookies['XSRF-TOKEN']

    def user_login(self, username, password):
        """
        TODO docstring

        Args:
            ce_api_token (str): CloudEndure API Token
        """
        print('To be implemented...')

    def get_projects(self):
        r = requests.get(self.HOST + self.endpoint.format('projects'),
                         headers=self.headers, cookies=self.session)

        return r.json()['items']

    def get_project_by_name(self, project_name):
        projects = self.get_projects()

        for project in projects:
            if project['name'] == self.project_name:
                return project

        return None

    def get_replication_configuration_by_id(self, project_id):
        url_path = '/'.join(['projects', project_id,
                             'replicationConfigurations'])
        r = requests.get(self.HOST + self.endpoint.format(url_path),
                         headers=self.headers, cookies=self.session)

        return r.json()['items'][0]

    def get_project_region(self, cloud_credentials, region_id):
        url_path = '/'.join(['cloudCredentials', cloud_credentials,
                             'regions'])
        r = requests.get(self.HOST + self.endpoint.format(url_path),
                         headers=self.headers, cookies=self.session)

        regions = r.json()['items']

        for region in regions:
            if region['id'] == region_id:
                return region

        return None

    def resolve_region_name(self, region_name):
        region_code = None

        if "Northern Virginia" in region_name:
            region_code = 'us-east-1'
        elif "Frankfurt" in region_name:
            region_code = 'eu-central-1'
        elif "Paris" in region_name:
            region_code = 'eu-west-3'
        elif "Stockholm" in region_name:
            region_code = 'eu-north-1'
        elif "Northern California" in region_name:
            region_code = 'us-west-1'
        elif "Oregon" in region_name:
            region_code = 'us-west-2'
        elif "AWS GovCloud (US)" in region_name:
            region_code = 'us-gov-west-1'
        elif "Bahrain" in region_name:
            region_code = 'me-south-1'
        elif "Hong Kong" in region_name:
            region_code = 'ap-east-1'
        elif "Tokyo" in region_name:
            region_code = 'ap-northeast-1'
        elif "Singapore" in region_name:
            region_code = 'ap-southeast-1'
        elif "AWS GovCloud (US-East)" in region_name:
            region_code = 'us-gov-east-1'
        elif "Mumbai" in region_name:
            region_code = 'ap-south-1'
        elif "South America" in region_name:
            region_code = 'sa-east-1'
        elif "Sydney" in region_name:
            region_code = 'ap-southeast-2'
        elif "London" in region_name:
            region_code = 'eu-west-2'
        elif "Central" in region_name:
            region_code = 'ca-central-1'
        elif "Ireland" in region_name:
            region_code = 'eu-west-1'
        elif "Seoul" in region_name:
            region_code = 'ap-northeast-2'
        elif "Ohio" in region_name:
            region_code = 'us-east-2'
        else:
            print("Incorrect Region Name")

        return region_code


class CloudEndureProject(CloudEndure):
    """
    Wrapper class to simplify CloudEndure Project API calls.

    To login, either provide CloudEndure API token or username and password.

    Args:
        project_name (str): CloudEndure project name
        ce_api_token (str): CloudEndure token.
        username     (str): CloudEndure username.
        password     (str): CloudEndure password.
    """

    def __init__(self, **args):
        super().__init__(**args)
        self.project_name = args['project_name']
        print('Fetching project...')
        self.project = self.get_project_by_name(self.project_name)
        print('Fetching project replication configuration...')
        self.replication_configurations = self \
            .get_replication_configuration_by_id(self.project['id'])

        print('Fetching project target region...')
        for cloud_credential in self.project['cloudCredentialsIDs']:
            target_region = self \
                .get_project_region(cloud_credential,
                                    self.replication_configurations['region'])

            if target_region:
                self.target_region = target_region
                self.target_region_name = self.resolve_region_name(
                    self.target_region['name'])
                break
