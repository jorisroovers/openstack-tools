import os

def exec_and_report(msg, func, *args):
    print msg,
    try:
        func(*args)
        print "DONE"
    except:
        print "FAIL"


def delete_resource(client, resource_name, resource):
    message = "\tDeleting %s %s (%s)..." % (resource_name, resource['name'], resource['id'])
    delete_method_name = "delete_" + resource_name
    delete_method = getattr(client, delete_method_name)
    exec_and_report(message, delete_method,resource['id'])

def print_table():
    pass

def print_row(cols):
    for col in cols:
        print col,
    print #newline



