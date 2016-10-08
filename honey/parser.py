from config import CONFIG


def parse_input(line):
    line_list = line.split(' ')
    command, args = line_list[0], line_list[1:]
    command_list = CONFIG['simple_commands']
    output = command_list.get(command)
    if not output:
        output = not_found(command)
    return output


def not_found(command):
    return "{0}: command not found".format(command)
