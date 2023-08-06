"""
Main Stackler Script
"""

from datetime import datetime
import os
import subprocess
import click
from git import Repo
import typer
from stackler import display_utils
from stackler import phab_utils

REPO_PATH = os.getcwd()
BASE_TAG = "origin/develop"

app = typer.Typer()


@app.command()
def submit(base_tag: str = typer.Option(BASE_TAG, "--base-tag", "-b"),
           update_message: str = typer.Option(
               '', "--update-message", "-m", help='The message for updating a diff'),
           dry_run: bool = typer.Option(
               False,
               "--dry-run", "-n",
               help='Print which commits are going to be submitted, but doesn\'t submit anything'),
           debug_dry_run: bool = False):
    """
    Submit a stack of commits separately.
    """
    _submit(base_tag=base_tag,
            update_message=update_message,
            dry_run=dry_run,
            debug_dry_run=debug_dry_run,
            prompt_dry_run=False)


def _submit(base_tag: str = BASE_TAG,
            update_message: str = '',
            dry_run: bool = False,
            debug_dry_run: bool = False,
            prompt_dry_run=False):

    # do an internal dry run to show the prompt
    if not dry_run and not debug_dry_run and not prompt_dry_run:
        print("By continuing, this script will:")
        _submit(base_tag=base_tag,
                update_message=update_message,
                dry_run=dry_run,
                debug_dry_run=debug_dry_run,
                prompt_dry_run=True)
        if not click.confirm('Do you want to continue?', default=True):
            print('Aborted')
            return

    # To submit a stack, a few things need to happen:
    # 1. find the base commit, which will remain unchanged for the entirety of
    # the operation.
    # 2. go through the stack of commits one by one via checkout:
    #     a. diff it out, get a modified commit
    #     b. connect diff with the previous one
    #     c. checkout the tip of the stack, rebase it onto the lastly modified
    #     commit
    # 3. move HEAD to the new tip

    repo = Repo(REPO_PATH)
    current_branch = repo.active_branch
    base_commit = repo.commit(base_tag)
    prev_commits = [repo.head.commit]
    for prev_commit in repo.head.commit.traverse():
        if prev_commit == base_commit:
            break
        prev_commits.append(prev_commit)

    # 1. find the base commit
    current_commit = prev_commits[-1]
    if base_commit == current_commit:
        print("No commit to submit")
        return

    # 2. go through the stack of commits
    prev_commit = base_commit
    prev_diff_id = ''
    current_diff_id = ''
    for i in range(len(prev_commits)):
        # sanity check:
        # Base - A - B - C - D
        # len(prev_commits) = 4
        # i goes from 0 to 3
        # to go to A, we need HEAD^3 (4 - 1)
        # hence `len(prev_commits) - i - 1`
        # HEAD^x now has x going from 3 to 0; current_commit from A to D
        current_commit = repo.commit(f'HEAD~{len(prev_commits) - i - 1}')

        repo.git.checkout(current_commit)
        is_updating = phab_utils.has_diff_attached()
        if is_updating:
            current_diff_id = phab_utils.get_diff_id()

        # show msgs
        if is_updating:
            display_utils.print_update_msg(
                current_commit, current_diff_id, update_message)
        else:
            display_utils.print_submit_msg(current_commit, prev_commit)

        # 2a. diff it out
        if not prompt_dry_run and not dry_run and not debug_dry_run:
            arc_args = ["arc", "diff", prev_commit.hexsha]
            if is_updating and update_message:
                arc_args.append('-m')
                arc_args.append(update_message)
            subprocess.run(arc_args, check=True)

            # 2b. connect the diff with previous one
            current_diff_id = phab_utils.get_diff_id()
            if not is_updating and prev_diff_id:
                phab_utils.add_parent_to_diff(current_diff_id, prev_diff_id)
            prev_diff_id = current_diff_id

        elif debug_dry_run:
            subprocess.run(
                f"git commit --amend -m '{repo.head.commit.message}updated at {datetime.now()}'",
                shell=True,
                check=True)

        # 2c. restack
        prev_commit = repo.head.commit
        repo.git.checkout(current_branch)
        repo.git.rebase(prev_commit.hexsha)

    # 3. move HEAD to new tip
    # already performed


@app.callback()
def callback():
    """Stackler makes working with stacks easier."""
    # This makes Typer treat submit as an explict command
