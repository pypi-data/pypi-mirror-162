#!/usr/bin/python
# coding: utf-8
""" This script loads branches information to a Json file
and reconstruct branches from such files.

The file format is as follows::

    [
        {
            "branch":"branch_name",
            "commit":"commit_hash",
            "depth":1,
            "is_dirty":false,
            "name":"repo_name",
            "path":"path/to/clone",
            "repo_url":{
                "origin":"git@github.com:Vauxoo/repo_name.git"
            },
            "type":"git"
        },
        {
            "branch":"branch_name",
            "commit":"commit_hash",
            "depth":1,
            "is_dirty":false,
            "name":"anotherrepo_name",
            "path":"path/to/clone/other/repo",
            "repo_url":{
                "origin":"git@github.com:Vauxoo/anotherrepo_name.git"
            },
            "type":"git"
        }
    ]

Is a list of dictionaries containing all the information of the repos where:

*branch*: Name of the branch
*commit*: commit hash you wish in the build (leave blank for the latest)
*depth*: --depth option (see git doc)
*is_dirty*: True if there is any local change that have not been commited yet
*name*: repo name
*path*: path where the repo will be cloned
*repo_url*: Github url where the repo is stored o where it was gotten from
"""

import chardet
import os
import logging
import git
from git import Repo
from . import utils

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)-5s - %(name)s.%(module)s.%(funcName)s - %(message)s'
)
_logger = logging.getLogger('Branchesv')


class GitBranch(object):
    """ This class provides manipulation of git repositories using
    lists of config dictionaries. Each dictionary contains the following
    information of a git branch:

    *path*: Path of branch location, usually relative to a common origin
    *name*: Name of repository
    *branch*: Branch to be used
    *commit*: Hash of the commit pointed by HEAD
    *is_dirty*: Status of the branch
    *depth*: Depth of the cloned branch. False by default.
    *type*: Always 'git'.
    *repo_url*: Urls of remote origins of the repository
    """

    def __init__(self, key_path=False):
        self.identity_file = '-i %s' % (key_path) if key_path else ''
        self.ssh_command = ('ssh %s -o UserKnownHostsFile=/dev/null '
                            ' -o StrictHostKeyChecking=no '
                            ' -o BatchMode=yes') % (self.identity_file)

    def __get_branch(self, path):
        """ Gets required information of a repository

            :param path: Path of .git directory
            :return: Config dictionary
        """
        info = {}
        repo = Repo(path)
        info.update({'path': str(os.path.dirname(path)),
                     'branch': str(repo.head.ref),
                     'commit': str(repo.head.reference.commit),
                     'is_dirty': repo.is_dirty(),
                     'name': utils.name_from_url(str(repo.remotes[0].url)),
                     'depth': 1})
        urls = {}
        remotes = repo.remotes
        for remote in remotes:
            urls.update({remote.name: remote.url})
        info.update({'repo_url': urls})
        return info

    def is_branch(self, path):
        """ Checks if a given path exists and is a git branch or not

            :param path: Path to be checked
            :return: True if path exists and is a git branch. False otherwise.
        """
        isbranch = False
        if os.path.exists(path):
            if os.path.isdir(path) and not os.path.islink(path):
                if ".git" in os.listdir(path):
                    isbranch = True
        return isbranch

    def get_recursive_branches(self, path):
        """ Gets information of all existing repositories in a
        directory in a recursive way, searching all the inner
        paths

            :param path: Common path that contains the repositories
            :param verbose: A param that allows to write in the logger or not
            :return: List of config dictionaries
        """
        res = []
        if os.path.exists(path) and os.path.isdir(path) and \
           not os.path.islink(path):
            for element in os.listdir(path):
                try:
                    element_path = os.path.join(path, element)
                except UnicodeDecodeError:
                    encoding = chardet.detect(element)['encoding']
                    element_path = os.path.join(path, element.decode(encoding))
                if os.path.isdir(element_path) and not os.path.islink(element_path):
                    if element == '.git':
                        res.append(self.__get_branch(element_path))
                        _logger.debug("Branch collected from %s", element_path)
                    else:
                        temp_res = self.get_branches(element_path)
                        if temp_res:
                            res = res + temp_res
        return res

    def get_branches(self, path, recursive=True):
        """ Gets information of all existing repositories in a
        directory

            :param path: Common path that contains the repositories
            :param verbose: A param that allows to write in the logger or not
            :param recursive: Sets the search as recursive in the path
            :return: List of config dictionaries
        """
        if recursive:
            res = self.get_recursive_branches(path)
        else:
            res = []
            if self.is_branch(path):
                git_path = os.path.join(path, ".git")
                res.append(self.__get_branch(git_path))
        return res

    def get_depth(self, branch):
        """ Gets the depth of the repository

            :param branch: Config dictionary of the repository
            :return: Depth or False
        """
        depth = branch.get('depth', False)
        if not depth:
            return depth
        if depth == 0:
            return False
        return depth

    def __clone(self, path, branch):
        """ Clones a repository in the specified path

            :param path: Path where will be cloned the repository
            :param branch: Config dictionary of the repository
            :return: Message dictionary
        """
        depth = self.get_depth(branch)
        clone_path = os.path.join(path, branch['path'])
        url = branch['repo_url'].get('origin', list(branch['repo_url'].values())[0])
        _logger.debug('Cloning repo %s - branch %s', branch['name'], branch['branch'])
        kwargs = {'env': {'GIT_SSH_COMMAND': self.ssh_command}}
        if branch.get('branch', False):
            kwargs.update({'depth': depth, 'branch': branch['branch']})
        try:
            repo = Repo.clone_from(url, clone_path, **kwargs)
            branch.update({'branch': str(repo.head.ref),
                           'curr_commit': str(repo.head.reference.commit)})
            _logger.debug('Repo cloned %s - branch %s', branch['name'], branch['branch'])
            res = utils.set_message(branch)
        except git.exc.GitCommandError as error:
            _logger.error(error)
            res = utils.set_message(branch, error.stderr)
        return res

    def set_branch(self, branch, path):
        """ Clones a single repository in the specified path with the
        specified configuration

            :param branch: Config dict of the repository
            :param path: Path where will be cloned the repository
            :return: Message dictionary
        """
        _logger.info('Setting repo %s - branch %s', branch['name'], branch['branch'])
        if not branch.get('path', False):
            branch.update({'path': branch['name']})
        clone_path = os.path.join(path, branch['path'])
        if os.path.exists(clone_path) and self.is_branch(clone_path):
            if branch.get('commit', False):
                res = self.reset(branch, path)
            else:
                res = self.__pull(branch, clone_path)
            if res['exit_code'] != 0:
                branch.update({'depth': 0})
                utils.clean_files(clone_path)
                res = self.__clone(path, branch)
                if branch.get('commit', False):
                    res = self.reset(branch, path)
        elif branch.get('commit', False):
            branch.update({'depth': 0})
            res = self.__clone(path, branch)
            if res['exit_code']:
                return res
            res = self.reset(branch, path)
        else:
            res = self.__clone(path, branch)
        if branch.get('curr_commit', False):
            _logger.info('Repo set %s - branch %s - sha %s', branch['name'], branch['branch'],
                         branch['curr_commit'])
            branch.pop('curr_commit')
        return res

    def reset(self, branch, path):
        _logger.debug('Resetting repo %s to commit %s', branch['path'], branch['commit'])
        reset_path = os.path.join(path, branch['path'])
        repo = Repo(reset_path)
        try:
            repo.git.reset(branch['commit'], "--hard")
            branch.update({'curr_commit': str(repo.head.reference.commit)})
            _logger.debug('Repo %s reset to commit %s', branch['path'], branch['commit'])
            res = utils.set_message(branch)
        except git.exc.GitCommandError as error:
            _logger.error(error)
            res = utils.set_message(branch, error.stderr)
        return res

    def __pull(self, branch, path=False):
        """ Pulls in the repo the new information from the origin url
            :param path: Path of the repository to be pulled
            :param branch: Config dict of the repository
            :return: Message dictionary
        """
        if not path:
            path = branch['path']
        url = branch['repo_url'].get('origin', list(branch['repo_url'].values())[0])
        try:
            repo = Repo(path)
            repo.git.update_environment(GIT_SSH_COMMAND=self.ssh_command)
            if not branch.get('branch', False):
                branch.update({'branch': str(repo.head.ref)})
            for remote in repo.remotes:
                if remote.url == url:
                    repo_index = repo.remotes.index(remote)
                    repo.remotes[repo_index].pull(branch['branch'])
                    branch.update({'curr_commit': str(repo.head.reference.commit)})
                    res = utils.set_message(branch)
                    break
            else:
                error_message = (
                    'The remote {remote} specified for the repository {repo} does not'
                    ' match any of the remotes of the repo that is already cloned in {path}.'
                    ' The repository {repo} will be cloned again'.format(remote=url,
                                                                         repo=branch['name'],
                                                                         path=path)
                    )
                _logger.warning(error_message)
                res = utils.set_message(branch, 'fatal: wrong remote')
        except git.exc.GitCommandError as error:
            res = utils.set_message(branch, error.command[0])
        except git.exc.NoSuchPathError:
            _logger.error("fatal: No Such Path %s", branch['path'])
            res = utils.set_message(branch, "fatal: No Such Path {path}".format(path=path))
        return res

    def pull(self, branch):
        """ Updates a single branch to a specified commit

            :param path: Common path of the repositories
            :param branch: Branches to be updated
            :return: Message dictionary
        """
        _logger.debug('Pulling latest changes for %s', branch['name'])
        res = self.__pull(branch)
        _logger.debug('Latest changes pulled for %s', branch['name'])
        return res


def action_file(tmp_dir, action, path):
    """ This function saves branches configuration in a json file, this is
    intended to be used before or after some action is executed on the
    instance

        :param dir: Directory where file will be dumped
        :param action: Reason for dumping the file
        :param path_list: List of paths where the branches are located
        :param branches: List of config dictionaries to be dumped
    """
    _logger.debug('Creating %s', action)
    b_info = []
    branches = GitBranch()
    temp_res = branches.get_branches(path)
    b_info = b_info + temp_res
    b_info = utils.simplify_path(b_info)
    file_action = os.path.join(tmp_dir, action)
    utils.save_json(b_info, file_action)


def save(json_file, path, recursive):
    """save command
    """
    if path == '.':
        path = os.getcwd()
    path_list = path.split(',')
    gitbranch = GitBranch()
    for paths in path_list:
        b_info = gitbranch.get_branches(paths, recursive=recursive)
        b_info_simple = utils.simplify_path(b_info)
        utils.save_json(b_info_simple, json_file)


def load(repos, path, tmp, key_path=False):
    if path == '.':
        path = os.getcwd()
    path_list = path.split(',')
    gitbranch = GitBranch(key_path)
    for paths in path_list:
        action_file(tmp, "pre_process.json", paths)
        for repo in repos:
            res = gitbranch.set_branch(repo, paths)
            if res.get('exit_code') > 0:
                return res
        action_file(tmp, "post_process.json", paths)


def pull(path, tmp, recursive, key_path=False):
    if path == '.':
        path = os.getcwd()
    path_list = path.split(',')
    gitbranch = GitBranch(key_path)
    for paths in path_list:
        b_info = gitbranch.get_branches(path, recursive=recursive)
        action_file(tmp, "pre_process.json", paths)
        for branch in b_info:
            gitbranch.pull(branch)
        action_file(tmp, "post_process.json", paths)
