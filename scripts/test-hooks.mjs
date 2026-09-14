import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtempSync, mkdirSync, writeFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {test} from 'node:test';

const hooks = resolve('.githooks');

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'awesome-hooks-'));
  t.after(() => rmSync(root, {recursive: true, force: true}));
  const bin = join(root, 'bin');
  mkdirSync(bin);
  writeFileSync(join(bin, 'pnpm'), '#!/bin/sh\nexit "${LINT_EXIT:-0}"\n', {mode: 0o755});
  const env = {...process.env, PATH: `${bin}:${process.env.PATH}`};
  // Never inherit a caller's Git index or repository into the test repository.
  for (const key of Object.keys(env)) {
    if (key.startsWith('GIT_')) delete env[key];
  }
  const git = (...args) => {
    const result = spawnSync('git', args, {cwd: root, env, encoding: 'utf8'});
    assert.equal(result.status, 0, result.stderr);
    return result.stdout.trim();
  };
  git('init', '-q');
  git('config', 'user.name', 'Hook Test');
  git('config', 'user.email', 'test@example.invalid');
  git('config', 'core.hooksPath', '/dev/null');
  git('config', 'commit.gpgsign', 'false');
  writeFileSync(join(root, 'README.md'), '# Initial\n');
  git('add', 'README.md');
  git('commit', '-qm', 'Initial fixture');
  const head = git('rev-parse', 'HEAD');
  return {
    git,
    edit: text => writeFileSync(join(root, 'README.md'), text),
    pushInput: `refs/heads/test ${head} refs/heads/test ${'0'.repeat(40)}\n`,
    run: (hook, input = '', lintExit = '0') => spawnSync('sh', [join(hooks, hook)], {
      cwd: root, env: {...env, LINT_EXIT: lintExit}, input, encoding: 'utf8',
    }),
  };
}

test('pre-commit propagates lint failures and accepts a valid staged tree', t => {
  const f = fixture(t);
  f.edit('# Staged\n');
  f.git('add', 'README.md');
  assert.equal(f.run('pre-commit').status, 0);
  assert.equal(f.run('pre-commit', '', '7').status, 7);
});

test('pre-commit rejects partial staging and staged whitespace errors', t => {
  const f = fixture(t);
  f.edit('# Staged\n');
  f.git('add', 'README.md');
  f.edit('# Unstaged fix\n');
  assert.match(f.run('pre-commit').stderr, /Stage or stash/);
  f.edit('# Trailing space \n');
  f.git('add', 'README.md');
  assert.notEqual(f.run('pre-commit').status, 0);
});

test('pre-push checks HEAD, rejects dirty content, and propagates lint failure', t => {
  const f = fixture(t);
  assert.equal(f.run('pre-push', f.pushInput).status, 0);
  assert.equal(f.run('pre-push', f.pushInput, '7').status, 7);
  f.edit('# Dirty\n');
  assert.notEqual(f.run('pre-push', f.pushInput).status, 0);
  f.git('add', 'README.md');
  assert.notEqual(f.run('pre-push', f.pushInput).status, 0);
});

test('pre-push rejects another tip and permits deletion without lint', t => {
  const f = fixture(t);
  const other = `refs/heads/other ${'1'.repeat(40)} refs/heads/other ${'0'.repeat(40)}\n`;
  assert.match(f.run('pre-push', other).stderr, /checked-out HEAD/);
  const deletion = `(delete) ${'0'.repeat(40)} refs/heads/old ${'1'.repeat(40)}\n`;
  assert.equal(f.run('pre-push', deletion, '7').status, 0);
});
