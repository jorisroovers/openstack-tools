import os
from common.shared import delete_resource
from common.os_client_manager import OSClientManager
from neutronclient.v2_0.client import Client



#TODO: delete a list of resources


if __name__ == "__main__":


	mgr = OSClientManager.create_from_env_vars()

    neutron_client = mgr.network_client

    print "DETERMINING WHAT SHOULD BE KEPT...",
    all_networks = neutron_client.list_networks()
    skip_network_names = ["public", "private"]
    skip_network_ids = [network["id"] for network in all_networks["networks"] if
                        network["name"] in skip_network_names]

    all_subnets = neutron_client.list_subnets()
    skip_subnet_ids = [subnet["id"] for subnet in all_subnets["subnets"] if
                       subnet["network_id"] in skip_network_ids]
    print "DONE"

    
    print "CLEANING UP FWAAS"
    firewalls = neutron_client.list_firewalls() 
    for firewall in firewalls["firewalls"]:
        print "\tDeleting Firewall %s (%s)..." % (
            firewall["name"], firewall["id"]),
        try:
            neutron_client.delete_firewall(firewall['id'])
            print "DONE"
        except:
            print "FAIL"

    firewall_policies = neutron_client.list_firewall_policies() 
    for firewall_policy in firewall_policies["firewall_policies"]:
        print "\tDeleting Firewall Policy %s (%s)..." % (
            firewall_policy["name"], firewall_policy["id"]),
        try:
            neutron_client.delete_firewall_policy(firewall_policy['id'])
            print "DONE"
        except:
            print "FAIL"

    firewall_rules = neutron_client.list_firewall_rules() 
    for firewall_rule in firewall_rules["firewall_rules"]:
        print "\tDeleting Firewall Rule %s (%s)..." % (
            firewall_rule["name"], firewall_rule["id"]),
        try:
            neutron_client.delete_firewall_rule(firewall_rule['id'])
            print "DONE"
        except:
            print "FAIL"
	

    print "CLEANING UP VPNAAS"

    connections = neutron_client.list_ipsec_site_connections()
    for connection in connections["ipsec_site_connections"]:
        print "\n\tDeleting IPSec Site Connection %s (%s)..." % (
            connection["name"], connection["id"]),
        try:
            neutron_client.delete_ipsec_site_connection(connection["id"])
            print "DONE"
        except:
            print "FAIL"

    vpnservices = neutron_client.list_vpnservices()
    for vpnservice in vpnservices["vpnservices"]:
        print "\n\tDeleting VPN Service %s (%s)..." % (
            vpnservice["name"], vpnservice["id"]),
        try:
            neutron_client.delete_vpnservice(vpnservice["id"])
            print "DONE"
        except:
            print "FAIL"

    ikepolicies = neutron_client.list_ikepolicies()
    for ikepolicy in ikepolicies["ikepolicies"]:
        delete_resource(neutron_client, "ikepolicy", ikepolicy)

    print "CLEANING UP PORTS"
    ports = neutron_client.list_ports()
    for port in ports["ports"]:
        if port["network_id"] in skip_network_ids:
            print "\tKeeping Port %s (%s)." % (
                port["name"], port["id"])
        else:
            print "\tDeleting Port %s (%s)..." % (
                port["name"], port["id"]),

            if port['device_owner'] == "network:router_interface":
                print "\n\t\tPort belongs to router, deleting router " \
                      "interface first"
                try:
                    neutron_client.remove_interface_router(port["device_id"],
                        {"port_id": port["id"]})
                    print "DONE"
                    print "\n\t\t Now removing port..."
                except:
                    print "FAIL"
            try:
                neutron_client.delete_port(port["id"])
                print "DONE"
            except:
                print "FAIL"

    print "\n"
    print "CLEANING UP ROUTERS",
    routers = neutron_client.list_routers()
    for router in routers["routers"]:
        external_gw_info = router["external_gateway_info"]
        if external_gw_info:
            if external_gw_info["network_id"] in skip_network_ids and \
                    "tempest" not in  router['name']:
                print "\n\tKeeping Router %s (%s)." % (
                    router["name"], router["id"]),
                continue

        print "\n\tDeleting Router %s (%s)..." % (
            router["name"], router["id"]),
        print router
        try:
            neutron_client.delete_router(router["id"])
            print "DONE"
        except:
            print "FAIL"

    print "\n"
    print "CLEANING UP NETWORKS",

    networks = [network for network in all_networks["networks"] if network[
                                                                       "name"] not in skip_network_names]
    for network in networks:
        print "Deleting network %s (%s)" % (network["name"], network["id"]),
        subnets = network["subnets"]
        if len(subnets) > 0:
            for subnet_id in subnets:
                subnet = neutron_client.show_subnet(subnet_id)
                subnet = subnet["subnet"]
                try:
                    neutron_client.delete_subnet(subnet["id"])
                    print "OK"
                except:
                    print "FAIL"
        else:
            neutron_client.delete_network(network["id"])
        print "OK"

    print "*" * 20
    print "Remaining networks:"
    networks = neutron_client.list_networks()
    for network in networks["networks"]:
        print "%s (%s)" % (network["name"], network["id"])

