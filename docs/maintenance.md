# Maintenance and Validation

## Setup

Install Node.js 24 (see `.nvmrc`), pnpm 11.19.0, and uv, then run:

```sh
pnpm install --frozen-lockfile --ignore-scripts
pnpm hooks:install
pnpm lint
```

The package version and `pnpm-lock.yaml` pin the validation dependencies. Re-run
installation after pulling dependency changes. Hook installation is explicit and
must be repeated for every clone. It refuses to replace an existing hook setup.
Node.js and pnpm must be on the PATH used by your terminal or Git GUI.

## Commit, Push, and Merge

The pre-commit hook runs whitespace checks on staged changes and lints the list.
It rejects unstaged tracked edits, including partial staging, so a working-tree
fix cannot conceal a staged README error. Stage or stash those edits first.
Include any new validation files in the commit; untracked files are not published.

The pre-push hook lints a clean tracked working tree matching HEAD and rejects
updates to other commits or refs. Push one checked-out branch at a time. It checks
the outgoing tip, not every historical commit. Ref deletion alone needs no lint.
These guards deliberately do not stash files or alter the index automatically.

GitHub Actions runs the same lint command for pushes and pull requests, with a
frozen lockfile and full Git history. It also supports manual dispatch. Hooks
block local operations, whereas CI runs after a push. Hooks can be bypassed and
are not installed by Git cloning.

For server-side enforcement, configure a GitHub branch ruleset on the default
branch: require pull requests and the `lint` status check from `Lint Awesome List`,
and limit bypass permissions. Select the check after the workflow has run. This
blocks merging failing changes; it does not prevent uploading a feature branch.
Repository settings are separate from the files in this change and have not been
modified. Check the exact status-check name in the GitHub UI.

## Initial Audit (2026-09-14)

The original README passed awesome-lint 2.3.0 with no diagnostics. No lint rules
were suppressed. Manual inspection still found improvements:

- Contribution instructions were placeholders; they now describe review criteria.
- The contribution section was in Contents under `Contribute`; it is now titled
  `Contributing` and excluded from Contents, as upstream requests.
- Empty tool categories were removed for readability; reintroduce them with entries.
- The old workflow downloaded an unpinned lint version and only covered `master`.
  The replacement uses locked dependencies and covers all branches.

Remaining manual checks and decisions:

- The local remote HEAD points to `master`; upstream asks for `main`. Coordinate
  a default-branch migration and update GitHub settings and external references.
  Do not rename only the local branch and report the migration as complete.
- Verify GitHub topics include `awesome` and `awesome-list` and configure the
  required status check. These settings are not established by a local lint pass.
- Audit linked software for archived, deprecated, undocumented, or unmaintained
  projects. Upstream calls for moving such software to a separate Markdown file.
  Historical research papers need a different assessment from software tools.
- Some book entries have only a title and year. Review whether their titles are
  sufficiently descriptive; do not invent summaries to satisfy formatting.
- Existing HTTP and external links still need destination checks. No full link
  availability audit has been performed. HTTP alone is not a lint failure, and
  blindly replacing it with HTTPS can break a valid resource.
- Paper selection currently emphasizes four conferences but also includes arXiv
  and other venues. The maintainer will supply further research-selection rules.
- Upstream prohibits blockchain-related *list submissions*. That is not an
  explicit blanket ban on blockchain-targeting fuzzers inside this fuzzing list.
  Do not remove those entries based on that submission rule alone.

The linter checks Markdown and selected Awesome conventions, not every editorial
requirement, paper count, scientific claim, or live link. Human review remains
necessary. See the [contribution guidelines](../contributing.md) for the review
rules and upstream sources. Local agent instructions are not tracked in Git.
