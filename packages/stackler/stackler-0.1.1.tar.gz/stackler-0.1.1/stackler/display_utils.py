"""
Display utils for better UX for Stackler
"""

from git import Commit
from termcolor import colored


def _darken(in_s: str) -> str:
    """returns a darkened string"""
    return colored(in_s, attrs=['dark'])


def _underline(in_s: str) -> str:
    """returns an underlined string"""
    return colored(in_s, attrs=['underline'])


def _cyan(in_s: str) -> str:
    """returns a cyan string"""
    return colored(in_s, 'cyan')


def _yellow(in_s: str) -> str:
    """returns a yellow string"""
    return colored(in_s, 'yellow')


def _green(in_s: str) -> str:
    """returns a green string"""
    return colored(in_s, 'green')


def _blue(in_s: str) -> str:
    """returns a blue string"""
    return colored(in_s, 'blue')


def _truncate_string(str_input, max_length):
    str_end = '...'
    length = len(str_input)
    if length > max_length:
        return str_input[:max_length - len(str_end)] + str_end
    return str_input


def commit_summary(cmt: Commit) -> str:
    """Returns an inline summary of a given commit"""
    hsh = cmt.hexsha[:8]
    msg = _truncate_string(cmt.message, 30)
    msg = msg.replace('\n', ' ').replace('\r', '')
    return f"[{_cyan(f'{hsh}')} {(msg)}]"


def print_update_msg(current_commit: Commit, current_diff_id: str, update_message: str):
    """print msg for updating an diff"""
    print(
        f"{_blue('Update')} {_yellow(current_diff_id)} with"
        + f" {commit_summary(current_commit)}"
        + (f", message: {_truncate_string(update_message, 30) }." if update_message else "."))


def print_submit_msg(current_commit: Commit, prev_commit: Commit):
    """print msg for submitting an diff"""
    print(
        f"{_green('Submit')} {commit_summary(current_commit)}"
        + f" based on {commit_summary(prev_commit)}.")
