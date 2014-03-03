from common.os_client_manager import OSClientManager
from common.shared import OperationList


class TempestCleaner:
    pass
    # TODO implement


def _find_by_id(objs, id):
    obj = [obj for obj in objs if obj.id == id]
    if len(obj) > 0:
        return obj[0]
    return None


def main():
    tempest_tenant_names = ["Tempest", "Tempest2"]

    print "[INIT]"
    print "Initializing openstack clients...",
    mgr = OSClientManager.create_from_env_vars()
    print "DONE"

    print "Fetching Tenants...",
    tenants = mgr.identity_client.tenants.list()
    tenant_ids = [tenant.id for tenant in tenants]
    temptest_tenant_ids = [tenant.id for tenant in tenants
                           if tenant.name in tempest_tenant_names]

    print "DONE"

    print "Fetching Users...",
    users = mgr.identity_client.users.list()
    print "DONE"

    print "[CLEANING UP INSTANCES]"
    print "Fetching instances...",
    instances = mgr.compute_client.servers.list(True, {"all_tenants": "1"})
    print "DONE"
    operation_list = OperationList()
    for instance in instances:
        tenant_id = instance.tenant_id
        if (tenant_id not in tenant_ids) or (tenant_id in temptest_tenant_ids):
            tenant = _find_by_id(tenants, instance.tenant_id)
            user = _find_by_id(users, instance.user_id)
            tenant_name = "N/A" if tenant == None else tenant.name
            user_name = "N/A" if user == None else user.name

            operation_list.add_operation(
                "Delete %s (Tenant:%s, User: %s)" % (instance.name,
                                                     tenant_name,
                                                     user_name), instance
                .delete)

    operation_list.confirm_and_execute()


    print "[CLEANING UP VOLUMES]"

    print "Fetching volumes...",
    volumes = mgr.volume_client.volumes.findall()
    print "DONE"

    print "Cleaning up Tempest volumes"

    operation_list = OperationList()

    for volume in volumes:
        tenant_id = getattr(volume, 'os-vol-tenant-attr:tenant_id')
        #user_id =
        if (tenant_id not in tenant_ids) or (tenant_id in temptest_tenant_ids):
            tenant = _find_by_id(tenants, tenant_id)
            tenant_name = "N/A" if tenant == None else tenant.name
            operation_list.add_operation("Delete %s (tenant:%s)" % (
                volume.display_name, tenant_name),
                                         volume.delete)

    operation_list.confirm_and_execute()





