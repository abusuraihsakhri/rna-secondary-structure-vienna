const { test } = require('node:test');
const assert = require('node:assert/strict');
const { sanitizeSequence, foldNussinov } = require('../web/app.js');

test('normalizes single-entry FASTA and T to U', () => {
  assert.equal(sanitizeSequence('>rna\n GGG TTT\n CCC\n'), 'GGGUUUCCC');
});

test('rejects invalid nucleotides, multiple FASTA entries, and oversize sequences', () => {
  assert.throws(() => sanitizeSequence('ACGN'), /Only A/);
  assert.throws(() => sanitizeSequence('>first\nAUG\n>second\nAUG'), /one sequence/);
  assert.throws(() => sanitizeSequence('A'.repeat(241)), /at most/);
  assert.throws(() => sanitizeSequence('  '), /Enter/);
});

test('predicts a canonical stem-loop without pseudoknots', () => {
  const p = foldNussinov('GGGAAACCC');
  assert.equal(p.structure, '(((...)))');
  assert.equal(p.pairCount, 3);
  assert.deepEqual(p.pairs, [[1,9],[2,8],[3,7]]);
  assert.equal(p.energyKcalMol, null);
});

test('enforces the minimum hairpin length', () => {
  assert.equal(foldNussinov('GAAAC').structure, '(...)');
  assert.equal(foldNussinov('GAC').structure, '...');
});

test('every pair is canonical and the structure is balanced', () => {
  for (const sequence of ['AUGCUAGC', 'GGGGAAAACCCC', 'AAAAAAA', 'GUGUGUGUGUGU', 'CGAUGCAUACGUC']) {
    const p = foldNussinov(sequence);
    const stack = [];
    for (let i = 0; i < p.length; i++) {
      if (p.structure[i] === '(') stack.push(i);
      if (p.structure[i] === ')') {
        const left = stack.pop();
        assert.notEqual(left, undefined);
        assert.ok(i - left >= 4);
        assert.ok(['AU','UA','GC','CG','GU','UG'].includes(p.sequence[left] + p.sequence[i]));
      }
    }
    assert.equal(stack.length, 0);
    assert.equal(p.structure.length, p.length);
    assert.equal(p.pairCount, (p.structure.match(/\(/g) || []).length);
  }
});