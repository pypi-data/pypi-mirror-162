# Copyright (C) 2010-2011 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import sys

from ... import branch, commands, errors, option, trace, urlutils
from . import generate_diff

class DiffCommand(commands.Command):

    encoding_type = 'exact'

    @staticmethod
    def get_revision_ids(revision, my_branch):
        if revision is None or len(revision) < 1:
            raise errors.BzrCommandError(
                'One or more revisions must be supplied.')
        old_revision = revision[0].as_revision_id(my_branch)
        if len(revision) > 1:
            new_revision = revision[1].as_revision_id(my_branch)
        else:
            new_revision = my_branch.last_revision()
        return old_revision, new_revision


class cmd_diff_mainline(DiffCommand):
    __doc__ = """\
    Perform a diff reflecting only changes originated in the mainline.
    """

    takes_options = ['revision']

    def run(self, revision=None):
        my_branch = branch.Branch.open_containing('.')[0]
        my_branch.lock_read()
        try:
            old_revision, new_revision = self.get_revision_ids(revision,
                                                               my_branch)
            writer = option.diff_writer_registry.get()
            generate_diff.mainline_diff(my_branch, old_revision, new_revision,
                                        writer(self.outf))
        finally:
            my_branch.unlock()


class cmd_diff_ignore_branches(DiffCommand):

    __doc__ = """Perform a diff ignoring merges from the specified branches."""
    takes_options = ['revision']
    takes_args = ['branch*']

    def run(self, revision=None, branch_list=None):
        if branch_list is None:
            branch_list = []
        my_branch = branch.Branch.open_containing('.')[0]
        my_branch.lock_read()
        try:
            old_revision, new_revision = self.get_revision_ids(revision,
                                                               my_branch)
            branches = [branch.Branch.open_containing(b)[0]
                        for b in branch_list]
            writer = option.diff_writer_registry.get()
            generate_diff.diff_ignore_branches(
                my_branch, branches, old_revision, new_revision,
                writer(self.outf))
        finally:
            my_branch.unlock()


class cmd_preview_diff(DiffCommand):

    __doc__ = """Perform a Launchpad-style preview diff.

    If no target branch is specified, the submit or parent branch will be
    used.
    """

    takes_args = ['source_branch?', 'target_branch?']
    takes_options = [option.Option(
        'prerequisite-branch',
        type=(str if sys.version_info[0] >= 3 else unicode),
        help='Use this as a prerequisite branch.')]

    def run(self, source_branch='.', target_branch=None,
            prerequisite_branch=None):
        writer = option.diff_writer_registry.get()
        source = branch.Branch.open_containing(source_branch)[0]
        remembered = None
        if target_branch is None:
            target_branch = source.get_submit_branch()
            remembered = 'submit'
        if target_branch is None:
            target_branch = source.get_parent()
            remembered = 'parent'
        if target_branch is None:
            raise errors.BzrCommandError('No target specified or remembered.')
        if remembered is not None:
            trace.note('Using remembered %s branch "%s".', remembered,
                       urlutils.unescape_for_display(target_branch, 'utf-8'))
        target = branch.Branch.open_containing(target_branch)[0]
        if prerequisite_branch is None:
            prerequisite = None
        else:
            prerequisite = branch.Branch.open_containing(
                prerequisite_branch)[0]
        generator = generate_diff.PreviewDiffGenerator(source, target,
                                                       prerequisite)
        generator.generate_preview_diff(writer(self.outf))
