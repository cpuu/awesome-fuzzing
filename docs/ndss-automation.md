# NDSS Candidate Proposals

The `Propose NDSS Papers` workflow is manually triggered. There is no schedule
and no automatic merge. It copies official titles and links into a proposed diff;
the maintainer still decides which resources belong in the list.

## Run on GitHub

1. Merge the workflow and scripts into the default branch.
2. In Actions, select `Propose NDSS Papers` and `Run workflow`.
3. Set `year` to `2026`. Leave `create_pr` unchecked for the first preview.
4. Download the `ndss-preview` artifact: proposed README, candidate JSON with
   source/cycle/PDF metadata, and proposed PR description.
5. Run again with `create_pr` checked to create a draft PR from `ndss` to the
   default branch. Review the diff and sources before marking ready and merging.

Enable `Allow GitHub Actions to create and approve pull requests` under repository
Settings > Actions > General > Workflow permissions for PR creation. The workflow
requests contents and pull-request write access. Actions write access dispatches
the existing lint workflow on `ndss`, since the default `GITHUB_TOKEN` does not
trigger another push/PR workflow. No personal token is required.

An existing `ndss` branch must have an open PR bearing this workflow's marker and
only bot-authored commits ahead of the default branch. Otherwise the workflow
stops rather than overwriting manual work. Finish or merge manual work first.
Re-runs update the same proposal; no-change runs do not create new PRs.

## Collection Rules

- Match `fuzz` case-insensitively in official paper-card titles, not authors or abstracts.
- Check the accepted-page year and published total when present. Verify each
  candidate's title, NDSS year, and summer/fall tag on its official detail page.
- Prefer the official Paper PDF link, falling back to the official detail page.
  PDF content and availability are not independently downloaded/tested.
- Add missing entries in a yearly NDSS collapsible group. Update the count and
  README coverage end year, preserving other conference sections.
- Preserve existing entries. Report changed links/titles for human review; abort
  if existing entries disappear from the source or existing markup is ambiguous.
- Do not invent summaries or infer cycles from title, URL numbering, or ordering.

The live 2026 comparison on 2026-09-14 returned summer=7 and fall=6, matching the
maintainer's count. These are not hardcoded limits. Page layout changes may require
parser updates.

## Local Preview and Tests

Install uv alongside Node.js/pnpm. All Python runs use uv:

```sh
uv run --no-project --python 3.12 python scripts/ndss.py --year 2026 --output-dir /tmp/ndss-preview
pnpm test
```

Preview leaves the working README unchanged. `--write` applies the proposal;
Actions uses it before lint and PR creation. Network or parsing failures stop
before writing the README. Tests use synthetic HTML without network requests.
No third-party Python packages are required.

References: [NDSS accepted papers](https://www.ndss-symposium.org/ndss2026/accepted-papers/),
[create-pull-request](https://github.com/peter-evans/create-pull-request),
[setup-uv](https://github.com/astral-sh/setup-uv).
