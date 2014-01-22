import subprocess

__author__ = 'Joris Roovers'


def stream_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')


def run_command(command):
    if isinstance(command, basestring):
        command = command.split(" ")
    result = []
    for line in stream_command(command):
        result.append(line.replace("\n", ""))
    return result
