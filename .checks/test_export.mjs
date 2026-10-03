import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, copyFileSync, readFileSync, writeFileSync, readdirSync, symlinkSync, renameSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, dirname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const repo = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const assets = JSON.parse(readFileSync(resolve(repo, 'scripts/public-assets.json')));
function fixture() {
  const root = mkdtempSync(resolve(tmpdir(), 'public-export-'));
  for (const file of [...assets, 'scripts/public-assets.json', 'scripts/export-public.mjs']) {
    const target = resolve(root, file);
    mkdirSync(dirname(target), { recursive: true });
    copyFileSync(resolve(repo, file), target);
  }
  return root;
}
function run(root) {
  return spawnSync(process.execPath, [resolve(root, 'scripts/export-public.mjs')], { encoding: 'utf8' });
}
function inventory(root, dir = root) {
  return readdirSync(dir, { withFileTypes: true }).flatMap(e => e.isDirectory() ? inventory(root, resolve(dir, e.name)) : [relative(root, resolve(dir, e.name))]).sort();
}
test('exports only approved public bytes, ignoring dot directories, credentials, config and maps', () => {
  const root = fixture();
  for (const file of ['.checks/private.md', '.github/workflows/private.yml', '.env', 'package.json', 'wrangler.toml', 'index.html.map']) {
    mkdirSync(dirname(resolve(root, file)), { recursive: true });
    writeFileSync(resolve(root, file), 'synthetic private sentinel');
  }
  assert.equal(run(root).status, 0);
  assert.deepEqual(inventory(resolve(root, '.public-dist')), [...assets].sort());
  for (const file of assets) assert.deepEqual(readFileSync(resolve(root, '.public-dist', file)), readFileSync(resolve(root, file)));
  assert.equal(run(root).status, 0, 'a clean repeat export succeeds');
});
test('fails closed for a stale nonpublic output file', () => {
  const root = fixture();
  assert.equal(run(root).status, 0);
  writeFileSync(resolve(root, '.public-dist/private.map'), 'synthetic sentinel');
  assert.notEqual(run(root).status, 0);
});
test('missing and symlinked public sources cannot be deployed', () => {
  for (const link of [false, true]) {
    const root = fixture();
    const file = resolve(root, assets[0]);
    renameSync(file, file + '.backup');
    if (link) symlinkSync(file + '.backup', file);
    assert.notEqual(run(root).status, 0);
    assert.throws(() => readdirSync(resolve(root, '.public-dist')), { code: 'ENOENT' });
  }
});
