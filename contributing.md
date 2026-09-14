# Contribution Guidelines

Please note that this project is released with a [Contributor Code of Conduct](code-of-conduct.md). By participating in this project you agree to abide by its terms.

## Adding a Resource

Ensure your pull request adheres to the following guidelines:

- Follow the applicable [Awesome list requirements](https://github.com/sindresorhus/awesome/blob/main/pull_request_template.md). Requirements for submitting a new list to the upstream Awesome repository do not automatically apply to a resource PR here.
- Explain why the resource is useful for fuzzing research or practice. Check for duplicates.
- Verify titles, dates, and links against the original publication or official repository.
- Use concise, factual descriptions with consistent capitalization and punctuation.
- Place papers in the appropriate venue and year, and update the displayed paper count.
- Preserve the existing yearly `<details><summary>` groups, with blank lines around the Markdown list inside each group.
- Check tool maintenance and documentation; flag archived or deprecated software for review.
- Preserve human curation. Automated discovery is not sufficient grounds for inclusion.
- For local changes, follow the validation steps below and fix failures before committing or pushing. For browser edits, check the PR's GitHub Actions results and address failures before review is complete.

## Submitting a Pull Request

1. Sign in to GitHub and open [Awesome Fuzzing](https://github.com/cpuu/awesome-fuzzing).
2. Fork the repository and edit `README.md` in your clone, or use GitHub's file editor to propose a change from a fork.
3. Add the resource in the appropriate section and verify its title, link, description, and any paper count affected by the change.
4. Open a pull request explaining why the resource belongs in this list and which original sources you checked.
5. Check the `Lint Awesome List` workflow results and respond to maintainer feedback.

New to pull requests? See GitHub's [guide to creating a pull request from a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

## Local Validation

Use Node.js 24 and pnpm 11.19.0, as specified in `.nvmrc` and `package.json`.

```sh
pnpm install --frozen-lockfile --ignore-scripts
pnpm hooks:install
pnpm lint
git diff --check
```

Run `pnpm test` when changing the validation hooks. See the [maintenance guide](docs/maintenance.md) for hook behavior and CI setup. Passing lint does not replace checking the resource's accuracy, relevance, availability, and maintenance status.

## Updating Your Pull Request

Make requested corrections on the same branch and push them to update the existing pull request. There is no need to open another PR. Re-run local validation after your final edit and check the updated GitHub Actions results.

## Upstream References

This guide adapts the [Awesome contribution guide](https://github.com/sindresorhus/awesome/blob/main/contributing.md) and [list requirements](https://github.com/sindresorhus/awesome/blob/main/pull_request_template.md) for fuzzing resources. Last compared with upstream on 2026-09-14.

Thank you for your suggestions!
