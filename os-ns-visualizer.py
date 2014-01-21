import subprocess
import os
from neutronclient.v2_0.client import Client
import re

def stream_command(command):
	p = subprocess.Popen(command,
	                     stdout=subprocess.PIPE,
	                     stderr=subprocess.STDOUT)
	return iter(p.stdout.readline, b'')

def run_command(command):
	result = []
	for line in stream_command(command):
		result.append(line.replace("\n", ""))
	return result

class NamespaceDriver():

	def __init__(self, ns):
		self.ns = ns

	@classmethod
	def list_namespaces(cls):
		namespaces = run_command(["ip", "netns", "list"])
		return namespaces

	def list_links(self):
		links = run_command(["ip", "netns", "exec", self.ns,"ip","link","list"])
		return links


class IPLink(object):
    
    def __init__(self, name, typ, mac):
        self.name = name
        self.type = typ
        self.mac = mac


class NamespaceMappedResource(object):
	
    def __init__(self, namespace):
        self.namespace = namespace
        self.ns_driver = NamespaceDriver(namespace)
        self.links = self.parse_links()

    def parse_links(self):
        link_regex = re.compile("^([0-9])*:")
        links = []
        # parse command output lines: put relevant links together
        for line in self.ns_driver.list_links():
            line = line.strip()
            if link_regex.match(line):
                curr_link = [line]
                links.append(curr_link)
            else:
                curr_link.append(line)

        # parse command output: parse link lines into attributes
        link_objs = []
        for link in links:
            parts1 = link[0].split(":")
            parts2 = link[1].split(" ")            
            if_name = parts1[1]
            if_type = parts2[0]
            if_mac = parts2[1]
            link_objs.append(IPLink(if_name, if_type, if_mac))

        return link_objs

class Router(NamespaceMappedResource):
	
	def __init__(self, neutron_uuid, namespace, neutron_router):
		super(Router, self).__init__(namespace)
		self.neutron_uuid = neutron_uuid
		self.neutron_router = neutron_router


class Network(NamespaceMappedResource):

	def __init__(self, neutron_uuid, namespace, neutron_network):
		super(Network, self).__init__(namespace)
		self.neutron_uuid = neutron_uuid
		self.neutron_network = neutron_network


if __name__ == "__main__":
	# Get env variables needed to connect to openstack
    try:
	    username = os.environ['OS_USERNAME']
	    password = os.environ['OS_PASSWORD']
	    auth_url = os.environ['OS_AUTH_URL']
	    tenant_name = os.environ['OS_TENANT_NAME']
   

	    neutron_client = Client(username=username, password=password, auth_url=auth_url, tenant_name=tenant_name)

	    neutron_routers = neutron_client.list_routers()
	    neutron_routers = {router['id']: router for router in neutron_routers['routers']}

	    neutron_networks = neutron_client.list_networks()
	    neutron_networks = {network['id']: network for network in neutron_networks['networks']}
	
	    # list over all namespaces and match corresponding openstack resources
	    routers = []
	    networks = [] 
	    for ns in NamespaceDriver.list_namespaces():
		    if ns.startswith("qdhcp-"):
			    network_id = ns.replace("qdhcp-","")
			    neutron_network = neutron_networks[network_id]
			    network = Network(network_id, ns, neutron_network)
			    networks.append(network)

		    elif ns.startswith("qrouter-"):
			    router_id = ns.replace("qrouter-","")
			    neutron_router = neutron_routers[router_id]
			    routers.append(Router(router_id, ns, neutron_router))



	


	    # Print out results
	    print "Networks"
	    for network in networks:
		    print "\t network:%s \t namespace:%s" % (network.neutron_network['name'], network.namespace)
            for link in network.links:
                print "\t \t LINK: %s (TYPE: %s, MAC:%s)" % (link.name, link.type, link.mac)
		
		
	    print "Routers"
	    for router in routers:
		    print "\t router:%s \t namespace:%s" % (router.neutron_router['name'], router.namespace)
            for link in router.links:
                print "\t \t LINK: %s (TYPE: %s, MAC:%s)" % (link.name, link.type, link.mac)

    except KeyError: 
        print "Please define OS_USERNAME, OS_PASSWORD, OS_AUTH_URL and OS_TENANT_NAME"	
		
	


