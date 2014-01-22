import re
from common.os_client_manager import OSClientManager
from jinja2 import Environment, FileSystemLoader
from common.terminal_output import DONE, FAIL
import common.shell_util as sh

import os
import shutil


class NamespaceDriver():
    def __init__(self, ns):
        self.ns = ns

    @classmethod
    def list_namespaces(cls):
        namespaces = sh.run_command(["ip", "netns", "list"])
        return namespaces

    def list_links(self):
        links = sh.run_command(["ip", "netns", "exec", self.ns, "ip", "link",
                                "list"])
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


class DnsmasqProcess(object):
    def __init__(self, pid, args):
        self.pid = pid
        self.args = args

    @classmethod
    def find_on_system(self):
        result = sh.run_command("pgrep -fl dnsmasq")
        processes = []
        for line in result:
            parts = line.split(" ")
            process_id = parts[0]
            process_args = dict()
            for arg in parts:
                # format: --arg_key=arg_val OR --arg_without_val
                if arg.startswith("--"):
                    arg_parts = arg.split("=")
                    # start from 3th char, # remove "--"
                    arg_name = arg_parts[0][2:]
                    arg_val = True
                    if len(arg_parts) > 1:
                        arg_val = arg_parts[1]
                    process_args[arg_name] = arg_val
            processes.append(DnsmasqProcess(process_id, process_args))

        return processes


class Router(NamespaceMappedResource):
    def __init__(self, neutron_uuid, namespace, neutron_router):
        super(Router, self).__init__(namespace)
        self.neutron_uuid = neutron_uuid
        self.neutron_router = neutron_router


class Network(NamespaceMappedResource):
    def __init__(self, neutron_uuid, namespace, neutron_network, dns_process):
        super(Network, self).__init__(namespace)
        self.neutron_uuid = neutron_uuid
        self.neutron_network = neutron_network
        self.dns_process = dns_process


def map_dnsprocess_to_networks():
    """
    Find DNSMasQ processes on this system, filter the ones that correspond
    to neutron networks and create a dict that maps the network id's to the
    corresponsing dnsmasq processes.
    """
    dnsprocesses = DnsmasqProcess.find_on_system()
    dnsprocess_map = dict()
    for process in dnsprocesses:
        pidfile = process.args.get('pid-file')
        if pidfile:
            regex = re.compile("(([0-9a-f]*-?)+)/pid$")
            m = regex.search(pidfile)
            if m:
                network_id = m.group(1)
                dnsprocess_map[network_id] = process
    return dnsprocess_map


def main():
    dns_processes = map_dnsprocess_to_networks()

    mgr = OSClientManager.create_from_env_vars()
    network_client = mgr.network_client

    neutron_routers = network_client.list_routers()
    neutron_routers = {router['id']: router for router in
                       neutron_routers['routers']}

    neutron_networks = network_client.list_networks()
    neutron_networks = {network['id']: network for network in
                        neutron_networks['networks']}


    # TODO change this so that we start from neutron networks and then try
    # to map to namespaces (instead of namespaces to networks).

    # list over all namespaces and match corresponding openstack resources
    routers = []
    networks = []
    for ns in NamespaceDriver.list_namespaces():
        if ns.startswith("qdhcp-"):
            network_id = ns.replace("qdhcp-", "")
            neutron_network = neutron_networks[network_id]
            network = Network(network_id, ns, neutron_network,
                              dns_processes.get(network_id))
            networks.append(network)

        elif ns.startswith("qrouter-"):
            router_id = ns.replace("qrouter-", "")
            neutron_router = neutron_routers[router_id]
            routers.append(Router(router_id, ns, neutron_router))



    # Print out results
    print "Networks"
    for network in networks:
        print "\t network:%s \t namespace:%s" % (
        network.neutron_network['name'], network.namespace)
        for link in network.links:
            print "\t \t LINK: %s (TYPE: %s, MAC:%s)" % (
            link.name, link.type, link.mac)

    print "Routers"
    for router in routers:
        print "\t router:%s \t namespace:%s" % (
        router.neutron_router['name'], router.namespace)
        for link in router.links:
            print "\t \t LINK: %s (TYPE: %s, MAC:%s)" % (
            link.name, link.type, link.mac)


    # Output HTML File
    template_dir = "os_ns_visualizer/templates"
    output_dir = os.path.expanduser("~")
    output_file = os.path.join(output_dir, "result.html")
    css_file = os.path.join(template_dir, "styles.css")

    print "Creating HTML file (%s)..." % output_file,
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('template.html')
    output = template.render(networks=networks, routers=routers)

    f = open(output_file, "w")
    f.write(output)
    f.close()
    shutil.copy(css_file, output_dir)
    print DONE





