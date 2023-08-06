"""
Phabricator related utils for Stackler
"""

import os
import re
import json
from phabricator import Phabricator
from git import Commit, Repo

PHABRICATOR_CONFIG_PATH = r".arcconfig"
PHBARICATOR_URI_KEY = r"phabricator.uri"


def _get_phab_uri() -> str:
    with open(PHABRICATOR_CONFIG_PATH, "r", encoding="utf-8") as arc_cfg_file:
        data = json.load(arc_cfg_file)
        return data[PHBARICATOR_URI_KEY]


P = Phabricator()
DIFF_REGEX = rf"(?<=Differential Revision: {_get_phab_uri()})D\d+"


def has_diff_attached(commit_id: str = ""):
    """check if the commit has a diff attached by checking the commit msg"""
    return re.search(DIFF_REGEX, _get_commit(commit_id=commit_id).message)


def get_diff_id(commit_id: str = "") -> str:
    """Get diff id like Dxxxxxx from a commit, HEAD if not specified"""
    return re.findall(DIFF_REGEX, _get_commit(commit_id=commit_id).message)[-1]


def add_parent_to_diff(diff_id: str, parent_diff_id: str):
    """Add the parent diff as the parent diff for the given diff_id"""
    parent_phid = _get_phid_from_diff_id(parent_diff_id)
    P.differential.revision.edit(transactions=[{"type": "parents.add", "value": [
                                 parent_phid]}, ], objectIdentifier=diff_id)


def _get_phid_from_diff_id(diff_id: str) -> str:
    """Get PHID from phabricator given a diff id"""
    return P.phid.lookup(names=[diff_id])[diff_id]["phid"]


def _get_commit(commit_id: str = "") -> Commit:
    """Get commit by id, HEAD if not specified"""
    repo = Repo(os.getcwd())
    cmt = repo.commit(commit_id) if commit_id else repo.head.commit
    return cmt
