# Copyright (C) 2010 Canonical Ltd
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


from io import BytesIO

from .. import generate_diff
from .... import tests


def get_controldir(tree):
    try:
        # Breezy
        return tree.controldir
    except AttributeError:
        # Bazaar
        return tree.bzrdir


class TestMainlineDiff(tests.TestCaseWithTransport):

    def create_diff_scenario(self):
        foo = self.make_branch_and_tree('foo')
        foo.lock_write()
        self.addCleanup(foo.unlock)
        self.build_tree_contents([('foo/baz', 'a\nz\n')])
        foo.add('baz')
        rev1 = foo.commit('initial commit')
        bar = get_controldir(foo).sprout('bar').open_workingtree()
        self.build_tree_contents([('bar/baz', 'c\na\nz\n')])
        rev2_bar = bar.commit('add c')
        foo.merge_from_branch(bar.branch)
        rev2 = foo.commit('merge')
        self.build_tree_contents([('foo/baz', 'c\na\nb\nz\n')])
        rev3 = foo.commit('add b')
        return foo, bar, rev1, rev2, rev2_bar, rev3

    def test_mainline_diff(self):
        foo, bar, rev1, rev2, rev2_bar, rev3 = self.create_diff_scenario()
        buf = BytesIO()
        generate_diff.mainline_diff(foo.branch, rev1, rev3, buf)
        self.assertContainsRe(buf.getvalue(), br'\+b')
        self.assertContainsRe(buf.getvalue(), br' a')
        self.assertNotContainsRe(buf.getvalue(), br'\+c')

    def test_merges(self):
        foo, bar, rev1, rev2, rev2_bar, rev3 = self.create_diff_scenario()
        self.assertEqual([(rev1, rev2)], list(
            generate_diff.merges(foo.branch.repository, rev1, rev3)))

    def create_unignored_merge_scenario(self):
        foo, bar, rev1, rev2, rev2_bar, rev3 = self.create_diff_scenario()
        unignored = get_controldir(foo).sprout('unignored').open_workingtree()
        self.build_tree_contents([('unignored/baz', 'c\na\nb\nz\nd\n')])
        unignored.commit('add d')
        foo.merge_from_branch(unignored.branch)
        rev4 = foo.commit('merge')
        return foo, bar, rev1, rev2_bar, rev4

    def test_diff_ignore_branches(self):
        foo, bar, rev1, rev2_bar, rev4 = self.create_unignored_merge_scenario()
        buf = BytesIO()
        generate_diff.diff_ignore_branches(foo.branch, [bar.branch], rev1,
                                           rev4, buf)
        self.assertContainsRe(buf.getvalue(), br'\+b')
        self.assertContainsRe(buf.getvalue(), br' a')
        self.assertNotContainsRe(buf.getvalue(), br'\+c')
        self.assertContainsRe(buf.getvalue(), br'\+d')

    def test_diff_ignore_old_revisions(self):
        foo, bar, rev1, rev2_bar, rev4 = self.create_unignored_merge_scenario()
        bar.commit('emtpy commit')
        foo.merge_from_branch(bar.branch)
        rev5 = foo.commit('empty commit')
        buf = BytesIO()
        generate_diff.diff_ignore_branches(foo.branch, [bar.branch], rev1,
                                           rev5, buf)
        self.assertContainsRe(buf.getvalue(), br'\+b')
        self.assertContainsRe(buf.getvalue(), br' a')
        self.assertNotContainsRe(buf.getvalue(), br'\+c')
        self.assertContainsRe(buf.getvalue(), br'\+d')

    def test_ignore_heads(self):
        foo, bar, rev1, rev2_bar, rev4 = self.create_unignored_merge_scenario()
        repo = foo.branch.repository
        heads = generate_diff.ignore_heads(repo, [bar.branch], rev1, rev4)
        self.assertEqual([rev2_bar], heads)

    def test_ignore_heads_already_merged(self):
        foo = self.make_branch_and_tree('foo')
        foo.lock_write()
        self.addCleanup(foo.unlock)
        rev1 = foo.commit('done')
        bar = get_controldir(foo).sprout('bar').open_workingtree()
        rev2b = bar.commit('done')
        foo.merge_from_branch(bar.branch)
        rev2 = foo.commit('done')
        rev3 = foo.commit('done')
        repo = foo.branch.repository
        heads = generate_diff.ignore_heads(repo, [bar.branch], rev2, rev3)
        self.assertEqual([], heads)
