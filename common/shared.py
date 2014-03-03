import os


def exec_and_report(msg, func, *args):
    print msg,
    try:
        func(*args)
        print "DONE"
    except:
        print "FAIL"


def delete_resource(client, resource_name, resource):
    message = "\tDeleting %s %s (%s)..." % (
        resource_name, resource['name'], resource['id'])
    delete_method_name = "delete_" + resource_name
    delete_method = getattr(client, delete_method_name)
    exec_and_report(message, delete_method, resource['id'])


def print_table():
    pass


def print_row(cols, col_lengths=15):
    for col in cols:
        length = max(col_lengths, len(col))
        extra_spacing = " " * abs((len(col) - length))
        print col + extra_spacing,
    print #newline


class OperationList():
    def __init__(self):
        self.operations = []
        self.descriptions = []

    def add_operation(self, description, func):
        self.descriptions.append(description)
        self.operations.append(func)

    def _get_input(self, question, valid_input):
        input = ""
        while (input not in valid_input):
            input = raw_input(question)
            input = input.lower()

        return input

    def confirm_and_execute(self):
        print "The following operations are scheduled for execution:"
        for description in self.descriptions:
            print description

        valid_input = ["a", "n", "q"]
        input = self._get_input("Do you want to execute these operations? ("
                                "[a]ll/[n]o/[q]uery one by one) ", valid_input)
        if input == "a":
            print "Executing Operations..."
            success = 0
            fail = 0
            for index, description in enumerate(self.descriptions):
                print "%s..." % description,
                try:
                    self.operations[index]()
                    print "DONE"
                    success += 1
                except:
                    print "FAIL"
                    fail += 1
            print "All Done (Success: %s, Fail: %s)" % (success, fail)
            return True

        elif input == "q":
            valid_input = ["y", "n"]
            success = 0
            fail = 0
            for index, description in enumerate(self.descriptions):
                input = self._get_input("%s... (y/n) " % description,
                                        valid_input)
                if input == "y":
                    try:
                        self.operations[index]()
                        print "DONE"
                        success += 1
                    except:
                        print "FAIL"
                        fail += 1
            print "All Done (Success: %s, Fail: %s)" % (success, fail)

        else:
            print "Aborted."
            return False