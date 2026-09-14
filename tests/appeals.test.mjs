import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { openAppeals } from '../src/lib/server/appeals.mjs';

test('separate connections share data; retry and restart preserve one updated record', () => {
  const folder = mkdtempSync(join(tmpdir(), 'welfare-test-'));
  const path = join(folder, 'test.sqlite');
  let first, second, restarted;
  try {
    first = openAppeals(path); second = openAppeals(path);
    first.create({ mainRequest: '需要協助', transcript: [{ role: 'user', text: '測試' }] }, 'test-key');
    first.create({ mainRequest: '重試' }, 'test-key');
    assert.equal(second.list().length, 1);
    assert.equal(second.list()[0].mainRequest, '需要協助');
    assert.equal(second.update('test-key', 'reviewing'), true);
    assert.equal(second.update('missing', 'resolved'), false);
    first.close(); first = null; second.close(); second = null;
    restarted = openAppeals(path);
    assert.equal(restarted.list()[0].status, 'reviewing');
    assert.equal(restarted.list()[0].transcript[0].text, '測試');
  } finally { first?.close(); second?.close(); restarted?.close(); rmSync(folder, { recursive: true }); }
});
