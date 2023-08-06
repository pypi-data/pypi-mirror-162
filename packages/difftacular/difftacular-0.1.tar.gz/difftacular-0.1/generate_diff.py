# Copyright (C) 2010-2012 Canonical Ltd
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


from contextlib import ExitStack

from ... import diff, revision as _mod_revision
from ...merge import Merge3Merger


def apply_merges(tree, branch, merges):
    """Apply the listed merges to the listed tree.

    :param tree: The tree to apply merges to.
    :param branch: A branch to provide merge configuration and to retrieve
        revision trees from.
    :param merges: The merges to apply, as a list of (base, other) tuples.
    :return: a tree with all merges applied."""
    repository = branch.repository
    for revisions in merges:
        base, other = repository.revision_trees(revisions)
        merger = Merge3Merger(tree, tree, base, other,
                              this_branch=branch, do_merge=False)
        transform = merger.make_preview_transform()
        tree = transform.get_preview_tree()
    return tree


def get_merged_tree(other_branch, other_revision, this_branch, this_tree):
    diff_base = get_lca(other_branch, other_revision, this_branch)
    merges = [(diff_base, other_revision)]
    return apply_merges(this_tree, other_branch, merges)


def mainline_diff(branch, old_revision, new_revision, to_file):
    """Perform a diff showing only changes made on mainline.

    :param branch: The branch to get merge configuration and revision trees
        from.
    :param old_revision: The old revision to use in the diff.
    :param new_revision: The new revision to use in the diff.
    :param to_file: A file-like object to write the diff to.
    """
    other_merges = merges(branch.repository, old_revision, new_revision)
    diff_with_merges(branch, old_revision, new_revision, other_merges, to_file)


def diff_with_merges(branch, old_revision, new_revision, merges, to_file):
    """Perform a diff with merges applied to the old revision.

    :param branch: The branch to get merge configuration and revision trees
        from.
    :param old_revision: The old revision to use in the diff.
    :param new_revision: The new revision to use in the diff.
    :param merges: The merges to apply to the old revision, as a list of
        (base, other) tuples.
    :param to_file: A file-like object to write the diff to.
    """
    repository = branch.repository
    old_tree = repository.revision_tree(old_revision)
    old_tree = apply_merges(old_tree, branch, merges)
    new_tree = repository.revision_tree(new_revision)
    diff.show_diff_trees(old_tree, new_tree, to_file, old_label='',
                         new_label='')


def ignore_heads(repository, ignore_branches, old_revision, new_revision):
    """List a bunch of revisions to ignore in a diff.

    The head revisions merged from ignore_branches into new_revision, but not
    merged into old_revision will be listed.

    :param repository: The repository to use for graphs.
    :param ignore_branches: The branches to ignore merges from.
    :param old_revision: The revision that the merges would go into.
    :param new_revision: The revision which has the merges applied.
    :return: a list of revision ids which are heads to merge.
    """
    lcas = []
    for branch in ignore_branches:
        graph = repository.get_graph(branch.repository)
        lcas.extend(graph.find_lca(new_revision, branch.last_revision()))
    if len(lcas) == 0:
        return []
    heads = graph.heads([old_revision] + lcas)
    return [h for h in heads if h != old_revision]


def diff_ignore_branches(branch, ignore_branches, old_revision, new_revision,
                         to_file):
    """Perform a diff ignoring merges from the specified branches.

    :param branch: The branch to get merge configuration and revision trees
        from.
    :param ignore_branches: The branches to ignore merges from.
    :param old_revision: The old revision to use in the diff.
    :param new_revision: The new revision to use in the diff.
    :param to_file: A file-like object to write the diff to.
    """
    repository = branch.repository
    merge_heads = ignore_heads(repository, ignore_branches, old_revision,
                               new_revision)
    graph = repository.get_graph()
    merges = iter_lca_revision(graph, old_revision, merge_heads)
    diff_with_merges(branch, old_revision, new_revision, merges, to_file)


def iter_merges(repository, revision_ids):
    """Iterate through (parent, child) tuples for a list of revisions.

    :param revision_ids: The revisions to iterate through.
    """
    graph = repository.get_graph()
    parent_map = graph.get_parent_map(revision_ids)
    merge_revisions = [r for r in revision_ids if len(parent_map[r]) > 1]
    for revision in revisions:
        parents = parent_map[revision]
        if len(parents) == 0:
            first_parent = _mod_revision.NULL_REVISION
        else:
            first_parent = parents[0]
        yield first_parent, revision


def iter_lca_revision(graph, revision, merge_revisions):
    """Iterate through (lca, revision) tuples for a list of revisions.

    :param graph: A Graph to use for generating unique LCAs.
    :param revision: The revision to generate LCAs against.
    :param merge_revisions: The revisions to iterate through.
    """
    for merge_revision in merge_revisions:
        base = graph.find_unique_lca(revision, merge_revision)
        yield base, merge_revision


def merges(repository, first_revision, second_revision):
    """Return a list of the merge revisions and their lefthand parents.

    :param repository: The repository to use for analysis
    :param first_revision: Ignore merges before this revision.  Must be a
        lefthand ancestor of second_revision.
    :param second_revision: Ignore merges after this revision.
    """
    revision_ids = []
    graph = repository.get_graph()
    for revision_id in graph.iter_lefthand_ancestry(second_revision,
                                                    (first_revision)):
        revision_ids.append(revision_id)
    revision_ids.reverse()
    parent_map = graph.get_parent_map(revision_ids)
    merge_revisions = [r for r in revision_ids if len(parent_map[r]) > 1]
    result = []
    for revision in merge_revisions:
        parents = parent_map[revision]
        if len(parents) == 0:
            first_parent = _mod_revision.NULL_REVISION
        else:
            first_parent = parents[0]
        result.append((first_parent, revision))
    return result


def get_lca(source_branch, source_revision, target_branch):
    """Return the LCA for a specified revision and target."""
    graph = source_branch.repository.get_graph(target_branch.repository)
    target_revision = target_branch.last_revision()
    return graph.find_unique_lca(target_revision, source_revision)


class PreviewDiffGenerator(object):
    """Generate a Launchapd-style Preview Diff."""

    def __init__(self, source_branch, target_branch, prerequisite_branch=None,
                 source_revision=None):
        self.source_branch = source_branch
        if source_revision is None:
            source_revision = source_branch.last_revision()
        self.source_revision = source_revision
        self.target_branch = target_branch
        self.prerequisite_branch = prerequisite_branch

    def get_from_tree(self, target_tree):
        """Return the tree to diff from.

        If there is no prerequisite branch, then the target branch's basis is
        used.  If a prerequisite is specified, then the last revision that was
        merged into source is merged into target.
        """
        from_tree = target_tree
        if self.prerequisite_branch is not None:
            # Find last revision merged into source_branch
            prereq_revision = get_lca(
                self.source_branch, self.source_revision,
                self.prerequisite_branch)
            # Merge found revision into target
            from_tree = get_merged_tree(
                self.source_branch, prereq_revision, self.target_branch,
                from_tree)
        return from_tree

    def generate_preview_diff(self, diff_writer):
        """Generate a preview diff.

        :param diff_writer: The writer to use for outputting the diff.
        """
        with ExitStack() as stack:
            for branch in [self.source_branch, self.target_branch,
                           self.prerequisite_branch]:
                if branch is not None:
                    stack.enter_context(branch.lock_read())
            target_tree = self.target_branch.basis_tree()
            from_tree = self.get_from_tree(target_tree)
            to_tree = get_merged_tree(self.source_branch, self.source_revision,
                                      self.target_branch, target_tree)
            diff.show_diff_trees(from_tree, to_tree, diff_writer, old_label='',
                                 new_label='')
