
def parse_input(line):
    cmd_list = line.split(' ')
    cmd = cmd_list[0]
    return not_found(cmd)


def not_found(command):
    return "{0}: command not found".format(command)
