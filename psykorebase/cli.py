# -*- coding: utf-8 -*-
"""Command line interfaces, i.e. scripts."""
from __future__ import print_function
import argparse
import subprocess
import sys

from contextlib import contextmanager
from os import getcwd, chdir
from os.path import abspath, isdir, join
from six.moves import input


class ExecutionError(Exception):
    """Raised when some subprocess returns error."""


def execute(command, stdin=None, stdout=None, stderr=None, confirm=False,
            capture=False):
    if confirm:
        answer = ''
        while answer not in ['y', 'n']:
            answer = input('About to execute "%s". Continue? [y, n] '
                           % ' '.join(command))
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
        raise ExecutionError('Command "%s" returned code %d' % (
            ' '.join(command), retcode))
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
    def __init__(self, repository_path, primary_branch, secondary_branch=None,
                 no_ff=False, rebase_continue=False, ask=False):
        self.repository_path = repository_path
        if not primary_branch and not rebase_continue:
            raise NotImplementedError('Unable to psykorebase without a '
                                      'primary_branch.')

        if rebase_continue:
            # Rebase --continue
            target_branch = self.current_branch()
            if '-rebased-on-top-of-' not in target_branch:
                raise ValueError('Unable to continue psykorebase on '
                                 '{target_branch}.'.format(
                                     target_branch=target_branch))
            self.secondary_branch, self.primary_branch = target_branch \
                                       .split('-rebased-on-top-of-')
            self.target_branch = target_branch
            print("Working with git, continue rebasing of {secondary} "
                  "on top of {primary}".format(
                      primary=self.primary_branch,
                      secondary=self.secondary_branch))
        else:
            self.primary_branch = primary_branch
            if secondary_branch is None:
                secondary_branch = self.current_branch()
            self.secondary_branch = secondary_branch
            self.target_branch = '%s-rebased-on-top-of-%s' % (
                self.secondary_branch, self.primary_branch)
        self.no_ff = no_ff is True
        self.rebase_continue = rebase_continue is True
        self.ask_confirmation = ask is True

        if self.secondary_branch == self.primary_branch:
            raise NotImplementedError('Unable to psykorebase {branch} on '
                                      'itself'.format(
                                          branch=self.primary_branch))

    def rebase(self):
        """Actually rebase."""
        if not self.rebase_continue:
            self.checkout(self.primary_branch)
            self.checkout(self.target_branch, create=True)
            self.merge(self.secondary_branch, no_ff=self.no_ff,
                       message='Psycho-rebased branch %s on top of %s'
                       % (self.secondary_branch, self.primary_branch))
        else:
            self.commit()
        self.delete_branch(self.secondary_branch)
        self.rename_branch(self.target_branch, self.secondary_branch)

    def checkout(self, branch, create=False):
        with cd(self.repository_path):
            command = ['git', 'checkout', branch]
            if create:
                command.insert(2, '-b')
            execute(command, confirm=self.ask_confirmation)

    def commit(self):
        with cd(self.repository_path):
            command = ['git', 'commit']
            execute(command, confirm=self.ask_confirmation)

    def merge(self, branch, no_ff=False, message=None):
        with cd(self.repository_path):
            command = ['git', 'merge', branch]
            if message is not None:
                command.extend(['-m', message])
            if no_ff:
                command.extend(['--no-ff'])
            else:
                command.extend(['--ff'])
            try:
                execute(command, confirm=self.ask_confirmation)
            except ExecutionError:
                print("Resolve the conflict and run "
                      "``psykorebase --continue``.")
                sys.exit(1)

    def delete_branch(self, branch):
        with cd(self.repository_path):
            command = ['git', 'branch', '-d', branch]
            execute(command, confirm=self.ask_confirmation)

    def rename_branch(self, src, dst):
        with cd(self.repository_path):
            command = ['git', 'branch', '-m', src, dst]
            execute(command, confirm=self.ask_confirmation)

    def current_branch(self):
        """Return name of current branch, using ``git branch``."""
        command = ['git', 'branch']
        process = execute(command, capture=True)
        stdout, __ = process.communicate()
        branches = stdout.decode('utf-8').split('\n')
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

    def dvcs_directory(self):
        """Return path to Git directory, i.e. to :file:`.git/`."""
        command = ['git', 'rev-parse', '--git-dir']
        process = execute(command, capture=True)
        stdout, __ = process.communicate()
        directory = stdout.strip()
        return directory


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
                        nargs='?',
                        default=None,
                        help='Branch you want to apply changes on top of.')
    parser.add_argument('secondary_branch',
                        metavar='SECONDARY-BRANCH',
                        type=str,
                        nargs='?',
                        default=None,
                        help='Branch with changes you want to rebase.')
    parser.add_argument('--no-ff',
                        dest='no_ff',
                        action='store_true',
                        help='Force a commit message for the psykorebase.')
    parser.add_argument('--continue',
                        dest='rebase_continue',
                        action='store_true',
                        help='Continue the rebase after a merge conflict.')
    parser.add_argument('--ask',
                        dest='ask',
                        action='store_true',
                        help='Ask confirmation before each command.')
    parsed_args = parser.parse_args(args)
    dvcs_type = get_dvcs_type(repository_path)
    primary_branch = parsed_args.primary_branch
    secondary_branch = parsed_args.secondary_branch
    no_ff = parsed_args.no_ff
    rebase_continue = parsed_args.rebase_continue
    ask = parsed_args.ask

    if primary_branch is None and not rebase_continue:
        sys.stderr.write("You must specify the branch you want "
                         "to psykorebase from.\n")
        sys.exit(100)

    factory = get_rebaser_factory(dvcs_type)
    rebaser = factory(repository_path,
                      primary_branch,
                      secondary_branch,
                      no_ff, rebase_continue, ask)
    if not rebase_continue:
        print("Working with {dvcs}, rebasing {secondary} on top of {primary}"
              .format(dvcs=dvcs_type, primary=rebaser.primary_branch,
                      secondary=rebaser.secondary_branch))
    rebaser.rebase()
