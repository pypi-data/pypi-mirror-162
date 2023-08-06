import os
import psutil


def get_shell_name():
    shell_name = psutil.Process(os.getppid()).name()
    return shell_name.lower()


SHELL_NAME = get_shell_name()


def get_msg_type(msg):
    if 'with_traceback' in dir(msg):
        msg_type = 'exception'
    else:
        msg_type = 'plain_text'
    return msg_type


def qprint(msg, color='red', background='black'):
    if SHELL_NAME == 'cmd.exe':
        if get_msg_type(msg) == 'plain_text':
            msg = f'-----------\n{msg}\n-----------'
        if get_msg_type(msg) == 'exception':
            msg = f'<Exception>\n{msg}\n</Exception>'
        print(msg)
        return
    else:
        color_dict = {
            'black': 30,
            'red': 31,
            'green': 32,
            'yellow': 33,
            'blue': 34,
            'magenta': 35,
            'cyan': 36,
            'white': 37,
        }
        color_num = color_dict.get(color, 31)
        background_num = color_dict.get(background, 30) + 10
        if get_msg_type(msg) == 'plain_text':
            msg = f'\033[0;{color_num};{background_num}m {msg} \n\033[0m'
        if get_msg_type(msg) == 'exception':
            msg = f'\033[0;{color_num};{background_num}m <Exception> \n {msg} \n </Exception> \n\033[0m'
        print(msg)
        return
