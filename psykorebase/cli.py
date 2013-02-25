# coding=utf-8
"""Command line interfaces, i.e. scripts."""
import argparse
from contextlib import contextmanager
from os import getcwd, chdir
from os.path import abspath, isdir, join
import subprocess
import sys


class ExecutionError(Exception):
    """Raised when some subprocess returns error."""


def execute(command, stdin=None, stdout=None, stderr=None, confirm=False,
            capture=False):
    if confirm:
        answer = ''
        while answer not in ['y', 'n']:
            answer = raw_input('About to execute "%s". Continue? [y, n] '
                               % command)
        if answer is 'n':
            raise ExecutionError('ABORTED BY USER')
    if capture and stdout is None:
        stdout = subprocess.PIPE
    if capture and stderr is None:
        stderr = subprocess.PIPE
    process = subprocess.Popen(command, stdin=stdin, stdout=stdout,
                               stderr=stderr)
    retcode = process.wait()
    if retcode:
        raise ExecutionError('Command "%s" returned code %d' % (command,
                                                                retcode))
    return process


@contextmanager
def cd(path):
    current_path = abspath(getcwd())
    try:
        chdir(abspath(path))
        yield abspath(path)
    finally:
        chdir(current_path)


class GitRebaser(object):
    """Git implementation of psykorebase."""
    def __init__(self, repository_path, primary_branch, secondary_branch=None):
        self.repository_path = repository_path
        self.primary_branch = primary_branch
        if secondary_branch is None:
            secondary_branch = self.current_branch()
        self.secondary_branch = secondary_branch
        self.target_branch = '%s-rebased-on-top-of-%s' % (secondary_branch,
                                                          primary_branch)
        if self.secondary_branch == self.primary_branch:
            raise NotImplementedError('Unable to psykorebase {branch} on '
                                      'itself'.format(
                                          branch=self.primary_branch))

    def rebase(self):
        """Actually rebase."""
        self.checkout(self.primary_branch)
        self.checkout(self.target_branch, create=True)
        self.merge(self.secondary_branch,
                   message='Psycho-rebased branch %s on top of %s'
                           % (self.secondary_branch, self.primary_branch))
        self.delete_branch(self.secondary_branch)
        self.rename_branch(self.target_branch, self.secondary_branch)

    def checkout(self, branch, create=False):
        with cd(self.repository_path):
            command = ['git', 'checkout', branch]
            if create:
                command.insert(2, '-b')
            execute(command, confirm=True)

    def merge(self, branch, message=None):
        with cd(self.repository_path):
            command = ['git', 'merge', branch]
            if message is not None:
                command.extend(['-m', message])
            execute(command, confirm=True)

    def delete_branch(self, branch):
        with cd(self.repository_path):
            command = ['git', 'branch', '-d', branch]
            execute(command, confirm=True)

    def rename_branch(self, src, dst):
        with cd(self.repository_path):
            command = ['git', 'branch', '-m', src, dst]
            execute(command, confirm=True)

    def current_branch(self):
        """Return name of current branch, using ``git branch``."""
        command = ['git', 'branch']
        process = execute(command, capture=True)
        stdout, __ = process.communicate()
        branches = stdout.split('\n')
        # Current branch is the one highlighted with an asterisk.
        current_branch = None
        for branch in branches:
            if branch.startswith('*'):
                current_branch = branch[2:]
                break
        if current_branch is None:
            raise ExecutionError('Unable to guess current branch with "git '
                                 'branch".')
        return current_branch


def is_git(path):
    """Return True if path is a valid Git repository."""
    return isdir(join(path, '.git'))


GIT = 'git'
DVCS_IDENTIFIERS = {GIT: is_git}
REBASERS = {GIT: GitRebaser}


def get_dvcs_type(path, dvcs_identifiers=DVCS_IDENTIFIERS):
    """Return DVCS type for path."""
    for name, identify in dvcs_identifiers.items():
        if identify(path):
            return name
    raise NotImplementedError('Unable to guess version control system for '
                              'path "%s".' % path)


def get_rebaser_factory(dvcs_type, rebasers=REBASERS):
    """Return implementation factory for dvcs_type"""
    return rebasers[dvcs_type]


def psykorebase(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Perform safe merged-based rebases.')
    repository_path = getcwd()
    parser.add_argument('primary_branch',
                        metavar='PRIMARY-BRANCH',
                        type=str,
                        nargs=1,
                        help='Branch you want to apply changes on top of.')
    parser.add_argument('secondary_branch',
                        metavar='SECONDARY-BRANCH',
                        type=str,
                        nargs='?',
                        default=None,
                        help='Branch with changes you want to rebase.')
    parsed_args = parser.parse_args(args)
    dvcs_type = get_dvcs_type(repository_path)
    primary_branch = parsed_args.primary_branch[0]
    secondary_branch = parsed_args.secondary_branch
    factory = get_rebaser_factory(dvcs_type)
    rebaser = factory(repository_path,
                      primary_branch,
                      secondary_branch)
    print "Working with {dvcs}, rebasing {secondary} on top of {primary}" \
          .format(dvcs=dvcs_type, primary=rebaser.primary_branch,
                  secondary=rebaser.secondary_branch)
    rebaser.rebase()
