from config import CONFIG


def parse_input(line):
    cmd_list = line.split(' ')
    # first element is the command
    command = cmd_list[0]
    # remainaing is args
    # args = cmd_list[1:]
    command_list = CONFIG['simple_commands']
    result = command_list.get(command)
    if not result:
        output = not_found(command)
    else:
        output = result['output']
    return output


def not_found(command):
    return "{0}: command not found".format(command)
