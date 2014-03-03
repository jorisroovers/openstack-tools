from common.os_client_manager import OSClientManager


class OperationList():

    def __init__(self):
        self.operations = []
        self.descriptions = []

    def add_operation(self, description, func):
        self.descriptions.append(description)
        self.operations.append(func)

    def confirm_and_execute(self):
        print "The following operations are scheduled for execution:"
        for description in self.descriptions:
            print description

        valid_input = ["y", "n"]
        input = ""
        while (input not in valid_input):
            input = raw_input("Do you want to execute these operations? (y/n)")
            input = input.lower()

        if input == "y":
            print "Executing Operations..."
            for index, description in enumerate(self.descriptions):
                print "%s..." % description,
                try:
                    self.operations[index]()
                    print "DONE"
                except:
                    print "FAIL"
            print "All Done."
            return True
        else:
            print "Aborted."
            return False


def main():

    mgr = OSClientManager.create_from_env_vars()
    volume_client = mgr.volume_client

    print "Fetching volumes..."
    volumes = volume_client.volumes.list()

    print "Cleaning up Tempest volumes"

    operation_list = OperationList()

    for volume in volumes:
        if "tempest" in volume.display_name:
            print dir(volume)
            operation_list.add_operation("Delete %s" % volume.display_name, volume.force_delete)

    operation_list.confirm_and_execute()





