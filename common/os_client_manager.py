__author__ = 'Joris Roovers'
from shared import print_row
import os
import cinderclient.client
import neutronclient.v2_0.client
import novaclient.client
import keystoneclient.v2_0.client


class OSClientManager(object):
    """
    Class managing different openstack clients.
    Also allows easy initialization based on the commonly used OS_*
    environment variables.
    """

    def __init__(self, username, password, auth_url, tenant_name):
        self.username = username
        self.password = password
        self.auth_url = auth_url
        self.tenant_name = tenant_name
        # clients
        self.identity_client = keystoneclient.v2_0.client.Client(
            username=username, password=password, tenant_name=tenant_name,
            auth_url=auth_url)

        self.volume_client = cinderclient.client.Client('1', username, password,
                                                        tenant_name, auth_url)
        self.network_client = neutronclient.v2_0.client.Client(
            username=username, password=password, tenant_name=tenant_name,
            auth_url=auth_url)

        self.compute_client = novaclient.client.Client('2', username,
                                                       password, tenant_name,
                                                       auth_url)

    @classmethod
    def create_from_env_vars(cls):
        return OSClientManager(*OSClientManager.get_credentials_from_env())


    def _environ(self, key, message):
        try:
            os.environ['OS_USERNAME']
        except KeyError, e:
            print "Please set the %s environment variable." % str(e)
            exit(1)


    @classmethod
    def get_credentials_from_env(cls):
        env_keys = ['OS_USERNAME', 'OS_PASSWORD', 'OS_AUTH_URL',
                    'OS_TENANT_NAME']

        env_values = []
        for key in env_keys:
            value = os.environ.get(key)
            if value:
                env_values.append(value)
            else:
                print "Please set the %s environment variable." % key

        if len(env_values) != len(env_keys):
            exit(1)

        return env_values


    def get_volume_client(self):
        pass



