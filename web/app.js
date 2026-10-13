'use strict';

const MIN_HAIRPIN_UNPAIRED = 3;
const MAX_BROWSER_LENGTH = 240;
const BASE_PAIRS = new Set(['AU', 'UA', 'CG', 'GC', 'GU', 'UG']);

function sanitizeSequence(raw, maxLength = MAX_BROWSER_LENGTH) {
  if (typeof raw !== 'string') throw new Error('Enter an RNA sequence.');
  const lines = raw.trim().split(/\r?\n/);
  if (lines[0]?.trim().startsWith('>')) lines.shift();
  if (lines.some(line => line.trim().startsWith('>'))) throw new Error('Enter one sequence only, not multiple FASTA entries.');
  const sequence = lines.join('').replace(/\s/g, '').toUpperCase().replace(/T/g, 'U');
  if (!sequence) throw new Error('Enter an RNA sequence.');
  if (/[^ACGU]/.test(sequence)) throw new Error('Only A, C, G, U (or T converted to U) are supported; ambiguous bases are not supported.');
  if (sequence.length > maxLength) throw new Error('Sequence must contain at most ' + maxLength + ' nucleotides.');
  return sequence;
}

function foldNussinov(raw) {
  const sequence = sanitizeSequence(raw);
  const n = sequence.length;
  const dp = Array.from({ length: n }, () => new Int16Array(n));
  const at = (i, j) => (i < 0 || j >= n || i >= j ? 0 : dp[i][j]);
  const canPair = (i, j) => j - i - 1 >= MIN_HAIRPIN_UNPAIRED && BASE_PAIRS.has(sequence[i] + sequence[j]);

  for (let span = 2; span <= n; span++) {
    for (let i = 0; i + span <= n; i++) {
      const j = i + span - 1;
      let best = Math.max(at(i + 1, j), at(i, j - 1));
      if (canPair(i, j)) best = Math.max(best, at(i + 1, j - 1) + 1);
      for (let k = i; k < j; k++) best = Math.max(best, at(i, k) + at(k + 1, j));
      dp[i][j] = best;
    }
  }

  const structure = Array(n).fill('.');
  const pairs = [];
  function traceback(i, j) {
    if (i >= j) return;
    const score = dp[i][j];
    if (canPair(i, j) && score === at(i + 1, j - 1) + 1) {
      structure[i] = '(';
      structure[j] = ')';
      pairs.push([i + 1, j + 1]);
      traceback(i + 1, j - 1);
      return;
    }
    if (score === at(i + 1, j)) { traceback(i + 1, j); return; }
    if (score === at(i, j - 1)) { traceback(i, j - 1); return; }
    for (let k = i; k < j; k++) {
      if (score === at(i, k) + at(k + 1, j)) {
        traceback(i, k);
        traceback(k + 1, j);
        return;
      }
    }
    throw new Error('Could not reconstruct the predicted structure.');
  }
  traceback(0, n - 1);
  pairs.sort((a, b) => a[0] - b[0]);
  return {
    sequence,
    structure: structure.join(''),
    length: n,
    pairs,
    pairCount: pairs.length,
    gcPercent: (sequence.match(/[GC]/g) || []).length * 100 / n,
    algorithm: 'Nussinov maximum-base-pair prediction (not ViennaRNA)',
    energyKcalMol: null
  };
}

function init() {
  const form = document.getElementById('fold-form');
  if (!form) return;
  const input = document.getElementById('sequence');
  const result = document.getElementById('results');
  const error = document.getElementById('error');
  const copy = document.getElementById('copy');
  const download = document.getElementById('download');
  const svg = document.getElementById('arcs');
  let latest = null;
  const setText = (id, value) => { document.getElementById(id).textContent = String(value); };
  const svgNS = 'http://www.w3.org/2000/svg';
  const makeSvg = (tag, attrs) => {
    const element = document.createElementNS(svgNS, tag);
    for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, String(value));
    return element;
  };

  function drawArcs(prediction) {
    svg.replaceChildren();
    const step = 17;
    const width = Math.max(650, (prediction.length + 1) * step);
    svg.setAttribute('viewBox', '0 0 ' + width + ' 210');
    svg.setAttribute('width', String(width));
    svg.setAttribute('height', '210');
    for (const [start, end] of prediction.pairs) {
      const x1 = start * step;
      const x2 = end * step;
      const lift = Math.min(168, 12 + (end - start) * 2.2);
      svg.append(makeSvg('path', {
        d: 'M ' + x1 + ' 172 Q ' + ((x1 + x2) / 2) + ' ' + (172 - lift) + ' ' + x2 + ' 172',
        fill: 'none', stroke: '#63a9fa', 'stroke-width': 1.7, opacity: .85
      }));
    }
    for (let index = 0; index < prediction.length; index++) {
      const x = (index + 1) * step;
      const node = makeSvg('text', { x, y: 195, 'text-anchor': 'middle', fill: '#e4ecf8', 'font-size': '13', 'font-family': 'monospace' });
      node.textContent = prediction.sequence[index];
      svg.append(node);
    }
  }

  function exportText(p) {
    return [
      '# ' + p.algorithm,
      '# Nussinov maximizes AU/GC/GU pairs with >=3 unpaired hairpin nucleotides.',
      '# No minimum free energy is computed. No pseudoknots are modeled.',
      '>prediction', p.sequence, p.structure,
      '# base_pairs=' + p.pairCount + '; length=' + p.length + '; GC=' + p.gcPercent.toFixed(1) + '%', ''
    ].join('\n');
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    try {
      latest = foldNussinov(input.value);
      error.textContent = '';
      error.hidden = true;
      result.hidden = false;
      document.getElementById('empty-note').hidden = true;
      setText('out-sequence', latest.sequence);
      setText('out-structure', latest.structure);
      setText('out-length', latest.length);
      setText('out-pairs', latest.pairCount);
      setText('out-gc', latest.gcPercent.toFixed(1) + '%');
      setText('out-unpaired', latest.length - 2 * latest.pairCount);
      setText('copy-status', '');
      drawArcs(latest);
    } catch (exc) {
      latest = null;
      result.hidden = true;
      document.getElementById('empty-note').hidden = false;
      error.textContent = exc.message;
      error.hidden = false;
    }
  });

  document.getElementById('example').addEventListener('click', () => {
    input.value = 'GGGAAACCC';
    form.requestSubmit();
  });
  copy.addEventListener('click', async () => {
    if (!latest) return;
    try {
      await navigator.clipboard.writeText(exportText(latest));
      setText('copy-status', 'Copied.');
    } catch (_) {
      setText('copy-status', 'Clipboard access blocked. Use the download button.');
    }
  });
  download.addEventListener('click', () => {
    if (!latest) return;
    const url = URL.createObjectURL(new Blob([exportText(latest)], {type: 'text/plain;charset=utf-8'}));
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rna-structure.txt';
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
}

if (typeof document !== 'undefined') document.addEventListener('DOMContentLoaded', init);
if (typeof module !== 'undefined' && module.exports) module.exports = {sanitizeSequence, foldNussinov};
