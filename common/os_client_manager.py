__author__ = 'Joris Roovers'
from shared import print_row
import os
import cinderclient.client
import neutronclient.v2_0.client


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
        self.volume_client = cinderclient.client.Client('1', username, password,
                                                        tenant_name, auth_url)
        self.network_client = neutronclient.v2_0.client.Client(
            username=username, password=password, tenant_name=tenant_name,
            auth_url=auth_url)

    @classmethod
    def create_from_env_vars(cls):
        return OSClientManager(*OSClientManager.get_credentials_from_env())

    @classmethod
    def get_credentials_from_env(cls):
        try:
            username = os.environ['OS_USERNAME']
            password = os.environ['OS_PASSWORD']
            auth_url = os.environ['OS_AUTH_URL']
            tenant_name = os.environ['OS_TENANT_NAME']

            print_row(("Username", username))
            print_row(("Password", password))
            print_row(("Auth URL", auth_url))
            print_row(("Tenant Name", tenant_name))

            return username, password, auth_url, tenant_name

        except KeyError, e:
            print "Please set the %s environment variable." % str(e)
            exit(1)


    def get_volume_client(self):
        pass



