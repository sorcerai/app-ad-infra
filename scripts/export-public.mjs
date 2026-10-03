import { lstatSync, realpathSync, readdirSync, mkdirSync, copyFileSync, readFileSync } from 'node:fs';
import { resolve, dirname, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = resolve(process.argv[2] || resolve(root, '.public-dist'));
const files = JSON.parse(readFileSync(resolve(root, 'scripts/public-assets.json'), 'utf8'));
if (output === root || root.startsWith(output + sep)) throw new Error('Output cannot contain the repository');
const sources = files.map(file => {
  if (file.startsWith('.') || file.split('/').includes('..')) throw new Error('Invalid public path');
  const source = resolve(root, file);
  if (!lstatSync(source).isFile() || lstatSync(source).isSymbolicLink() || !realpathSync(source).startsWith(root + sep)) throw new Error('Public source must be a regular repository file: ' + file);
  return source;
});
const expected = new Set(files);
function inspect(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = resolve(directory, entry.name);
    if (entry.isSymbolicLink()) throw new Error('Output contains a symlink');
    if (entry.isDirectory()) inspect(path);
    else if (!entry.isFile() || !expected.has(relative(output, path).split(sep).join('/'))) throw new Error('Output contains a nonpublic file');
  }
}
try {
  if (!lstatSync(output).isDirectory() || lstatSync(output).isSymbolicLink()) throw new Error('Output must be a regular directory');
  inspect(output);
} catch (error) {
  if (error.code !== 'ENOENT') throw error;
}
mkdirSync(output, { recursive: true });
files.forEach((file, index) => {
  const target = resolve(output, file);
  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(sources[index], target);
});
inspect(output);
console.log('Exported ' + files.length + ' public assets to ' + output);
