# Repository Instructions

## Purpose

Awesome Fuzzing is a human-curated research resource listed under Security in
[Awesome](https://github.com/sindresorhus/awesome). Automation supports the
maintainer's research and editorial decisions; it does not replace them.

## Rule 1: Follow Upstream Awesome Guidelines

Read these primary sources when changing list policy or upgrading validation:

- [Contribution guide](https://github.com/sindresorhus/awesome/blob/main/contributing.md)
- [List requirements](https://github.com/sindresorhus/awesome/blob/main/pull_request_template.md)
- [Creating a list](https://github.com/sindresorhus/awesome/blob/main/create-list.md)
- [Awesome lint](https://github.com/sindresorhus/awesome-lint)

Last policy review: 2026-09-14. Upstream can change; report new conflicts rather
than silently weakening validation. Distinguish requirements for this list from
requirements for submitting a new list to the upstream repository.

Keep the README human-curated. Do not automatically add search results, generate
an entire list, or fabricate descriptions. Upstream disallows AI-generated lists
and fully AI-generated submissions to upstream. The maintainer must review
research relevance, accuracy, and inclusion decisions.

Preserve the Awesome heading and badge, topic introduction, Contents, and CC0
license. Keep contribution instructions outside Contents. Use consistent Markdown
and concise factual descriptions. Preserve official paper titles and publication
years. Do not infer that an old research paper is obsolete from its age alone.
Review software maintenance and documentation using the official repository.
Prefer canonical links; verify destinations before replacing HTTP links or URLs.

## Validation Before Commit and Push

- Use Node.js 24 and the pnpm version in package.json.
- Install with `pnpm install --frozen-lockfile --ignore-scripts`.
- Enable local guards with `pnpm hooks:install` in each clone.
- Run `pnpm lint` and `git diff --check` after the final edit and before committing.
- Review the staged diff and run `git diff --cached --check` before committing.
- Before pushing, validate the committed tree again. Hooks require no unstaged
  tracked edits at commit time and a clean tracked tree at push time.
- Do not commit or push when validation fails or cannot run. Report the command
  and unresolved errors. Do not bypass hooks or suppress lint to obtain a pass.
- Keep the linter version and lockfile in sync. Any justified rule exception must
  be narrow, documented, reviewed by the maintainer, and reported upstream when
  appropriate; never disable all lint rules.
- A request to configure validation is not a request to commit or push changes.

Lint does not establish research quality, link availability, repository activity,
or compliance with every upstream editorial rule. Review those separately and
describe unverified areas explicitly. See `docs/maintenance.md` for setup and
known gaps. Additional maintainer rules will be added here as they are supplied.
